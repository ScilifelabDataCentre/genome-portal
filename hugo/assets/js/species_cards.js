/*
Handles searching, ordering and pagination of the species cards

*/
let currentPage = 1;
const cardsPerPage = document.querySelectorAll('.scilife-species-card').length;
const noResultsCard = document.getElementById('no-filtered-card');
const paginationItems = document.querySelectorAll('.pagination .page-item');
const paginationExists = paginationItems.length > 0; // if not enough species, there will be no pagination yet.
let speciesData = []; // updated once JSON data is fetched


/**
 * Fetch the JSON data with all species info, Updates the global speciesData variable
 * Runs once on page load.
 */
function fetchSpeciesData() {
    return fetch('/species_catalog.json')
        .then(response => response.json())
        .then(fetchedData => {
            speciesData = fetchedData;
            return speciesData;
        })
        .catch(error => {
            console.error('Error fetching species data:', error);
            return [];
        });
}


/**
 * Function to populate the species cards with the fetched data.
 *
 * @param {Array} species_data - An array of species data objects.
 */
function populateSpeciesCards(species_data) {
    species_data.forEach((species, index) => {
        const card = document.getElementById(`species-card-${index + 1}`);
        if (card) {
            card.querySelector('a').href = species.rel_permalink;
            card.querySelector('a').title = `Go to the ${species.title} page`;
            card.querySelector('img').src = species.cover_image;
            card.querySelector('img').alt = `Image of ${species.title}`;
            card.querySelector('.science-name').innerHTML = species.title;
            card.querySelector('.common-name').innerHTML = species.subtitle;
            card.querySelector('.card-text').textContent = `Last updated: ${species.last_updated}`;
            card.querySelector('.btn').href = species.rel_permalink;
            card.querySelector('.btn').title = `Go to the ${species.title} page`;

            // Handles attribution text with or without link
            if (species.img_attrib_link) {
                const captionWithLink = card.querySelector('.caption-with-link');
                captionWithLink.href = species.img_attrib_link;
                captionWithLink.querySelector('.scilife-card-image-attrib').textContent = species.img_attrib_text;
                captionWithLink.style.display = 'flex';

                const captionNoLink = card.querySelector('.caption-no-link');
                captionNoLink.style.display = 'none';
            } else {
                const captionNoLink = card.querySelector('.caption-no-link');
                captionNoLink.textContent = species.img_attrib_text;
                captionNoLink.style.display = 'flex';

                const captionWithLink = card.querySelector('.caption-with-link');
                captionWithLink.style.display = 'none';
            }

            card.style.display = 'flex';
        }
    });
}

// Sorting functions below
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

function hideAllCards() {
    const cards = document.querySelectorAll('.scilife-species-card');
    cards.forEach(card => {
        card.style.display = 'none';
    });
}

/**
 * Updates the dropdown view with the selected sorting option.
 *
 * @param {HTMLElement} target - The dropdown item that was selected.
 */
function updateSortDropdown(target) {
    const SORTING_BUTTONS = ["Alphabet", "RevAlphabet", "Updated"];
    const ICON_MAPPING = {
        'Name (A to Z)': 'bi-sort-alpha-down',
        'Name (Z to A)': 'bi-sort-alpha-up',
        'Last updated': 'bi-clock'
    };

    SORTING_BUTTONS.forEach(id => document.getElementById(id).classList.remove("active"));
    target.classList.add("active");

    const dropdown = document.querySelector(".scilife-sort-dropdown");
    const sortOptionSelected = target.textContent.trim();
    const icon = ICON_MAPPING[sortOptionSelected];

    dropdown.textContent = sortOptionSelected;
    dropdown.innerHTML = `<i class="bi ${icon}"></i> ` + sortOptionSelected;
}

/**
 * Updates the page number shown as active in the pagination
 *
 * @param {string|number} page - Can be 'prev', 'next', or a specific page number.
 */
function updateActivePage(page) {
    paginationItems.forEach(item => {
        item.classList.remove('active');
    });

    const activeItem = document.querySelector(`.pagination .page-link[data-page="${page}"]`).parentElement;
    if (activeItem) {
        activeItem.classList.add('active');
    }
}

