// Function to fetch the JSON data
function fetchSpeciesData() {
    return fetch('/species_catalog.json')
        .then(response => response.json())
        .catch(error => {
            console.error('Error fetching species data:', error);
            return [];
        });
}

// Function to populate the species cards with the fetched data
function populateSpeciesCards(data) {
    data.forEach((species, index) => {
        if (index < 6) {
            const card = document.getElementById(`species-card-${index + 1}`);
            if (card) {
                card.querySelector('a').href = species.rel_permalink;
                card.querySelector('a').title = `Go to the ${species.title} page`;
                card.querySelector('img').src = species.cover_image;
                card.querySelector('img').alt = `Image of ${species.title}`;
                if (species.img_attrib_link) {
                    card.querySelector('.scilife-card-image-attrib').innerHTML = `<a href="${species.img_attrib_link}" title="Go to the image source" target="_blank">${species.img_attrib_text}</a>`;
                } else {
                    card.querySelector('.scilife-card-image-attrib').textContent = species.img_attrib_text;
                }
                card.querySelector('#science-name').innerHTML = species.title;
                card.querySelector('#common-name').innerHTML = species.subtitle;
                card.querySelector('.card-text').textContent = `Last updated: ${species.last_updated}`;
                card.querySelector('.hidden-date').textContent = species.last_updated;
                card.querySelector('.btn').href = species.rel_permalink;
                card.querySelector('.btn').title = `Go to the ${species.title} page`;
            }
        }
    });
}








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
    });
});




// On initial load...
// Fetch the data and populate the species cards
fetchSpeciesData().then(data => populateSpeciesCards(data));

// Event listners for when page fully loaded or search box input
// document.querySelector("#Search").addEventListener("input", searchAndFilter);
