/*
Handles searching/filtering, ordering and pagination of the species cards on the home page.
This script works with 'index.html' inside the hugo/layouts folder.

On load:
1. Species attributes needed for searching fetched from the <template> cards built for each species.
2. Determine if pagination exists (decided by Hugo based on number of species and 'maxSpeciesPerPage' in 'hugo/config.yaml').
3. Run the render function to display the species cards that should be shown.

Once loaded:
- Event listners created for search box, dropdown and pagination (if pagination exists).
- Each event listner calls the main render function (renderSpeciesCards) alongside some others dependant on the event.

Notes:
- This code can handle both pagination and no pagination (i.e. not enough species to warrant it). So can the Playwright tests assocaited with this page.
*/

const SORT_OPTIONS = {
    LAST_UPDATED: 'lastUpdated',
    A_TO_Z: 'alphabet',
    Z_TO_A: 'revAlphabet'
};

const paginationItems = document.querySelectorAll('.pagination .page-item');
const noResultsCard = document.getElementById('no-filtered-card');
const PAGINATION_EXISTS = paginationItems.length > 0; // if not enough species, there will be no pagination yet.
const CARDS_PER_PAGE = parseInt(document.getElementById('card-container').dataset.numbCardsPerPage);

let state = {
    speciesData: [], // updated by reading from the <template>s in the HTML
    currentPage: 1,
    sortOrder: SORT_OPTIONS.LAST_UPDATED,
    searchText: '',
    numbMatches: 0 // updated when search ran.
};


/**
 * Runs on page load.
 * Gets the info needed to search and order the species cards from each <template> card.
 * Runs the render function to display the species cards.
 */
function prepareSpeciesPage() {
    const templates = document.querySelectorAll('template[id^="card-"]');
    templates.forEach(template => {
        const title = template.content.querySelector('.science-name').textContent.toLowerCase();
        const subtitle = template.content.querySelector('.common-name').textContent.toLowerCase();
        const species = {
            id: template.id,
            speciesText: title + ' ' + subtitle, // used for searching
            last_updated: template.content.querySelector('.card-text').textContent.replace('Last updated: ', ''),
        };
        state.speciesData.push(species);
    });
    state.numbMatches = templates.length

    renderSpeciesCards();
}


// Sorting functions below

function stringToDate(str) {
    // Need to use reformat date standard to use JS Date constructor
    const [dd, mm, yyyy] = str.split('/');
    return new Date(yyyy, mm - 1, dd);
}

function sortLastUpdated(a, b) {
    const dateA = stringToDate(a.last_updated);
    const dateB = stringToDate(b.last_updated);
    return dateB - dateA;
}

function sortAlphabetically(a, b) {
    return a.speciesText.localeCompare(b.speciesText);
}

const sortRevAlphabetically = (a, b) => -sortAlphabetically(a, b);


/**
 * Run on page load and every time an event listener is triggered.
 * Based on current state, updates: species cards, pagination buttons and the no results card.
 */
function renderSpeciesCards() {
    const cardContainer = document.getElementById('card-container');
    cardContainer.innerHTML = '';

    const speciesToDisplay = filterAndOrderSpecies();

    if (speciesToDisplay.length === 0) {
        noResultsCard.style.display = 'block';
        state.currentPage = 1
        updatePaginationButtons();
    } else {
        noResultsCard.style.display = 'none';
        speciesToDisplay.forEach((speciesId) => {
            const template = document.getElementById(speciesId);
            const content = template.content.cloneNode(true);
            cardContainer.appendChild(content);
        });
        updatePaginationButtons();
    }
}


/**
 * Search/filter all species and order them according to active dropdown selection
 * The id's of each species <template> is returned (in order of display).
 *
 * @returns {Array} - An array of filtered species HTML <template> ids.
 *                    (Returns empty array if no matches.)
 */
