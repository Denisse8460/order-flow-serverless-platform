from mangum import Mangum

from src.api.app import app


lambda_handler = Mangum(
    app,
    lifespan="off",
)