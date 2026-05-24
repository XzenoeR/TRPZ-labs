from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from spaceship.config import Settings
from spaceship.routers import api, health

import numpy as np
from fastapi import APIRouter

router = APIRouter()

@router.get("/matrices")
def get_matrices():
    matrix_a = np.random.rand(10, 10).tolist()
    matrix_b = np.random.rand(10, 10).tolist()
    product = np.dot(matrix_a, matrix_b).tolist()
    
    return {
        "matrix_a": matrix_a,
        "matrix_b": matrix_b,
        "product": product
    }

# aboba 2
#aboba
def make_app(settings: Settings) -> FastAPI:
    print("aboba Bogdan IM-42")
    app = FastAPI(
        debug=settings.debug,
        title=settings.app_title,
        description=settings.app_description,
        version=settings.app_version,
    )
    app.state.settings = settings

    if settings.debug:
        app.mount('/static', StaticFiles(directory='build'), name='static')

    app.include_router(api.router, prefix='/api', tags=['api'])
    app.include_router(health.router, prefix='/health', tags=['health'])

    @app.get('/', include_in_schema=False, response_class=FileResponse)
    async def root() -> str:
        return 'build/index.html'

    return app
