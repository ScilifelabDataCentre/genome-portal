// Adapted from https://logfetch.com/hugo-add-copy-to-clipboard-button/
// Adds functionality to copy-to-clipboard buttonswhich sit above each code/citation block.

// on click swap the copy button with the copied button for a few seconds
const handleButtonClick = (copyButton, copiedButton, codeBlock, clipboard) => {
    clipboard.writeText(codeBlock.innerText).then(
        () => {
            copyButton.style.display = 'none';
            copiedButton.style.display = 'inline-block';
            setTimeout(() => {
                copyButton.style.display = 'inline-block';
                copiedButton.style.display = 'none';
            }, 2000);
        },
        (error) => {
            console.error("Clipboard write failed", error);
            copyButton.innerText = "Error";
        }
    );
};

// create the copy to clipboard button above the code/citation block
const createClipboard = (codeBlock, clipboard) => {
    const copyButton = container.querySelector('#copy-button');
    const copiedButton = container.querySelector('#copied-button');
    copyButton.addEventListener('click', () => handleButtonClick(copyButton, copiedButton, codeBlock, clipboard));
    return container;
};

// attach event listeners to the existing clipboard buttons
const attachClipboardListeners = (clipboard) => {
    document.querySelectorAll(".clipboard").forEach((clipboardContainer) => {
        const copyButton = clipboardContainer.querySelector('#copy-button');
        const copiedButton = clipboardContainer.querySelector('#copied-button');
        const codeBlock = clipboardContainer.nextElementSibling.querySelector('code');

        copyButton.addEventListener('click', () => handleButtonClick(copyButton, copiedButton, codeBlock, clipboard));
    });
};

document.addEventListener("DOMContentLoaded", () => {
    attachClipboardListeners(navigator.clipboard);
});
