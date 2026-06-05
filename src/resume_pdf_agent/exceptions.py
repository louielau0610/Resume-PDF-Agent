"""Custom exceptions for resume_pdf_agent."""


class ResumeAgentError(Exception):
    """Base exception for resume_pdf_agent errors."""


class ValidationError(ResumeAgentError):
    """Raised when resume input validation fails."""


class RenderingError(ResumeAgentError):
    """Raised when rendering fails."""


class UnsupportedExportFormatError(ResumeAgentError):
    """Raised when an unsupported export format is requested."""
