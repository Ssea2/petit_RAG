import ollama

class slm_manager:

    def __init__(self, config) -> None:
        self.config_ = config["slm_manager"]
        self.model = self.config_["model"]
        self.conversation = [
            {
                "role": "system",
                "content": self.config_["objective"]
            }
        ]
        self.available_models = self._get_available_models()
        self._check_model_availability()

    def _get_available_models(self) -> list[str]:
        return [model.model for model in list(ollama.list())[0][1]]


    def _check_model_availability(self) -> None:
        if not self.model in self.available_models:
            ollama.pull(self.model)
        return None

    def prompt_upgrade(self, prompt: str, documents: list[dict]):
        documents_data = []
        sources = []
        for document in documents:
            documents_data.append(document["chunk"])
            sources.append(document["filename"])
        upgraded_prompt = f"<QUESTION> : {prompt} \n <SOURCES> : {documents_data}"
        return {"prompt": upgraded_prompt, "sources": list((sources))}

    def generate(self, prompt: str, documents: list[dict]):
        message = self.prompt_upgrade(prompt=prompt, documents=documents)
        print("MESSAGE:", message)
        self.conversation.append({
            "role": "user",
            "content": message["prompt"]
        })

        stream = ollama.chat(
            model = self.model,
            messages = self.conversation,
            stream=True,
        )
        anwser = " ".join(chunk["message"]["content"] for chunk in stream)

        self.conversation.append(
            {
            "role": "assistant",
            "content": " ".join(chunk["message"]["content"] for chunk in stream)
            }
        )
        return anwser, message["sources"]

