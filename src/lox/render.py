def render(value: object) -> str:
    if value is None:
        return "nil"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, float):
        return str(value).removesuffix(".0")
    return str(value)
