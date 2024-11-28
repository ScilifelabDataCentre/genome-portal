/*
Get the current date and set it in any span element with class "todays-date"
Format looks like: November 27, 2024
*/
const options = { year: 'numeric', month: 'long', day: 'numeric' };
const today = new Date();
const formattedDate = today.toLocaleDateString("en-US", options);

const dateElements = document.getElementsByClassName("todays-date");
for (let element of dateElements) {
    element.innerHTML = formattedDate;
}
