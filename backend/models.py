"""
Data models for the Website Generator application.

This module contains Pydantic models for API requests/responses
and database record representations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, HttpUrl, Field


class WebsiteRequest(BaseModel):
    """Request model for website generation."""
    url: HttpUrl = Field(..., description="The URL to scrape and optimize")


class WebsiteResponse(BaseModel):
    """Response model for website data."""
    id: UUID
    identifier: str
    original_url: str
    created_at: datetime
    status: str = "completed"
    template_name: Optional[str] = None


class JobRequest(BaseModel):
    """Request model for job creation."""
    url: HttpUrl = Field(..., description="The URL to process")


class JobResponse(BaseModel):
    """Response model for job status."""
    id: UUID
    website_id: Optional[UUID] = None
    status: str = Field(..., description="Job status: pending, processing, completed, failed")
    error_message: Optional[str] = None
    created_at: datetime
    identifier: Optional[str] = None


class JobStatus(BaseModel):
    """Model for job status updates."""
    status: str = Field(..., description="Job status: pending, processing, completed, failed")
    error_message: Optional[str] = None
    website_id: Optional[UUID] = None
    identifier: Optional[str] = None


class WebsiteRecord(BaseModel):
    """Database record model for websites."""
    id: UUID
    identifier: str
    original_url: str
    original_html: Optional[str] = None
    generated_html: Optional[str] = None
    template_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobRecord(BaseModel):
    """Database record model for jobs."""
    id: UUID
    website_id: Optional[UUID] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = "healthy"
    timestamp: datetime
    database: str = "connected"
    version: str = "1.0.0"
