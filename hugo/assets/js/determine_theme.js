/*
This script runs as early as possible to detect if a user prefers dark or light mode.
Running as early as possible prevents the "white flash" (if user prefers dark mode) seen when loading the page otherwise.
This script works with "change_theme.js" which provides a way to swap the mode/theme once the page is loaded.

Note: extra brackets on the function make it a: Immediately Invoked Function Expression
*/
(function() {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const currentTheme = localStorage.getItem('bsTheme') || (prefersDark ? 'dark' : 'light');
    document.documentElement.setAttribute('data-bs-theme', currentTheme);
})();
