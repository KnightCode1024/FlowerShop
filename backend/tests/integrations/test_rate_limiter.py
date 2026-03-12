import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from dishka import make_async_container, Provider, Scope, provide
from dishka.integrations.fastapi import setup_dishka, FromDishka

from core.rate_limiter import RateLimiter, Strategy, rate_limit


# Провайдер для тестового RateLimiter
class RateLimiterProvider(Provider):
    def __init__(self, mock_limiter=None):
        super().__init__()
        self.mock_limiter = mock_limiter or AsyncMock(spec=RateLimiter)
    
    @provide(scope=Scope.REQUEST)
    async def get_rate_limiter(self) -> RateLimiter:
        return self.mock_limiter


@pytest.fixture
def mock_rate_limiter():
    limiter = AsyncMock(spec=RateLimiter)
    limiter.is_limited = AsyncMock(return_value=False)
    return limiter


@pytest.fixture
def app_with_ip_rate_limit(mock_rate_limiter):
    app = FastAPI()
    
    # Создаем провайдер с моком
    provider = RateLimiterProvider(mock_rate_limiter)
    container = make_async_container(provider)
    setup_dishka(container, app)
    
    @app.get("/test-ip")
    @rate_limit(strategy=Strategy.IP, policy="5/s;10/m")
    async def test_ip_endpoint(
        request: Request,
        rate_limiter: FromDishka[RateLimiter]  # Используем FromDishka
    ):
        return {"status": "success"}
    
    return app, mock_rate_limiter


@pytest.fixture
def app_with_user_rate_limit(mock_rate_limiter):
    app = FastAPI()
    
    provider = RateLimiterProvider(mock_rate_limiter)
    container = make_async_container(provider)
    setup_dishka(container, app)
    
    @app.get("/test-user")
    @rate_limit(strategy=Strategy.USER, policy="10/m")
    async def test_user_endpoint(
        request: Request,
        rate_limiter: FromDishka[RateLimiter]  # Используем FromDishka
    ):
        return {"status": "success"}
    
    return app, mock_rate_limiter


class TestRateLimitIntegration:
    
    def test_ip_rate_limit_success(self, app_with_ip_rate_limit):
        app, mock_limiter = app_with_ip_rate_limit
        mock_limiter.is_limited.return_value = False
        
        client = TestClient(app)
        response = client.get("/test-ip")
        
        assert response.status_code == 200
        assert response.json() == {"status": "success"}
        
        # Проверяем вызов is_limited
        mock_limiter.is_limited.assert_called_once()
        call_args = mock_limiter.is_limited.call_args[0]
        assert call_args[1] == "/test-ip"
        assert call_args[2] == [(5, 1), (10, 60)]
    
    def test_ip_rate_limit_with_x_forwarded_for(self, app_with_ip_rate_limit):
        app, mock_limiter = app_with_ip_rate_limit
        mock_limiter.is_limited.return_value = False
        
        client = TestClient(app)
        response = client.get(
            "/test-ip",
            headers={"X-Forwarded-For": "203.0.113.1, 10.0.0.1"}
        )
        
        assert response.status_code == 200
        mock_limiter.is_limited.assert_called_once()
    
    def test_ip_rate_limit_too_many_requests(self, app_with_ip_rate_limit):
        app, mock_limiter = app_with_ip_rate_limit
        mock_limiter.is_limited.return_value = True
        
        client = TestClient(app)
        response = client.get("/test-ip")
        
        assert response.status_code == 429
        assert "Too many requests" in response.json()["detail"]
    
    def test_user_rate_limit_with_user_in_state(self, app_with_user_rate_limit):
        app, mock_limiter = app_with_user_rate_limit
        mock_limiter.is_limited.return_value = False
        
        client = TestClient(app)
        
        # Создаем middleware для добавления пользователя в request.state
        @app.middleware("http")
        async def add_user_to_state(request: Request, call_next):
            request.state.user = Mock(id=123)
            response = await call_next(request)
            return response
        
        response = client.get("/test-user")
        assert response.status_code == 200
        mock_limiter.is_limited.assert_called_once()
    
    def test_user_rate_limit_without_user(self, app_with_user_rate_limit):
        app, mock_limiter = app_with_user_rate_limit
        
        client = TestClient(app)
        response = client.get("/test-user")
        
        assert response.status_code == 401
        assert "User not authenticated" in response.json()["detail"]