function filterAndOrderSpecies() {
    let filteredSpecies = state.speciesData;

    // filter by text content
    if (state.searchText !== "") {
        filteredSpecies = state.speciesData.filter(species => {
            return species.speciesText.includes(state.searchText);
        });
    }

    state.numbMatches = filteredSpecies.length

    // order species
    if (filteredSpecies.length !== 0) {
        if (state.sortOrder === SORT_OPTIONS.LAST_UPDATED) {
            filteredSpecies.sort(sortLastUpdated);
        } else if (state.sortOrder === SORT_OPTIONS.A_TO_Z) {
            filteredSpecies.sort(sortAlphabetically);
        } else {
            filteredSpecies.sort(sortRevAlphabetically);
        }
    }

    // select results to show based on page number
    if (PAGINATION_EXISTS) {
        const startIndex = (state.currentPage - 1) * CARDS_PER_PAGE;
        const endIndex = startIndex + CARDS_PER_PAGE;
        filteredSpecies = filteredSpecies.slice(startIndex, endIndex);
    }
    return filteredSpecies.map(species => species.id);
}


/**
 * Updates the dropdown view with the selected sorting option.
 * Fills in the dropdown inner HTML using 1 of 3 pre-prepared <templates> items.
 *
 * @param {HTMLElement} target - The dropdown item that was selected.
 */
function updateSortDropdown() {
    const dropdown = document.querySelector(".scilife-sort-dropdown");
    const dropdownButtons = Object.values(SORT_OPTIONS);
    dropdownButtons.forEach(id => document.getElementById(id).classList.remove("active"));

    const activeButton = document.getElementById(state.sortOrder);
    activeButton.classList.add("active");

    const templateId = `text-${state.sortOrder}`;
    const template = document.getElementById(templateId);
    const clone = template.content.cloneNode(true);
    dropdown.innerHTML = '';
    dropdown.appendChild(clone);
}


/**
 * Updates the page number shown as active in the pagination
 */
function updateActivePage() {
    paginationItems.forEach(item => {
        item.classList.remove('active');
    });
    const activePage = document.querySelector(`.pagination .page-link[data-page="${state.currentPage}"]`).parentElement;
    activePage.classList.add('active');
}

/**
 * Update the page number based on on the provided page identifier.
 *
 * @param {string|number} pageSelection - Can be 'prev', 'next', or a specific page number.
 */
function changeCurrentPage(pageSelection) {
    if (pageSelection === 'prev') {
        state.currentPage = Math.max(state.currentPage - 1, 1);
    } else if (pageSelection === 'next') {
        state.currentPage = Math.min(state.currentPage + 1, Math.ceil(state.speciesData.length / CARDS_PER_PAGE));
    } else {
        state.currentPage = parseInt(pageSelection);
    }
    updateActivePage();
}

/**
 * Sets which buttons are enabled/disabled based on the number of pages with results and the current page.
 */
function updatePaginationButtons() {
    const numbActivePages = Math.ceil(state.numbMatches / CARDS_PER_PAGE)

    paginationItems.forEach((item) => {
        const pageLink = item.querySelector('.page-link');
        const page = pageLink.getAttribute('data-page');
        if (page === 'prev') {
            item.classList.toggle('disabled', state.currentPage === 1);
        } else if (page === 'next') {
            item.classList.toggle('disabled', state.currentPage >= numbActivePages);
        } else {
            const pageIndex = parseInt(page);
            item.classList.toggle('disabled', pageIndex > numbActivePages);
        }
    });
}


// On load
prepareSpeciesPage();


// Event: type in search box
// Reset to page 1, filter results and display them
document.querySelector('#Search').addEventListener('input', (event) => {
    state.searchText = event.target.value.toLowerCase();
    if (PAGINATION_EXISTS) {
        state.currentPage = 1;
        changeCurrentPage(1);
    }
    renderSpeciesCards();
});


// Event: Change the ordering of the species via dropdown
// Update the dropdown text with selected item, filter results and display them
document.querySelector('.dropdown-menu').addEventListener('click', (event) => {
    if (event.target.classList.contains('scilife-dropdown-item')) {
        event.preventDefault();
        const sortSelected = event.target.id;
        const sortOrder = Object.keys(SORT_OPTIONS).find(key => SORT_OPTIONS[key] === sortSelected);
        state.sortOrder = SORT_OPTIONS[sortOrder];
        updateSortDropdown();
        renderSpeciesCards();
    }
});


// Event: Change the page
// Change the page, update the cards with species in that slice of the data
if (PAGINATION_EXISTS) {
    document.querySelector('.pagination').addEventListener('click', (event) => {
        if (event.target.classList.contains('page-link')) {
            event.preventDefault();
            const pageSelection = event.target.getAttribute('data-page');
            changeCurrentPage(pageSelection);
            renderSpeciesCards();
        }
    });
}
