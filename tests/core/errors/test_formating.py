from pypely.core.errors._formating import format_parameter_signature


def test_format_parameter_signature(add):
    to_test = format_parameter_signature(add)

    assert to_test == "(x: <class 'int'>, y: <class 'int'>)"


def test_format_parameter_signature_of_none_annotated_function():
    # Prepare
    def add(x, y):
        return x + y

    expected = "(x, y)"

    # Act
    to_test = format_parameter_signature(add)

    # Compare
    assert to_test == expected
