/*
Find tables on a page marked as wanting to be datatables and adds event listeners to them.
Tables with data-table="true" attribute are made into datatables.
*/

document.addEventListener('DOMContentLoaded', function() {
    var tables = document.querySelectorAll('table[data-table="true"]');
    tables.forEach(function(table) {

        // Table customisation options
        var info = table.getAttribute('data-info') === 'true' ? true : false;
        var ordering = table.getAttribute('data-ordering') === 'true' ? true : false;
        var paging = table.getAttribute('data-paging') === 'true' ? true : false;
        var searching = table.getAttribute('data-searching') === 'true' ? true : false;

        var tableName = '#' + table.id;
        new DataTable(tableName, {
            info: info,
            ordering: ordering,
            paging: paging,
            searching: searching
        });
    });
});
