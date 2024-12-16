/*
Handles searching/filtering, ordering and pagination of the species cards on the home page.
This script works with 'index.html' inside the hugo/layouts folder.

On load:
1. Species attributes needed for searching fetched from the <template> cards built for each species.
2. Determine if pagination exists (decided by Hugo based on number of species and 'maxSpeciesPerPage' in 'hugo/config.yaml').
3. Run the render function to display the species cards that should be shown.

Once loaded:
- Event listners created for search box, sort options dropdown and pagination controls (if pagination is enabled).
- Event listeners perform state modification and call the main render function anew (renderSpeciesCards)

Notes:
- This code can handle both pagination and no pagination (i.e. not enough species to warrant it). So can the Playwright tests assocaited with this page.
*/

const SORT_OPTIONS = {
    LAST_UPDATED: 'lastUpdated',
    A_TO_Z: 'alphabet',
    Z_TO_A: 'revAlphabet'
};

const cardContainer = document.getElementById('card-container');
const paginationItems = document.querySelectorAll('.pagination .page-item');
const noResultsCard = document.getElementById('no-filtered-card');
const paginationExists = paginationItems.length > 0; // if not enough species, there will be no pagination yet.
const cardsPerPage = parseInt(document.getElementById('card-container').dataset.numbCardsPerPage);

/**
 * Reformat Hugo generated date to be used in JS Date object.
 * Used for comparing last updated dates of species.
 *
 * @param {string} str - Date string in format 'dd/mm/yyyy'.
 */
function stringToDate(str) {
    const [dd, mm, yyyy] = str.split('/');
    return new Date(yyyy, mm - 1, dd);
}


/**
 * Runs on page load and initializes the state object.
 * Gets the info needed to search and order the species cards from each <template> card.
 *
 * @returns {Object} - The state object containing everything needed to render the species cards.
 */
function initState() {
    let state = {
        speciesData: [],
        currentPage: 1,
        sortOrder: SORT_OPTIONS.LAST_UPDATED,
        searchText: '',
        numbMatches: 0,
    };
    const templates = document.querySelectorAll('template[id^="card-"]');
    state.numbMatches = templates.length;

    templates.forEach(template => {
        const content = template.content;
        const title = content.querySelector('.science-name').textContent.toLowerCase();
        const subtitle = content.querySelector('.common-name').textContent.toLowerCase();
        const lastUpdatedText = content.querySelector('.card-text').textContent.replace('Last updated: ', '');
        const species = {
            id: template.id,
            speciesText: title + ' ' + subtitle, // used for searching
            last_updated: stringToDate(lastUpdatedText),
        };
        state.speciesData.push(species);
    });

    return state;
}


/**
 * Run on page load and every time an event listener is triggered.
 * Based on current state, updates: species cards, pagination buttons and the no results card.
 *
 * @param {Object} state - The state object containing the current state of the species cards.
 * @param {HTMLElement} cardContainer - The container element where species cards are displayed.
 */
function renderSpeciesCards(state, cardContainer) {
    cardContainer.innerHTML = '';
    const speciesIds = filterAndOrderSpecies(state.speciesData, state.searchText, state.sortOrder);
    state.numbMatches = speciesIds.length;

    let speciesToDisplay;
    if (paginationExists) {
        speciesToDisplay = paginateSpecies(speciesIds, state.currentPage);
    } else {
        speciesToDisplay = speciesIds;
    }

    if (speciesToDisplay.length === 0) {
        noResultsCard.style.display = 'block';
        state.currentPage = 1;
        updatePaginationButtons(state.numbMatches, state.currentPage);
    } else {
        noResultsCard.style.display = 'none';
        speciesToDisplay.forEach((speciesId) => {
            const template = document.getElementById(speciesId);
            const content = template.content.cloneNode(true);
            cardContainer.appendChild(content);
        });
        updatePaginationButtons(state.numbMatches, state.currentPage);
    }
}


// Sorting functions below

function sortLastUpdated(a, b) {
    return b.last_updated - a.last_updated;
}
function sortAlphabetically(a, b) {
    return a.speciesText.localeCompare(b.speciesText);
}
const sortRevAlphabetically = (a, b) => -sortAlphabetically(a, b);


/**
 * Search/filter all species and order them according to active dropdown selection
 * The id's of each species <template> is returned (in display order).
 *
 * @param {Array} speciesData - The array of species data objects.
 * @param {string} searchText - The text to filter species by.
 * @param {string} sortOrder - The order in which to sort the species (one of SORT_OPTIONS).
 * @returns {Array} - An array of species <template> IDs in display order.
 */
function filterAndOrderSpecies(speciesData, searchText, sortOrder) {
    let filteredSpecies = speciesData;

    // filter by text content
    if (searchText !== "") {
        filteredSpecies = speciesData.filter(species => {
            return species.speciesText.includes(searchText);
        });
    }

    // order species
    if (filteredSpecies.length !== 0) {
        if (sortOrder === SORT_OPTIONS.LAST_UPDATED) {
            filteredSpecies.sort(sortLastUpdated);
        } else if (sortOrder === SORT_OPTIONS.A_TO_Z) {
            filteredSpecies.sort(sortAlphabetically);
        } else {
            filteredSpecies.sort(sortRevAlphabetically);
        }
    }
    speciesIds = filteredSpecies.map(species => species.id);
    return speciesIds;
}


