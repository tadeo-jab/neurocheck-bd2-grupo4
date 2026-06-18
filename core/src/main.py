"""NeuroCheck — dual-database clinical/learning platform."""

import uvicorn
from src.config import settings


def main():
    uvicorn.run(
        "src.app:create_app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        factory=True,
    )


if __name__ == "__main__":
    main()
