from textual.widgets import Label

class Title(Label):
    DEFAULT_CSS = """
    Title {
        width: 100%;
        background: $secondary;
        content-align: center middle;
        margin-bottom: 1;
    }
    """

    def __init__(self, title: str):
        super().__init__(title)
