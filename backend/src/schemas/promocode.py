from pydantic import BaseModel


class PromoCreateRequest(BaseModel):
    code: str | None = None
    count_activation: int
    max_count_activators: int
    percent: float


class PromoUpdateRequest(BaseModel):
    id: int
    code: str | None = None
    count_activation: int | None = None
    max_count_activators: int | None = None
    percent: float | None = None


class PromoActivateRequest(BaseModel):
    code: str


class PromoActivateCreate(BaseModel):
    user_id: int
    code: str


class PromoCreate(BaseModel):
    code: str | None = None
    count_activation: int
    max_count_activators: int
    percent: float


class PromoUpdate(BaseModel):
    id: int
    code: str | None = None
    count_activation: int
    max_count_activators: int
    percent: float
