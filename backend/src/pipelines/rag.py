


def rag_pipeline(prompt: str):
    return "HI"

def documents_pipeline(documents: list, action:str):
    match action:
        case "POST":
            return "1"
        case "DELETE":
            return "2"
        case _:
            return None