/**
 * Changes page based on the provided page identifier.
 *
 * @param {string|number} page - Can be 'prev', 'next', or a specific page number.
 */
function changeCurrentPage(page) {
    if (page === 'prev') {
        currentPage = Math.max(currentPage - 1, 1);
    } else if (page === 'next') {
        currentPage = Math.min(currentPage + 1, Math.ceil(speciesData.length / cardsPerPage));
    } else {
        currentPage = parseInt(page);
    }
    updateActivePage(currentPage);
}

/**
 * Sets which buttons are enabled/disabled based on the number of pages with results and the current page.
 *
 * @param {number} numPages - The total number of pages with results/cards.
 */
function updatePaginationButtons(numPages) {
    paginationItems.forEach((item) => {
        const pageLink = item.querySelector('.page-link');
        if (pageLink) {
            const page = pageLink.getAttribute('data-page');
            if (page === 'prev') {
                item.classList.toggle('disabled', currentPage === 1);
            } else if (page === 'next') {
                item.classList.toggle('disabled', currentPage === numPages);
            } else {
                const pageIndex = parseInt(page);
                item.classList.toggle('disabled', pageIndex > numPages);
            }
        }
    });
}

/**
 * Search/filter all species and order them according to dropdown selection
 * speciesData is the global variable containing all species data
 */
function filterAndOrderSpecies() {
    let filteredData = speciesData;

    const searchText = document.querySelector("#Search").value.toLowerCase();
    const revAlphabetSet = document.querySelector("#RevAlphabet").classList.contains("active");
    const lastUpdatedSet = document.querySelector("#Updated").classList.contains("active");
    if (searchText !== "") {
        filteredData = speciesData.filter(species => {
            const title = species.title.toLowerCase();
            const subtitle = species.subtitle.toLowerCase();
            return title.includes(searchText) || subtitle.includes(searchText);
        });
    }

    if (filteredData.length !== 0) {
        if (revAlphabetSet) {
            filteredData.sort(sortRevAlphabetically);
        } else if (lastUpdatedSet) {
            filteredData.sort(sortUpdated);
        } else {
            filteredData.sort(sortAlphabetically);
        }
    }
    return filteredData;
}


/**
 * Displays the filtered species on the cards.
 *
 * @param {Array} filteredData - An array of filtered species data objects.
 */
function displayResults(filteredData) {
    hideAllCards();
    if (filteredData.length === 0) {
        noResultsCard.style.display = 'block';
        updatePaginationButtons(1);
    } else {
        noResultsCard.style.display = 'none';
        const numPages = Math.ceil(filteredData.length / cardsPerPage);
        updatePaginationButtons(numPages);

        const startIndex = (currentPage - 1) * cardsPerPage;
        const endIndex = startIndex + cardsPerPage;
        const paginatedResults = filteredData.slice(startIndex, endIndex);
        populateSpeciesCards(paginatedResults);
    }
}


// On initial load: Fetch the data and populate the species cards
fetchSpeciesData().then(() => {
    const filteredData = filterAndOrderSpecies();
    displayResults(filteredData);
});

// Event listeners below for each type of possible user interaction

// Event: type in search box
// Reset to page 1, filter results and display them
document.querySelector('#Search').addEventListener('input', (event) => {
    if (paginationExists) {
        changeCurrentPage(1);
    }
    const filteredData = filterAndOrderSpecies();
    displayResults(filteredData);
});



// Event: Change the ordering of the species via dropdown
// Update the dropdown text with selected item, filter results and display them
document.querySelector('.dropdown-menu').addEventListener('click', (event) => {
    if (event.target.classList.contains('scilife-dropdown-item')) {
        event.preventDefault();
        updateSortDropdown(event.target);
        const filteredData = filterAndOrderSpecies();
        displayResults(filteredData);
    }
});

// Event: Change the page
// Change the page, update the cards with species in that slice of the data
if (paginationExists) {
    document.querySelector('.pagination').addEventListener('click', (event) => {
        if (event.target.classList.contains('page-link')) {
            event.preventDefault();
            const page = event.target.getAttribute('data-page');
            changeCurrentPage(page);
            const filteredData = filterAndOrderSpecies();
            displayResults(filteredData);
        }
    });
}
