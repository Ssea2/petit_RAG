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

    def generate(self, prompt: str):
        print("MESSAGE:", prompt)
        self.conversation.append({
            "role": "user",
            "content": prompt
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

