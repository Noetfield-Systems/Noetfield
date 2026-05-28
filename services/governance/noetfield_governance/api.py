"""FastAPI entrypoint for the Noetfield platform foundation."""

from fastapi import FastAPI

from noetfield_events import event_catalog

app = FastAPI(
    title="Noetfield Platform API",
    version="0.3.1",
    description="Executable foundation for governed ambient intelligence.",
)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "noetfield-platform"}


@app.get("/events/catalog", tags=["events"])
async def events_catalog() -> dict[str, dict[str, str]]:
    return event_catalog()
