"""Data models and enums for LeapOCR SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable


class Format(str, Enum):
    """Output format types for OCR processing."""

    MARKDOWN = "markdown"
    STRUCTURED = "structured"
    PER_PAGE_STRUCTURED = "per_page_structured"


class Model(str, Enum):
    """OCR model types.

    Predefined models available in LeapOCR. You can also use custom model strings
    by passing them directly to the model parameter in ProcessOptions.
    """

    STANDARD_V1 = "standard-v1"
    ENGLISH_PRO_V1 = "english-pro-v1"
    PRO_V1 = "pro-v1"


class JobStatusType(str, Enum):
    """Job processing status types."""

    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PARTIALLY_DONE = "partially_done"
    FAILED = "failed"


@dataclass
class ProcessOptions:
    """Options for OCR processing.

    Args:
        format: Output format (structured, markdown, or per-page structured)
        model: OCR model to use (Model enum or custom string)
        schema: JSON schema for structured extraction
        instructions: Natural language instructions for extraction
        template_slug: Slug of pre-configured template to use
        metadata: Additional metadata to attach to the job
    """

    format: Format = Format.STRUCTURED
    model: Model | str | None = None
    schema: dict[str, Any] | None = None
    instructions: str | None = None
    template_slug: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class PollOptions:
    """Options for polling job status."""

    poll_interval: float = 2.0  # seconds
    max_wait: float = 300.0  # seconds (5 minutes)
    on_progress: Callable[[JobStatus], None] | None = None


@dataclass
class ClientConfig:
    """Configuration for LeapOCR client."""

    base_url: str = "https://api.leapocr.com/api/v1"
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_multiplier: float = 2.0
    debug: bool = False


@dataclass
class ProcessResult:
    """Result from initiating OCR processing."""

    job_id: str
    status: JobStatusType
    created_at: datetime
    estimated_completion: datetime | None = None


@dataclass
class JobStatus:
    """Job status information."""

    job_id: str
    status: JobStatusType
    processed_pages: int
    total_pages: int
    progress: float  # 0-100
    created_at: datetime
    updated_at: datetime
    error_message: str | None = None


@dataclass
class PageMetadata:
    """Metadata for a single page."""

    processing_ms: int | None = None
    retry_count: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class PageResult:
    """Result for a single page."""

    page_number: int
    text: str
    metadata: PageMetadata
    processed_at: datetime
    id: str | None = None


@dataclass
class PaginationInfo:
    """Pagination information for results."""

    page: int
    limit: int
    total: int
    total_pages: int


@dataclass
class JobResult:
    """Complete job results."""

    job_id: str
    status: JobStatusType
    pages: list[PageResult]
    file_name: str
    total_pages: int
    processed_pages: int
    processing_time_seconds: float
    credits_used: int
    model: str
    result_format: str
    completed_at: datetime
    pagination: PaginationInfo | None = None


@dataclass
class ModelInfo:
    """OCR model information."""

    name: str
    display_name: str
    description: str
    credits_per_page: int
    priority: int


@dataclass
class BatchResult:
    """Result from batch processing."""

    batch_id: str
    jobs: list[ProcessResult]
    total_files: int
    submitted_at: datetime
