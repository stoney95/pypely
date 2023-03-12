"""I test all components used by `memorizable`"""

import pytest

from pypely.memory._impl import PipelineMemory
from pypely.memory.errors import InvalidMemoryAttributeError, MemoryAttributeExistsError, MemoryAttributeNotFoundError


def test_PipelineMemory_raises_expected_errors():
    # Prepare
    test_memory = PipelineMemory()
    test_memory.add("test_entry", "test")

    # Act
    with pytest.raises(MemoryAttributeExistsError):
        test_memory.add("test_entry", "something-else")

    with pytest.raises(MemoryAttributeNotFoundError):
        test_memory.get("not-existing-entry")

    with pytest.raises(InvalidMemoryAttributeError):
        test_memory.add_type("test_entry", None)

    with pytest.raises(InvalidMemoryAttributeError):
        test_memory.add_type("test_entry", type(None))
