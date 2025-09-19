import yaml
import json
from fastapi.openapi.utils import get_openapi
from main import app

openapi_schema = get_openapi(
    title=app.title,
    version=app.version,
    description=app.description,
    routes=app.routes,
)

with open("openapi.yaml", "w") as f:
    yaml.dump(openapi_schema, f, sort_keys=False)