const promtArea = document.querySelector(".prompt-input");

promtArea.addEventListener("input", function () {
	this.style.height = "auto";

	const parentHeight = this.parentElement.clientHeight;
	const newHeight = Math.min(parentHeight * 0.5, this.scrollHeight);
	
	this.style.height = `${newHeight}px`;
})

promtArea.addEventListener("keydown", function (event) {
	if (event.key == "Enter" && !event.shiftKey){
		const history = document.querySelector(".history");
		const prompt = this.value.replace(/\n/g, "<br>");
		this.value = "";
		this.style.height = "auto";
		const userhtml = `<p class="user">${prompt}</p>`;
		history.insertAdjacentHTML("beforeend", userhtml);
	}
})
