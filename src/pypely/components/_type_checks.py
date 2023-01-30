# from ._data import Fork, Operation, Pipeline, Merge, Memorizable, Step


# def is_operation(step: Step) -> bool:
#     """I check if a step is an `Operation`.

#     Args:
#         step (Step): The step that will be checked

#     Returns:
#         bool: True if the step is of type `pypely.components.Operation`
#     """
#     return type(step) is Operation


# def is_pipeline(step: Step) -> bool:
#     """I check if a step is a `Pipeline`.

#     Args:
#         step (Step): The step that will be checked

#     Returns:
#         bool: True if the step is of type `pypely.components.Pipeline`
#     """
#     return type(step) is Pipeline


# def is_fork(step: Step) -> bool:
#     """I check if a step is a `Fork`.

#     Args:
#         step (Step): The step that will be checked

#     Returns:
#         bool: True if the step is of type `pypely.components.Fork`
#     """
#     return type(step) is Fork


# def is_merge(step: Step) -> bool:
#     """I check if a step is a `Merge`.

#     Args:
#         step (Step): The step that will be checked

#     Returns:
#         bool: True if the step is of type `pypely.components.Merge`
#     """
#     return type(step) is Merge


# def is_memorizable(step: Step) -> bool:
#     """I check if a step is a `Memorizable`.

#     Args:
#         step (Step): The step that will be checked

#     Returns:
#         bool: True if the step is of type `pypely.components.Memorizable`
#     """
#     return type(step) is Memorizable