from pypely.memory._impl import get_memory


def add_to_memory(name, func):
    def __inner(*args):
        result = func(*args)
        memory = get_memory()
        memory.add(name, result)

        return result
    return __inner


def use_memory(func):
    def __inner(*args):
        memory = get_memory()
        return func(*args, memory)
    return __inner