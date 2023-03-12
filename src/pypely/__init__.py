"""I am pypely.

Welcome to the py pipeline abstraction language.
"""

from .core.functions import fork, identity, merge, pipeline, to

__all__ = ["pipeline", "identity", "merge", "fork", "to"]
