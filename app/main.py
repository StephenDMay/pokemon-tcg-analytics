from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import cards, decks
from app.core.config import settings
import logging

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION
    )

    # Configure CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    application.include_router(cards.router, prefix="/api/cards", tags=["cards"])
    application.include_router(decks.router, prefix="/api/decks", tags=["decks"])

    
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return application

app = create_application()