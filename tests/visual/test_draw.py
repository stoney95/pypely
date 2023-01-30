# import pytest
# import tempfile

# from pypely import pipeline, fork, merge
# from pypely.memory import memorizable
# from pypely.visual import draw

# from pathlib import Path

# HERE = Path(__file__).parent.resolve()

# @pytest.mark.skip("Draw is currently not working as it relies on the not working implementation of `pypely.components.decompose`")
# def test_draw(add):
#     _add = memorizable(add)

#     def multiply_by(x):
#         @memorizable
#         def _multiply_by(y):
#             return x * y
        
#         return _multiply_by

#     inner_pipeline = pipeline(
#         fork(
#             add,
#             add
#         ),
#         multiply_by(4)
#     )

#     test = pipeline(
#         _add >> "test",
#         multiply_by(5),
#         inner_pipeline << "test",
#         multiply_by(1) >> "inner",
#         fork(
#             multiply_by(2),
#             _add << "inner",
#         ),
#         merge(add),
#         _add << "test"
#     )

#     with tempfile.TemporaryDirectory() as tmp:
#         test_path = Path(tmp) / "test.html"
#         draw(test, path=test_path)

#         with open(test_path, 'r') as f:
#             to_test = f.read()

#         with open(HERE / "expected.html", 'r') as f:
#             expected = f.read()

#         to_test = _replace_multiple_spaces(to_test)
#         expected = _replace_multiple_spaces(expected)
#         assert to_test == expected


# def _replace_multiple_spaces(text: str) -> str:
#     """I replace multiple spaces in a string with one space.

#     Args:
#         text (str): String input with multiple spaces

#     Returns:
#         str: String with only one space between words
#     """

#     return " ".join(text.split())
