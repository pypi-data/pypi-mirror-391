class OpendorsException(Exception):
    def __init__(self, message: str, err_len: int = 0):
        """
        Constructs a custom exception.

        The parameters are used to construct a useful error message that shows the region of the error.
        This is done by adding a second line to the passed message,
        and marking the erratic value at the end of the message string with ^.

        Example:
            Error message: error.
                           ^^^^^

        :param message: The message to set for the exception
        :param err_len: The length of the erratic string at the end of the message that will be marked
        """
        # -1 in padding to de-align linebreak
        super().__init__((message + "\n" + ("^" * err_len).rjust(len(message) - 1)) if err_len > 0 else message)
