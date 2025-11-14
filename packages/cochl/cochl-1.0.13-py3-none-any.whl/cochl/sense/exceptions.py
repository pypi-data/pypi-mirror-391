class CochlSenseException(BaseException):
    def __init__(self, message: str):
        super().__init__(message)
        self.message: str = message

    def __str__(self):
        return f'{self.message}\nPlease contact support@cochl.ai'


class TimeoutException(BaseException):
    def __init__(self, session_id: str, timeout: float):
        super().__init__()
        self.session_id = session_id
        self.timeout = timeout

    def __str__(self):
        return f'Prediction (session_id={self.session_id}) has timed out "{self.timeout}s"'
