import time, uuid, logging
from fastapi import FastAPI, Request

logger = logging.getLogger("audit")
logging.basicConfig(level=logging.INFO)

def add_audit(app: FastAPI) -> None:
    @app.middleware("http")
    async def audit_mw(request: Request, call_next):
        rid = str(uuid.uuid4())
        start = time.time()
        response = await call_next(request)
        dur_ms = int((time.time() - start) * 1000)
        logger.info(
            f'RID={rid} path={request.url.path} method={request.method} '
            f'status={response.status_code} dur_ms={dur_ms}'
        )
        response.headers["X-Request-ID"] = rid
        return response