# Тесты для проверки политик rate limiting
class TestRateLimitPolicies:
    
    @pytest.mark.parametrize("policy,expected_windows", [
        ("5/s", [(5, 1)]),
        ("10/m", [(10, 60)]),
        ("20/h", [(20, 3600)]),
        ("30/d", [(30, 86400)]),
        ("5/s;10/m", [(5, 1), (10, 60)]),
        ("5/s;10/m;20/h", [(5, 1), (10, 60), (20, 3600)]),
    ])
    def test_valid_policies(self, mock_rate_limiter, policy, expected_windows):
        mock_rate_limiter.is_limited.return_value = False
        
        app = FastAPI()
        provider = RateLimiterProvider(mock_rate_limiter)
        container = make_async_container(provider)
        setup_dishka(container, app)
        
        @app.get("/test-policy")
        @rate_limit(strategy=Strategy.IP, policy=policy)
        async def test_endpoint(
            request: Request,
            rate_limiter: FromDishka[RateLimiter]  # Используем FromDishka
        ):
            return {"status": "success"}
        
        client = TestClient(app)
        response = client.get("/test-policy")
        
        assert response.status_code == 200
        
        # Проверяем, что windows сформированы правильно
        mock_rate_limiter.is_limited.assert_called_once()
        call_args = mock_rate_limiter.is_limited.call_args[0]
        assert call_args[2] == expected_windows
    
    @pytest.mark.parametrize("invalid_policy", [
        "invalid",
        "5/x",
        "5/s;10/x",
        "5/s;10/m;20/h;30/d",  # больше 3 сегментов
        "5s",
        "5/",
        "/s",
    ])
    def test_invalid_policies(self, invalid_policy):
        app = FastAPI()
        
        # Проверяем, что декоратор выбрасывает исключение при создании
        with pytest.raises((ValueError, Exception)) as exc_info:
            @app.get("/test-invalid")
            @rate_limit(strategy=Strategy.IP, policy=invalid_policy)
            async def test_endpoint(
                request: Request,
                rate_limiter: RateLimiter  # Здесь не важно, т.к. ошибка в декораторе
            ):
                return {"status": "success"}
        
        # Проверяем, что ошибка связана с невалидной политикой
        error_msg = str(exc_info.value).lower()
        assert any(phrase in error_msg for phrase in [
            "invalid request policy",
            "invalid policy",
            "invalid format",
            "policy"
        ])


# Тесты с реальным Redis (пропускаем, если нет Redis)
@pytest.mark.skip(reason="Requires Redis")
class TestRateLimitRealRedis:
    
    @pytest.fixture
    async def real_rate_limiter(self, redis_client):
        """Создаем реальный RateLimiter с Redis"""
        return RateLimiter(redis_client)
    
    @pytest.fixture
    def app_with_real_limiter(self, real_rate_limiter):
        app = FastAPI()
        
        # Создаем провайдер с реальным rate_limiter
        provider = RateLimiterProvider(real_rate_limiter)
        container = make_async_container(provider)
        setup_dishka(container, app)
        
        @app.get("/real-test")
        @rate_limit(strategy=Strategy.IP, policy="2/s;5/m")
        async def real_test_endpoint(
            request: Request,
            rate_limiter: FromDishka[RateLimiter]
        ):
            return {"status": "success"}
        
        return app
    
    def test_real_rate_limit_multiple_requests(self, app_with_real_limiter):
        client = TestClient(app_with_real_limiter)
        
        # Первые два запроса должны пройти (2/s)
        response1 = client.get("/real-test")
        assert response1.status_code == 200
        
        response2 = client.get("/real-test")
        assert response2.status_code == 200
        
        # Третий запрос должен быть отклонен
        response3 = client.get("/real-test")
        assert response3.status_code == 429


# Тесты для проверки декоратора без rate_limiter
def test_rate_limit_missing_rate_limiter():
    app = FastAPI()
    
    # Не добавляем RateLimiter в DI
    container = make_async_container()
    setup_dishka(container, app)
    
    @app.get("/test-missing")
    @rate_limit(strategy=Strategy.IP, policy="5/s")
    async def test_endpoint(request: Request):
        return {"status": "success"}
    
    client = TestClient(app)
    with pytest.raises(Exception) as exc_info:
        client.get("/test-missing")
    
    assert "Rate limiter not found" in str(exc_info.value)