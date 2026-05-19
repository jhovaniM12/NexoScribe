from fastapi import FastAPI
from app.core.config import settings
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router

app = FastAPI(
      title=settings.app_name,
      version="0.1.0",
      debug=settings.debug,
  )
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(users_router, prefix=settings.api_v1_prefix)

@app.get(f"{settings.api_v1_prefix}/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