/**
 * Selects which species cards to show based on the current page number.
 *
 * @param {Array} speciesIds - An array of species <template> IDs in display order.
 * @param {number} currentPage - The current page number.
 * @returns {Array} - Array of species <template> IDs to be shown on this specific page.
 */
function paginateSpecies(speciesIds, currentPage) {
    const startIndex = (currentPage - 1) * cardsPerPage;
    const endIndex = startIndex + cardsPerPage;
    const paginatedSpeciesIds = speciesIds.slice(startIndex, endIndex);
    return paginatedSpeciesIds;
}


/**
 * Updates the dropdown view with the selected sorting option.
 * Fills in the dropdown inner HTML using 1 of 3 pre-prepared <templates> items.
 *
 * @param {string} sortOrder - The current sort order (one of SORT_OPTIONS).
 */
function updateSortDropdown(sortOrder) {
    const dropdown = document.querySelector(".scilife-sort-dropdown");
    const dropdownButtons = Object.values(SORT_OPTIONS);
    dropdownButtons.forEach(id => document.getElementById(id).classList.remove("active"));

    const activeButton = document.getElementById(sortOrder);
    activeButton.classList.add("active");

    const templateId = `text-${sortOrder}`;
    const template = document.getElementById(templateId);
    const clone = template.content.cloneNode(true);
    dropdown.innerHTML = '';
    dropdown.appendChild(clone);
}


/**
 * Updates the page number shown as active in the pagination
 *
 * @param {number} currentPage - Page number to be shown as active.
 */
function updateActivePage(currentPage) {
    paginationItems.forEach(item => {
        item.classList.remove('active');
    });
    const activePage = document.querySelector(`.pagination .page-link[data-page="${currentPage}"]`).parentElement;
    activePage.classList.add('active');
}


/**
 * Update the page number based on on the provided page identifier.
 *
 * @param {string|number} pageSelection - Can be 'prev', 'next', or a specific page number.
 * @param {number} currentPage - The current page number.
 * @param {number} numbSpecies - The total number of species.
 * @returns {number} - The new page number.
 */
function changeCurrentPage(pageSelection, currentPage, numbSpecies) {
    if (pageSelection === 'prev') {
        newPageNumb = Math.max(currentPage - 1, 1);
    } else if (pageSelection === 'next') {
        newPageNumb = Math.min(currentPage + 1, Math.ceil(numbSpecies / cardsPerPage));
    } else {
        newPageNumb = parseInt(pageSelection);
    }

    updateActivePage(newPageNumb);
    return newPageNumb;
}


/**
 * Sets which buttons are enabled/disabled based on the number of pages with results and the current page.
 *
 * @param {number} numbMatches - The total number of matches (species).
 * @param {number} currentPage - Current page number.
 */
function updatePaginationButtons(numbMatches, currentPage) {
    const numbActivePages = Math.ceil(numbMatches / cardsPerPage);

    paginationItems.forEach((item) => {
        const pageLink = item.querySelector('.page-link');
        const page = pageLink.getAttribute('data-page');
        if (page === 'prev') {
            item.classList.toggle('disabled', currentPage === 1);
        } else if (page === 'next') {
            item.classList.toggle('disabled', currentPage >= numbActivePages);
        } else {
            const pageIndex = parseInt(page);
            item.classList.toggle('disabled', pageIndex > numbActivePages);
        }
    });
}


/**
 * Debounce a function (used for species search)
 * @param {Function} callback - Function to debounce.
 * @param {number} delay - Delay in ms.
 * @returns {Function} - A debounced version of the function.
 */
function debounce(callback, delay) {
    let timer;
    return function (...args) {
        clearTimeout(timer)
        timer = setTimeout(() => {
            callback.apply(this, args);
        }, delay)
    }
}


/**
 * Setup on page load and addition of event listners.
 */
function main() {
    let state = initState();
    let cardContainer = document.getElementById('card-container');
    const numbSpecies = state.speciesData.length;
    renderSpeciesCards(state, cardContainer);

    // Event: type in search box
    // Reset to page 1, filter results and display them
    const debouncedSearch = debounce((event) => {
        state.searchText = event.target.value.toLowerCase();
        if (paginationExists) {
            state.currentPage = changeCurrentPage(1, state.currentPage, numbSpecies);
        }
        renderSpeciesCards(state, cardContainer);
    }, 200);
    document.querySelector('#Search').addEventListener('input', debouncedSearch);

    // Event: Change the ordering of the species via dropdown
    // Update the dropdown text with selected item, filter results and display them
    document.querySelector('.dropdown-menu').addEventListener('click', (event) => {
        if (event.target.classList.contains('scilife-dropdown-item')) {
            event.preventDefault();
            const sortSelected = event.target.id;
            const sortOrder = Object.keys(SORT_OPTIONS).find(key => SORT_OPTIONS[key] === sortSelected);
            state.sortOrder = SORT_OPTIONS[sortOrder];
            updateSortDropdown(state.sortOrder);
            renderSpeciesCards(state, cardContainer);
        }
    });

    // Event: Change the page
    // Change the page, update the cards with species in that slice of the data
    if (paginationExists) {
        document.querySelector('.pagination').addEventListener('click', (event) => {
            if (event.target.classList.contains('page-link')) {
                event.preventDefault();
                const pageSelection = event.target.getAttribute('data-page');
                state.currentPage = changeCurrentPage(pageSelection, state.currentPage, numbSpecies);
                renderSpeciesCards(state, cardContainer);
            }
        });
    }
}

main();
