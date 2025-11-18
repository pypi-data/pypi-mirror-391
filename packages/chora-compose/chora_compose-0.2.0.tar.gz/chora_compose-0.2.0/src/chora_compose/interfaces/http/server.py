"""FastAPI HTTP REST API server for chora-compose."""

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from chora_compose.interfaces.api import Composer

# === FastAPI App ===

app = FastAPI(
    title="chora-compose",
    description="Content generation and orchestration capability server",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# === Global Composer Instance ===

_composer = Composer()

# === Request/Response Models ===


class CreateRequest(BaseModel):
    """Request model for create endpoint."""

    artifact_id: str = Field(..., description="Unique artifact identifier")
    context: dict[str, Any] = Field(
        default_factory=dict, description="Runtime context variables"
    )
    force: bool = Field(False, description="Force regeneration (bypass cache)")


class RefreshRequest(BaseModel):
    """Request model for refresh endpoint."""

    artifact_id: str = Field(..., description="Unique artifact identifier")
    context: dict[str, Any] = Field(
        default_factory=dict, description="Runtime context variables"
    )
    force: bool = Field(False, description="Force regeneration")


class ConfigureRequest(BaseModel):
    """Request model for configure endpoint."""

    item_type: str = Field(..., description="Type: template, collection, or freshness")
    item_id: str = Field(..., description="Unique identifier for the item")
    config: dict[str, Any] = Field(..., description="Configuration data")


class ArtifactResponse(BaseModel):
    """Response model for artifact operations."""

    id: str
    content: str | None = None
    cached: bool | None = None
    refreshed: bool | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class InspectResponse(BaseModel):
    """Response model for inspect operation."""

    id: str
    exists: bool
    metadata: dict[str, Any] | None = None
    freshness: dict[str, Any] | None = None


class DiscoverResponse(BaseModel):
    """Response model for discover operation."""

    templates: list[dict[str, Any]] | None = None
    collections: list[dict[str, Any]] | None = None
    configs: dict[str, Any] | None = None
    count: int


class ConfigureResponse(BaseModel):
    """Response model for configure operation."""

    success: bool
    item_type: str
    item_id: str
    message: str


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: str | None = None


# === API Endpoints ===


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "chora-compose",
        "version": "0.2.0",
        "description": "Content generation and orchestration capability server",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/v1/artifacts", response_model=ArtifactResponse)
async def create_artifact(request: CreateRequest):
    """Create artifact with idempotent caching.

    Generates content from templates with smart caching: fresh artifacts are
    returned from cache, stale artifacts are regenerated.
    """
    try:
        result = await _composer.create(
            artifact_id=request.artifact_id,
            context=request.context,
            force=request.force,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/v1/artifacts/{artifact_id}/refresh", response_model=ArtifactResponse)
async def refresh_artifact(
    artifact_id: str,
    context: dict[str, Any] | None = None,
    force: bool = Query(False, description="Force regeneration"),
):
    """Refresh stale artifacts.

    Selectively regenerates stale artifacts based on freshness policies.
    """
    try:
        result = await _composer.refresh(
            artifact_id=artifact_id,
            context=context or {},
            force=force,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/artifacts/{artifact_id}", response_model=InspectResponse)
async def inspect_artifact(artifact_id: str):
    """Inspect artifact metadata and freshness status."""
    try:
        result = await _composer.inspect(artifact_id=artifact_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/v1/discover", response_model=DiscoverResponse)
async def discover_items(
    item_type: str = Query("all", description="Type: all, templates, collections, configs")
):
    """Discover available templates, collections, and configurations."""
    try:
        result = await _composer.discover(item_type=item_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/configure", response_model=ConfigureResponse)
async def configure_item(request: ConfigureRequest):
    """Configure templates, collections, or freshness policies."""
    try:
        result = await _composer.configure(
            item_type=request.item_type,
            item_id=request.item_id,
            config=request.config,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Convenience endpoints for specific configurations


@app.post("/api/v1/templates/{template_id}")
async def configure_template(
    template_id: str,
    template_path: str,
    description: str | None = None,
    default_context: dict[str, Any] | None = None,
):
    """Configure a template."""
    try:
        result = await _composer.configure_template(
            template_id=template_id,
            template_path=template_path,
            description=description,
            default_context=default_context,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/collections/{collection_id}")
async def configure_collection(
    collection_id: str,
    template_ids: list[str],
    description: str | None = None,
):
    """Configure a collection."""
    try:
        result = await _composer.configure_collection(
            collection_id=collection_id,
            template_ids=template_ids,
            description=description,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/freshness/{policy_id}")
async def configure_freshness(
    policy_id: str,
    max_age_hours: int,
    applies_to: list[str] | None = None,
):
    """Configure a freshness policy."""
    try:
        result = await _composer.configure_freshness(
            policy_id=policy_id,
            max_age_hours=max_age_hours,
            applies_to=applies_to,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
