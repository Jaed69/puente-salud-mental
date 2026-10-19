"""FastAPI application factory."""

from fastapi import FastAPI

from puente.api.messages import router as messages_router
from puente.companion.factory import build_chat_model
from puente.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(title=settings.app_name)
    app.state.settings = settings
    app.state.chat_model = build_chat_model(settings)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(messages_router)
    return app


app = create_app()
