import getpass

def greet(name: str | None = None) -> str:
    """Return a greeting string with the given or current username."""
    if not name:
        name = getpass.getuser()  # Automatically fetches the system username
    return f"Hello, {name} — from bhavani!"
