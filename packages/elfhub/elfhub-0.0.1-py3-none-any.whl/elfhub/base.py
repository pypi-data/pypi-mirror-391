def greet(name: str = "World") -> str:
    """
    Returns a friendly greeting.
    """
    message = f"Hello, {name}!"
    print(message)
    return message