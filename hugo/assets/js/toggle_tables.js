/*
Add toggle to swap between the long and short tables on each species download page.
*/

document.addEventListener('DOMContentLoaded', function () {
    const checkbox = document.getElementById('flexSwitchCheckChecked');
    const longTable = document.getElementById('table-container-long');
    const shortTable = document.getElementById('table-container-short');

    if (!checkbox || !longTable || !shortTable) {
        console.error('Required elements not found');
        return;
    }

    checkbox.addEventListener('change', function () {
        if (this.checked) {
            longTable.style.display = 'none';
            shortTable.style.display = 'block';
        } else {
            longTable.style.display = 'block';
            shortTable.style.display = 'none';
        }
    });

    // Initial state setup
    checkbox.dispatchEvent(new Event('change'));
});
