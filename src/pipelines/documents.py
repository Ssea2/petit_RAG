import logging

logger = logging.getLogger(__name__)


class DocumentManager:

    def __init__(self) -> None:
        pass

    def stack(self, documents: list, action:str):
        match action:
            case "POST":
                return "1"
            case "DELETE":
                return "2"
            case _:
                return None
