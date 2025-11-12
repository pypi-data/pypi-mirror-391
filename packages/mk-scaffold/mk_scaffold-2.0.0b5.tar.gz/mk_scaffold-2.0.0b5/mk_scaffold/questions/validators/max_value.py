from prompt_toolkit.validation import ValidationError


def validate(value, schema):
    """
    Return { value to use, stop (True/False) }

    If stop is True, the rest of the validators are skipped.
    """
    vartype = schema.get("type", "integer")
    if vartype != "integer":
        return value, False

    max_value = schema.get("max_value", None)
    if max_value and int(value) > max_value:
        raise ValidationError(message=f"Answer cannot be more than {max_value}") from None
    return value, False
