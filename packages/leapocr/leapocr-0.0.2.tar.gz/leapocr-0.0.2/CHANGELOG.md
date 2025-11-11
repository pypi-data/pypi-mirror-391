# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.2] - 2025-11-11

### Breaking Changes
- **Removed `process_and_wait()` method** - Use two-step pattern: `process_file()`/`process_url()` → `wait_until_done()`
- API now matches Go/JS SDKs for consistency across all language implementations

### Added
- **New OCR Models**:
  - `Model.ENGLISH_PRO_V1` - High-accuracy English document processing (2 credits/page)
  - `Model.PRO_V1` - Premium multilingual document processing (2 credits/page)
- **Custom Model Support** - `ProcessOptions.model` now accepts custom model strings for organization-specific models
- **`wait_until_done()` method** - Explicit job waiting with poll options, matching Go/JS SDK patterns
- New example: `examples/advanced/model_selection.py` demonstrating all models and custom model usage

### Changed
- **Two-step processing pattern** (BREAKING):
  - Old: `result = await client.ocr.process_and_wait("doc.pdf")`
  - New: `job = await client.ocr.process_file("doc.pdf")` → `result = await client.ocr.wait_until_done(job.job_id)`
- Updated all documentation and examples to use two-step pattern
- Modernized type hints: `Optional[X]` → `X | None`, `Union[X, Y]` → `X | Y`
- Enhanced README with model comparison table and custom model examples
- Improved batch processing examples showing submit-all → wait-all pattern

### Fixed
- Type annotation compatibility with Python 3.9+ using `from __future__ import annotations`

### Migration Guide
Users upgrading from v0.0.1 must update code:
```python
# Before (v0.0.1)
result = await client.ocr.process_and_wait(
    "document.pdf",
    options=ProcessOptions(format=Format.STRUCTURED)
)

# After (v0.0.2)
job = await client.ocr.process_file(
    "document.pdf",
    options=ProcessOptions(format=Format.STRUCTURED)
)
result = await client.ocr.wait_until_done(job.job_id)
```

**Benefits of new pattern**:
- Explicit control over job submission vs. waiting
- Better concurrent batch processing
- API parity with Go/JS SDKs
- Flexibility to check status or delete jobs between steps

## [0.0.1] - 2025-11-08

### Added
- Initial release of LeapOCR Python SDK
- Async-first client with httpx
- Support for file and URL processing
- Multiple output formats (Structured, Markdown, Per-Page Structured)
- Custom schema support for structured data extraction
- Built-in retry logic with exponential backoff
- Progress tracking with callbacks
- Comprehensive error handling hierarchy
- Type-safe API with full mypy support
- Direct multipart file uploads
- Concurrent batch processing support
- 93 unit tests and 13 integration tests
- Complete documentation and examples

### Core Features
- `LeapOCR` main client with async context manager
- `OCRService` for document processing operations
- `ProcessOptions` for configurable processing
- `PollOptions` for custom polling behavior
- `ClientConfig` for client configuration

### Error Classes
- `LeapOCRError` - Base error class
- `AuthenticationError` - Authentication failures
- `RateLimitError` - Rate limit exceeded
- `ValidationError` - Input validation errors
- `FileError` - File-related errors
- `JobError` - Job processing errors
- `JobFailedError` - Job processing failures
- `JobTimeoutError` - Job timeout errors
- `NetworkError` - Network connectivity issues
- `APIError` - API error responses
- `InsufficientCreditsError` - Insufficient credits

### Examples
- Basic file processing
- URL processing with manual polling
- Concurrent batch processing
- Schema-based extraction
- Custom configuration
- Error handling strategies
- Timeout handling

[Unreleased]: https://github.com/leapocr/leapocr-python/compare/v0.0.2...HEAD
[0.0.2]: https://github.com/leapocr/leapocr-python/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/leapocr/leapocr-python/releases/tag/v0.0.1
