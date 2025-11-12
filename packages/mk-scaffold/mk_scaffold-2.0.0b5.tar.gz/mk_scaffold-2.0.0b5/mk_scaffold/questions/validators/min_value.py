from prompt_toolkit.validation import ValidationError


def validate(value, schema):
    """
    Return { value to use, stop (True/False) }

    If stop is True, the rest of the validators are skipped.
    """
    vartype = schema.get("type", "integer")
    if vartype != "integer":
        return value, False

    min_value = schema.get("min_value", None)
    if min_value and int(value) < min_value:
        raise ValidationError(message=f"Answer cannot be less than {min_value}") from None
    return value, False
