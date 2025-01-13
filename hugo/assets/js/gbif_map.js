/*
Creates a population map using the GBIF API and leaflet for a given species.
*/

document.addEventListener("DOMContentLoaded", function () {
    const mapElement = document.getElementById('map');
    const latitude = mapElement.getAttribute('data-latitude');
    const longitude = mapElement.getAttribute('data-longitude');
    const initialZoom = mapElement.getAttribute('data-initial-zoom');
    const gbifTaxonId = mapElement.getAttribute('data-gbif-taxon-id');

    const map = L.map('map', {
        minZoom: 1,
        maxZoom: 15,
    }).setView([latitude, longitude], initialZoom);

    map.attributionControl.setPrefix('<a href="https://leafletjs.com" title="A JavaScript library for interactive maps">Leaflet</a>')

    // Add the map tile layer from GBIF
    // format is: https://tile.gbif.org/{srs}/{tileset}/{z}/{x}/{y}{format}{params}
    const baseLayer = L.tileLayer('https://tile.gbif.org/3857/omt/{z}/{x}/{y}@1x.png?style=gbif-geyser-en', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
        maxZoom: 15,
    }).addTo(map);

    // add the GBIF occurrence overlay
    const gbifUrl = `https://api.gbif.org/v2/map/occurrence/density/{z}/{x}/{y}@1x.png?srs=EPSG%3A3857&taxonKey=${gbifTaxonId}&style=blue.marker&year=2000,2099`;
    const gbifAttrib = '<a href="https://www.gbif.org">GBIF</a>';

    const gbifLayer = L.tileLayer(gbifUrl, {
        minZoom: 1,
        maxZoom: 15,
        zoomOffset: -1,
        tileSize: 512,
        attribution: gbifAttrib
    }).addTo(map);

    // event listeners for api errors
    let mapError = false;
    baseLayer.on('tileerror', function (error) {
        mapError = true;
    });
    gbifLayer.on('tileerror', function (error) {
        mapError = true;
    });

    let hasRun = false;
    gbifLayer.on('load', function () {
        if (!hasRun) {
            hasRun = true;

            if (mapError) {
                // Update map with a generic error message.
                if (!document.querySelector('.map-error-message')) {
                    const errorMessage = L.control({ position: 'bottomright' });

                    errorMessage.onAdd = function (map) {
                        const div = L.DomUtil.create('div', 'map-error-message');
                        div.innerHTML = '<h1>The distribution map is temporarily unavailable</h1>';
                        return div;
                    };
                    errorMessage.addTo(map);
                }
            } else {
                // Add a help button, when clicked, toast pop-up happens.
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
        }
    });
});
