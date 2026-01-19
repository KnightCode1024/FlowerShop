import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import config
from routers import product_router, category_router, dev_router, user_router
from core.dependencies import init_dependencies


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    container = getattr(app.state, "dishka_container", None)
    if container is not None:
        await container.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


init_dependencies(app)


routers = [
    product_router,
    category_router,
    dev_router,
    user_router,
]

for router in routers:
    app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.app.HOST,
        port=config.app.PORT,
        reload=True,
    )
