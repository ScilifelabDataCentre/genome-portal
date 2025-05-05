/*
Creates a population map using the GBIF API and leaflet for a given species.
*/


/**
 * Runs on page load and initializes the global state object.
 *
 * @returns {Object} - The state object containing everything needed to render the species map.
 */
function initState() {
    const mapElement = document.getElementById('map');
    const latitude = mapElement.getAttribute('data-latitude');
    const longitude = mapElement.getAttribute('data-longitude');
    const initialZoom = mapElement.getAttribute('data-initial-zoom');
    const gbifTaxonId = mapElement.getAttribute('data-gbif-taxon-id');

    // pre built html element for error message (display:none unless error)
    const mapErrorMessage = document.getElementById('map-error-message');

    const map = L.map('map', {
        minZoom: 1,
        maxZoom: 15,
    }).setView([latitude, longitude], initialZoom);

    map.attributionControl.setPrefix('<a href="https://leafletjs.com" title="A JavaScript library for interactive maps">Leaflet</a>')

    return {
        map: map,
        latitude: latitude,
        longitude: longitude,
        initialZoom: initialZoom,
        gbifTaxonId: gbifTaxonId,
        mapErrorMessage: mapErrorMessage,
    };
}


/**
 * Add the tileset layer
 * format is: https://tile.gbif.org/{srs}/{tileset}/{z}/{x}/{y}{format}{params}
 *
 * @param {L.Map} map - The Leaflet map instance.
 */
function addBaseLayer(map) {
    L.tileLayer('https://tile.gbif.org/3857/omt/{z}/{x}/{y}@1x.png?style=gbif-geyser-en', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
        maxZoom: 15,
    }).addTo(map);

    console.log('Base layer added');
}


/**
 * Add the GBIF occurrences overlay
 * @param {L.Map} map - The Leaflet map instance
 * @param {string} gbifTaxonId - The GBIF taxon ID for the species.
 * @returns {L.TileLayer} - The Leaflet tile layer for the GBIF occurrences overlay
 */
function addObservationLayer(map, gbifTaxonId) {
    const gbifUrl = `https://api.gbif.org/v2/map/occurrence/density/{z}/{x}/{y}@1x.png?srs=EPSG%3A3857&taxonKey=${gbifTaxonId}&style=blue.marker&year=2000,2099`;
    const gbifAttrib = '<a href="https://www.gbif.org">GBIF</a>';

    const obsverationLayer = L.tileLayer(gbifUrl, {
        minZoom: 1,
        maxZoom: 15,
        zoomOffset: -1,
        tileSize: 512,
        attribution: gbifAttrib
    }).addTo(map);

    return obsverationLayer;
}


/**
 * Add a help button, when clicked, toast pop-up happens.
 *
 * @param {L.Map} map - The Leaflet map instance
 */
function addHelpButton(map) {
    const helpControl = L.control({ position: 'topright' });
    const helpButtonHTML = '<button class="btn btn-light" id="helpButton" style="font-size: 1.3rem"><img src="/img/icons/question.svg" alt="Help button" class="scilife-icons-xl"></button>';

    helpControl.onAdd = function (map) {
        let div = L.DomUtil.create('div', 'help-control');
        div.innerHTML = helpButtonHTML;
        return div;
    };

    helpControl.addTo(map);

    document.getElementById('helpButton').addEventListener('click', function () {
        document.querySelectorAll('.toast').forEach(function (toast) {
            toast.classList.add('show');
        });
    });
}


/**
 * Setup the map on page load and add event listners to control the error message's state.
 * The error message is set to display: none by default in the HTML.
 */
function main() {
    let state = initState();

    // May still be good to have this here to prevent caching issues (if error on prior page load)
    state.map.on('load', function () {
        state.mapErrorMessage.style.display = 'none';
    });

    addHelpButton(state.map);
    addBaseLayer(state.map);

    // tileerror occurs if no observations are found (not caught by general error handler below)
    const obsverationLayer = addObservationLayer(state.map, state.gbifTaxonId);
    obsverationLayer.on('tileerror', function (event) {
        state.mapErrorMessage.style.display = 'block';
        console.warn('tileerror: No observations found for this taxon, check the taxon ID is correct');
    });

    // This includes errors triggered after initial load (e.g. user zooms in/out)
    state.map.on('error', function () {
        state.mapErrorMessage.style.display = 'block';
    });
}

document.addEventListener('DOMContentLoaded', main);
