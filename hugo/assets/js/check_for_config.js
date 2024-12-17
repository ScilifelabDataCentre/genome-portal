
/* Check if a config file exists before loading JBrowse2
Otherwise, display an alert to the user that no config file exists
*/
document.addEventListener('DOMContentLoaded', async function () {
    const urlParams = new URLSearchParams(window.location.search);
    const configFile = urlParams.get('config');
    const noConfigBlock = document.getElementById('no-config');
    const jbrowseBlock = document.getElementById('root');

    if (!configFile) {
        noConfigBlock.style.display = 'block';
        jbrowseBlock.style.display = 'none';
        return;
    }

    try {
        const response = await fetch(configFile);
        if (response.ok) {
            return;
        } else {
            noConfigBlock.style.display = 'block';
            jbrowseBlock.style.display = 'none';
        }
    } catch (error) {
        noConfigBlock.style.display = 'block';
        jbrowseBlock.style.display = 'none';
    }
});
