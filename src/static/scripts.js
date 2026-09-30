
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


async function get_rag_anwser(userPrompt) {
	const response = await fetch('/language_model/question',{
		method: "POST",
		headers: {
        "Content-Type": "application/json"
		},
		body: JSON.stringify({prompt: userPrompt})
	})
	const results = await response.json();
	console.log(results);
}


function add2History(userPrompt) {
	const htmlMessage = `<p class="message user">${userPrompt.replace(/\n/g, "<br>")}</p>`;

	history.insertAdjacentHTML("beforeend", htmlMessage);

	textAreaPrompt.value = '';
	textAreaPrompt.style.height = "auto";
	console.log("ha");
	get_rag_anwser(userPrompt);
	console.log("response");
}

function checkCommand() {
	const userPrompt = textAreaPrompt.value;
	switch (userPrompt)	{
		case "/clear":
			history.replaceChildren();
			textAreaPrompt.value = "";
			break;
		case "":
			break;
		default:
			add2History(userPrompt);
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

// file selector
const filesSelector = document.querySelector(".files-selector");
const buttonAddDocuments = document.querySelector(".button-add-documents");

async function fileSelectionSend() {
	await new Promise((resolve) => {
		filesSelector.onchange = () => resolve();
		filesSelector.click();
		});

	const files = filesSelector.files;
	if (files.length === 0) return;

	const files2send = new FormData();
	Array.from(files).forEach(file => {
		files2send.append("files", file, file.name)
	})

	try {
    const response = await fetch('/database/documents', {
      method: 'POST',
      body: files2send // Le navigateur gère le Content-Type tout seul
    });

    const result = await response.json();
    console.log('Upload réussi :', result);
	} catch (error) {
    console.error("Erreur lors de l'envoi :", error);
	}
}

buttonAddDocuments.addEventListener("click", fileSelectionSend);


// RAG 

