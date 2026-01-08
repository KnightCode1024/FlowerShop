import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import config
from routers import product_router, category_router, dev_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


routers = [
    product_router,
    category_router,
    dev_router,
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
