
const speciesCards = Array.from(document.querySelectorAll('.scilife-species-card'));

// helper function to handle missing elements by returning empty string
function getElementText(root, selector) {
    const element = root.querySelector(selector);
    if (!element) {
        console.warn(`Element not found for selector: ${selector} in root: ${root}`);
        return '';
    }
    return element.textContent;
}

function sortAlphabetically(a, b) {
    const titleA = getElementText(a, '#science-name');
    const titleB = getElementText(b, '#science-name');
    return titleA.localeCompare(titleB);
}

const sortRevAlphabetically = (a, b) => -sortAlphabetically(a, b);

// All dates have DD/MM/YYYY format but
// JS Dates object need standard define in stringToDate function
function stringToDate(str) {
    const [dd, mm, yyyy] = str.split('/');
    return new Date(yyyy, mm - 1, dd);
}

function sortUpdated(a, b) {
    const dateStrA = getElementText(a, '.hidden-date');
    const dateStrB = getElementText(b, '.hidden-date');

    const dateA = stringToDate(dateStrA);
    const dateB = stringToDate(dateStrB);
    return dateB - dateA;
}

function searchAndFilter() {
    const searchText = document.querySelector("#Search").value.toLowerCase();
    const AlphabetSet = document.querySelector("#Alphabet").classList.contains("active");
    const RevAlphabetSet = document.querySelector("#RevAlphabet").classList.contains("active");
    const UpdatedSet = document.querySelector("#Updated").classList.contains("active");

    document.querySelector("#card-container").innerHTML = "";
    let cardsToAppend = [];

    if (searchText === "") {
        cardsToAppend = speciesCards.slice();
    } else {
        cardsToAppend = speciesCards.filter(function (card) {
            const title = getElementText(card, '#science-name').toLowerCase();
            const subtitle = getElementText(card, '#common-name').toLowerCase();
            const cardText = getElementText(card, '.card-text').toLowerCase();
            return title.includes(searchText) || subtitle.includes(searchText) || cardText.includes(searchText);
        });
    }

    if (cardsToAppend.length === 0) {
        document.querySelector("#no-filtered-card").style.display = 'block';
    } else {
        document.querySelector("#no-filtered-card").style.display = 'none';

        if (RevAlphabetSet) {
            cardsToAppend.sort(sortRevAlphabetically);
        }
        else if (UpdatedSet) {
            cardsToAppend.sort(sortUpdated);
        }
        else {
            cardsToAppend.sort(sortAlphabetically)
        }

        cardsToAppend.forEach(function (card) {
            document.querySelector("#card-container").appendChild(card.parentElement);
        });
    }
}

// Event listeners for sorting buttons and then search box
const sortingButtons = ["Alphabet", "RevAlphabet", "Updated"];
sortingButtons.forEach(buttonId => {
    document.getElementById(buttonId).addEventListener("click", function () {
        sortingButtons.forEach(id => document.getElementById(id).classList.remove("active"));
        this.classList.add("active");

        // (Update the dropdown text with selected item)
        const dropdown = document.querySelector(".scilife-sort-dropdown");
        const sortOptionSelected = this.textContent.trim();
        const iconMapping = {
            'Name (A to Z)': 'bi-sort-alpha-down',
            'Name (Z to A)': 'bi-sort-alpha-up',
            'Last updated': 'bi-clock'
        };
        const icon = iconMapping[sortOptionSelected];

        dropdown.textContent = sortOptionSelected;
        dropdown.innerHTML = `<i class="bi ${icon}"></i> ` + sortOptionSelected;

        searchAndFilter();
    });
});

// Event listners for when page fully loaded or search box input
document.addEventListener("DOMContentLoaded", searchAndFilter);
document.querySelector("#Search").addEventListener("input", searchAndFilter);
