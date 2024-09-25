// JavaScript function to reset the form fields after submission
function submitForm(event) {
    // Prevent default form submission behavior
    event.preventDefault();

    // Reset the form fields
    document.getElementById("expenditureForm").reset();
}

// Function to show entries for a specific page
function showPage(pageNumber) {
    const rows = document.querySelectorAll("#expenditureTable tbody tr");
    const itemsPerPage = 5;
    const startIndex = (pageNumber - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, rows.length);

    for (let i = 0; i < rows.length; i++) {
        if (i >= startIndex && i < endIndex) {
            rows[i].style.display = "";
        } else {
            rows[i].style.display = "none";
        }
    }
}

// Initial call to show the first page
showPage(1);

// function for button generation automation
function generatePaginationButtons(totalPages) {
    const paginationDiv = document.getElementById("pagination");
    paginationDiv.innerHTML = ""; // Clear existing buttons

    // Create "Prev" button
    const prevButton = document.createElement("button");
    prevButton.textContent = "Prev";
    prevButton.className = "prev";
    prevButton.addEventListener("click", function () {
        const currentPage = parseInt(document.querySelector('.active-page').textContent);
        const previousPage = currentPage - 1;
        if (previousPage >= 1) {
            showPage(previousPage);
            setActivePage(previousPage);
        }
    });
    paginationDiv.appendChild(prevButton);

    // Create buttons for each page
    for (let i = 1; i <= totalPages; i++) {
        const button = document.createElement("button");
        button.textContent = i;
        button.id = `page-${i}`;
        if (i == 1){
            setActivePage(1);
            button.classList.add('active-page');
        }
        button.addEventListener("click", function () {
            showPage(i);
            setActivePage(i);
        });
        paginationDiv.appendChild(button);
    }

    // Create "Next" button
    const nextButton = document.createElement("button");
    nextButton.textContent = "Next";
    nextButton.className = "nxt";
    nextButton.addEventListener("click", function () {
        const currentPage = parseInt(document.querySelector('.active-page').textContent);
        const nextPage = currentPage + 1;
        if (nextPage <= totalPages) {
            showPage(nextPage);
            setActivePage(nextPage);
        }
    });
    paginationDiv.appendChild(nextButton);
}

// Function to set the active page button
function setActivePage(pageNumber) {
    const activePage = document.querySelector(".active-page");
    if (activePage) {
        activePage.classList.remove("active-page");
    }
    const newActivePage = document.querySelector(`#page-${pageNumber}`);
    if (newActivePage) {
        newActivePage.classList.add("active-page");
    }
}

// Calculate total number of pages based on number of rows
const totalRows = document.querySelectorAll("#expenditureTable tbody tr").length;
const totalPages = Math.ceil(totalRows / 5);

// Generate pagination buttons
generatePaginationButtons(totalPages);

