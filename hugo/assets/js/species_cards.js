const NUM_CARDS = 6;
let speciesData = [];

// Function to fetch the JSON data
function fetchSpeciesData() {
    return fetch('/species_catalog.json')
        .then(response => response.json())
        .then(data => {
            speciesData = data;
            return data;
        })
        .catch(error => {
            console.error('Error fetching species data:', error);
            return [];
        });
}

// hide the cards that are not populated
function hideRemainingCards(startIndex) {
    for (let i = startIndex; i < NUM_CARDS; i++) {
        const card = document.getElementById(`species-card-${i + 1}`);
        if (card) {
            card.style.display = 'none';
        }
    }
}



// Function to populate the species cards with the fetched data
function populateSpeciesCards(data) {
    data.forEach((species, index) => {
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
            card.querySelector('.science-name').innerHTML = species.title;
            card.querySelector('.common-name').innerHTML = species.subtitle;
            card.querySelector('.card-text').textContent = `Last updated: ${species.last_updated}`;
            card.querySelector('.hidden-date').textContent = species.last_updated;
            card.querySelector('.btn').href = species.rel_permalink;
            card.querySelector('.btn').title = `Go to the ${species.title} page`;
            card.style.display = 'block'; // Ensure the card is visible
        }
    });
}

// Sort alphabetically
function sortAlphabetically(a, b) {
    return a.title.localeCompare(b.title);
}

const sortRevAlphabetically = (a, b) => -sortAlphabetically(a, b);

// Sort by last updated
function sortUpdated(a, b) {
    const dateA = new Date(a.last_updated);
    const dateB = new Date(b.last_updated);
    return dateB - dateA;
}

function searchAndFilter() {
    const searchText = document.querySelector("#Search").value.toLowerCase();
    const AlphabetSet = document.querySelector("#Alphabet").classList.contains("active");
    const RevAlphabetSet = document.querySelector("#RevAlphabet").classList.contains("active");
    const UpdatedSet = document.querySelector("#Updated").classList.contains("active");

    let filteredData = speciesData;

    if (searchText !== "") {
        filteredData = speciesData.filter(species => {
            const title = species.title.toLowerCase();
            const subtitle = species.subtitle.toLowerCase();
            const cardText = species.last_updated.toLowerCase();
            return title.includes(searchText) || subtitle.includes(searchText) || cardText.includes(searchText);
        });
    }

    if (filteredData.length === 0) {
        document.querySelector("#no-filtered-card").style.display = 'block';
    } else {
        document.querySelector("#no-filtered-card").style.display = 'none';

        if (RevAlphabetSet) {
            filteredData.sort(sortRevAlphabetically);
        } else if (UpdatedSet) {
            filteredData.sort(sortUpdated);
        } else {
            filteredData.sort(sortAlphabetically);
        }

        // Get the first set of results and populate the species cards
        const topResults = filteredData.slice(0, NUM_CARDS);
        populateSpeciesCards(topResults);
    }
}

// On initial load...
// Fetch the data and populate the species cards then filter according to defaults.
fetchSpeciesData().then(data => {
    populateSpeciesCards(data);
    searchAndFilter();
});

// Event listeners for click on sorting buttons
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
        // TODO - do I need to add hideRemainingCards(0) here? when pagination in place?
        searchAndFilter(); // Re-filter and sort on button click
    });
});

// Event listeners for search box input
document.querySelector("#Search").addEventListener("input", function() {
    hideRemainingCards(0);
    searchAndFilter();
});
