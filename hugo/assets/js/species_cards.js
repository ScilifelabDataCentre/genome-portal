/*
Docstring TODO
*/
let speciesData = [];
let currentPage = 1;
let NUM_CARDS = 0; // updated once JSON data is fetched
const CARDS_PER_PAGE = document.querySelectorAll('.scilife-species-card').length;

// Function to fetch the JSON data
function fetchSpeciesData() {
    return fetch('/species_catalog.json')
        .then(response => response.json())
        .then(fetchedData => {
            speciesData = fetchedData;
            NUM_CARDS = speciesData.length;
            return speciesData; // Return the global speciesData variable
        })
        .catch(error => {
            console.error('Error fetching species data:', error);
            return [];
        });
}


// Sort alphabetically
function sortAlphabetically(a, b) {
    return a.title.localeCompare(b.title);
}

const sortRevAlphabetically = (a, b) => -sortAlphabetically(a, b);

// All dates have DD/MM/YYYY format but
// JS Dates object need standard define in stringToDate function
function stringToDate(str) {
    const [dd, mm, yyyy] = str.split('/');
    return new Date(yyyy, mm - 1, dd);
}

function sortUpdated(a, b) {
    const dateA = stringToDate(a.last_updated);
    const dateB = stringToDate(b.last_updated);
    return dateB - dateA;
}

function searchAndFilter() {
    const searchText = document.querySelector("#Search").value.toLowerCase();
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

    if (filteredData.length !== 0) {
        if (RevAlphabetSet) {
            filteredData.sort(sortRevAlphabetically);
        } else if (UpdatedSet) {
            filteredData.sort(sortUpdated);
        } else {
            filteredData.sort(sortAlphabetically);
        }
    }
    return filteredData;
}


// Function to hide all cards
function hideAllCards() {
    const cards = document.querySelectorAll('.scilife-species-card');
    cards.forEach(card => {
        card.style.display = 'none';
    });
}

// Function to populate the species cards with the fetched data
function populateSpeciesCards(data) {

    // Hide all cards initially
    hideAllCards();

    // Add back the cards that match the search up to the page limit
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
            card.querySelector('.btn').href = species.rel_permalink;
            card.querySelector('.btn').title = `Go to the ${species.title} page`;
            card.style.display = 'block'; // Ensure the card is visible
        }
    });

}

// Updates the page number shown as active in the pagination
function updateActivePage(page) {
    document.querySelectorAll('.pagination .page-item').forEach(item => {
        item.classList.remove('active');
    });

    const activeItem = document.querySelector(`.pagination .page-link[data-page="${page}"]`).parentElement;
    if (activeItem) {
        activeItem.classList.add('active');
    }
}

// Function to handle pagination
function handlePagination(page) {
    if (page === 'prev') {
        currentPage = Math.max(currentPage - 1, 1);
    } else if (page === 'next') {
        currentPage = Math.min(currentPage + 1, Math.ceil(speciesData.length / CARDS_PER_PAGE));
    } else {
        currentPage = parseInt(page);
    }
    updateActivePage(currentPage);
}

function updatePaginationButtons(numPages) {
    const paginationItems = document.querySelectorAll('.pagination .page-item');
    paginationItems.forEach((item, index) => {
        const pageLink = item.querySelector('.page-link');
        if (pageLink) {
            const page = pageLink.getAttribute('data-page');
            if (page === 'prev') {
                if (currentPage === 1) {
                    item.classList.add('disabled');
                } else {
                    item.classList.remove('disabled');
                }
            } else if (page === 'next') {
                if (currentPage === numPages) {
                    item.classList.add('disabled');
                } else {
                    item.classList.remove('disabled');
                }
            } else {
                const pageIndex = parseInt(page);
                if (pageIndex > numPages) {
                    item.classList.add('disabled');
                } else {
                    item.classList.remove('disabled');
                }
            }
        }
    });
}



function displayResults(filteredData) {
    if (filteredData.length === 0) {
        document.querySelector("#no-filtered-card").style.display = 'block';
        hideAllCards();
        updatePaginationButtons(1);
    } else {
        document.querySelector("#no-filtered-card").style.display = 'none';

        // Calculate the number of pages based on the filtered data
        const numPages = Math.ceil(filteredData.length / CARDS_PER_PAGE);
        updatePaginationButtons(numPages);

        // Calculate the start and end indices based on the current page
        const startIndex = (currentPage - 1) * CARDS_PER_PAGE;
        const endIndex = startIndex + CARDS_PER_PAGE;

        // Get the subset of results for the current page and populate the species cards
        const paginatedResults = filteredData.slice(startIndex, endIndex);
        populateSpeciesCards(paginatedResults);
    }
}



function handlePaginationEvent(event) {
    event.preventDefault();
    const target = event.target;
    const page = target.getAttribute('data-page');
    handlePagination(page);
    const filteredData = searchAndFilter();
    displayResults(filteredData);
}

function handleSortingEvent(event) {
    event.preventDefault();
    const target = event.target;
    const sortingButtons = ["Alphabet", "RevAlphabet", "Updated"];
    sortingButtons.forEach(id => document.getElementById(id).classList.remove("active"));
    target.classList.add("active");

    // (Update the dropdown text with selected item)
    const dropdown = document.querySelector(".scilife-sort-dropdown");
    const sortOptionSelected = target.textContent.trim();
    const iconMapping = {
        'Name (A to Z)': 'bi-sort-alpha-down',
        'Name (Z to A)': 'bi-sort-alpha-up',
        'Last updated': 'bi-clock'
    };
    const icon = iconMapping[sortOptionSelected];

    dropdown.textContent = sortOptionSelected;
    dropdown.innerHTML = `<i class="bi ${icon}"></i> ` + sortOptionSelected;

    currentPage = 1; // Reset to page 1 when a sort event occurs
    const filteredData = searchAndFilter();
    displayResults(filteredData);
}

function handleSearchEvent(event) {
    currentPage = 1; // Reset to page 1 when a search input event occurs
    handlePagination(currentPage); // Update the active page
    const filteredData = searchAndFilter();
    displayResults(filteredData);
}



// On initial load...
// Fetch the data and populate the species cards
fetchSpeciesData().then(speciesData => {
    const filteredData = searchAndFilter();
    displayResults(filteredData);
});




// Attach event listeners to pagination buttons, sorting buttons, and search input
document.querySelectorAll('.page-link').forEach(element => {
    element.addEventListener('click', handlePaginationEvent);
});
document.querySelectorAll('.scilife-dropdown-item').forEach(element => {
    element.addEventListener('click', handleSortingEvent);
});
document.querySelector('#Search').addEventListener('input', handleSearchEvent);
