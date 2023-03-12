"""I provide all errors that can occur when interacting with the core of pypely."""

from .pipeline import (
    InvalidParameterAnnotationError,
    OutputInputDoNotMatchError,
    ParameterAnnotationsMissingError,
    PipelineStepError,
    ReturnTypeAnnotationMissingError,
)

__all__ = [
    "InvalidParameterAnnotationError",
    "OutputInputDoNotMatchError",
    "ParameterAnnotationsMissingError",
    "PipelineStepError",
    "ReturnTypeAnnotationMissingError",
]
