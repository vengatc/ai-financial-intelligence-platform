"""Main application module for the AI Financial Intelligence Platform."""

from fastapi import FastAPI
from src.config import config
from src.utils import get_timestamp, logger

# Create FastAPI application
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="AI-powered financial intelligence platform for analyzing financial data.",
)


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": f"Welcome to {config.APP_NAME}",
        "version": config.APP_VERSION,
        "timestamp": get_timestamp(),
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": get_timestamp(),
    }


@app.get("/api/v1/analyze")
async def analyze():
    """Placeholder endpoint for financial analysis."""
    return {
        "message": "Financial analysis endpoint",
        "status": "coming_soon",
        "timestamp": get_timestamp(),
    }


def main():
    """Run the application."""
    import uvicorn

    logger.info(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
    logger.info(f"Server running on {config.HOST}:{config.PORT}")

    uvicorn.run(
        "src.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
    )


if __name__ == "__main__":
    main()