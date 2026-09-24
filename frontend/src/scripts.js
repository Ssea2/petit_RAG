
const textAreaPrompt = document.querySelector(".prompt-input");
const history = document.querySelector(".history");
const buttonPromptSender = document.querySelector(".button-prompt-sender");


function textAreaHeightUpdate() {
	const maxratio = 0.5;
	this.style.height = "auto";
	const parentHeight = this.parentElement.clientHeight;
	const newHeight = Math.min(maxratio*parentHeight, this.scrollHeight);

	this.style.height = `${newHeight}px`;
}

function add2History(prompt) {
	const htmlMessage = `<p class="message user">${prompt}</p>`;

	history.insertAdjacentHTML("beforeend", htmlMessage);

	textAreaPrompt.value = '';
	textAreaPrompt.style.height = "auto";
}

function checkCommand() {
	const prompt = textAreaPrompt.value.replace(/\n/g, "<br>");
	switch (prompt)	{
		case "/clear":
			history.replaceChildren();
		case "":
			break;
		default:
			add2History(prompt);
	}
}

textAreaPrompt.addEventListener("input", textAreaHeightUpdate);
textAreaPrompt.addEventListener("keydown", function (event) {
	if (event.key == "Enter" && !event.shiftKey){
		event.preventDefault();
		checkCommand();
	}
})

buttonPromptSender.addEventListener("click", checkCommand);
