from typing import Any, Dict

class LastFMException(Exception):
    pass

class HTTPException(LastFMException):
    def __init__(self, response: Dict[str, Any]) -> None:
        self.response = response

        self.error: int = response['error']
        self.message: str = response['message']

        super().__init__(self.message)