import uvicorn

from run import make_app

uvicorn.run(make_app(), port=8001)