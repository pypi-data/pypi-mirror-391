import importlib.resources

def greet(name):
    return f"Hello, {name}! 👋 Welcome to nltk_com_fsd."

def read_textfile():
    """Reads info.txt inside the package."""
    with importlib.resources.open_text("nltk_com_fsd", "info.txt") as f:
        return f.read()
