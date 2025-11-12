class TesonError(Exception):
    """
    Custom exception class for TEson conversion errors.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"TesonError: {self.message}"
