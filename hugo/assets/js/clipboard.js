// Adapted from https://logfetch.com/hugo-add-copy-to-clipboard-button/
const addCopyButtons = (clipboard) => {
    document.querySelectorAll("pre > code").forEach((codeBlock) => {
        // Create a button that can copy to clipboard
        const button = document.createElement("button");
        button.className = "copy-clipboard-button";
        button.type = "button";
        button.innerText = "Copy";
        button.addEventListener("click", () => {
            clipboard.writeText(codeBlock.innerText).then(
                () => {
                    button.blur();
                    button.innerText = "Copied";
                    setTimeout(() => (button.innerText = "Copy"), 2000);
                },
                (error) => {
                    console.error("Clipboard write failed", error);
                    button.innerText = "Error";
                }
            );
        });

        // Wrap the copy button in a div so easier to style
        const clipboardDiv = document.createElement("div");
        clipboardDiv.className = "copy-button";
        clipboardDiv.appendChild(button);
        const preElement = codeBlock.parentNode;
        preElement.parentNode.insertBefore(clipboardDiv, preElement);
    });
};

document.addEventListener("DOMContentLoaded", () => {
    addCopyButtons(navigator.clipboard);
});
