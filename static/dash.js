const sideMenu = document.querySelector('aside');
const menuBtn = document.getElementById('menu-btn');
const closeBtn = document.getElementById('close-btn');
const darkMode = document.querySelector('.dark-mode');

// Function to toggle dark mode
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode-variables');
    darkMode.querySelector('span:nth-child(1)').classList.toggle('active');
    darkMode.querySelector('span:nth-child(2)').classList.toggle('active');

    // Store the theme preference in local storage
    const isDarkMode = document.body.classList.contains('dark-mode-variables');
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
}

// Function to apply the stored theme preference
function applyStoredThemePreference() {
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme === 'dark') {
        toggleDarkMode(); // Apply dark mode if stored preference is dark
    }
}

// Event listeners
menuBtn.addEventListener('click', () => {
    sideMenu.style.display = 'block';
});

closeBtn.addEventListener('click', () => {
    sideMenu.style.display = 'none';
});

darkMode.addEventListener('click', toggleDarkMode);


// Apply stored theme preference when the page loads
window.addEventListener('load', applyStoredThemePreference);


//--------------------------------------------------------------- Pie chart section
var ctx = document.getElementById('expenditureChart').getContext('2d');
var catlab = categoryLabels;
var catamt = categoryAmounts;

// Create the pie chart with 3D effect
var expenditureChart = new Chart(ctx, {
    type: 'pie',
    data: {
        labels: catlab,
        datasets: [{
            label: 'Expenditure by Category',
            data: catamt,
            backgroundColor: [
                'rgba(255, 0, 106,1)', // Red
                'rgba(108, 155, 207,1)', // Blue
                'rgba(247, 208, 96,1)', // Yellow
                'rgba(27, 156, 133,1)', // Green
                // Add more colors as needed
            ],
            borderWidth: 0
        }]
    },
    options: {
        responsive: true,
        title: {
            display: true,
            text: 'Expenditure by Category'
        },
        plugins: {
            legend: {
                position: 'right'
            },
            tooltip: {
                position: 'average'
            }
        },
        layout: {
            padding: {
                left: 0,
                right: 0,
                top: 10,
                bottom: 0
            }
        },
        elements: {
            arc: {
                depth: 150, // Adjust the depth for 3D effect
                bevelWidth: 5 // Adjust the width of the bevel
            }
        }
    }
});

//-----------------------------------------line

// Get the canvas element for income chart
var incomeCtx = document.getElementById('incomeChart').getContext('2d');

// Parse the Flask variables to JavaScript arrays
var weeklyIncomeLabels = JSON.parse('{{ weekly_income_labels | tojson | safe }}');
var weeklyIncomeAmounts = JSON.parse('{{ weekly_income_amounts | tojson | safe }}');

// Data for income line chart
var weeklyIncomeData = {
    labels: weeklyIncomeLabels,
    datasets: [{
        label: 'Weekly Income',
        data: weeklyIncomeAmounts,
        borderColor: 'rgba(75, 192, 192, 1)', // Color for the line
        backgroundColor: 'rgba(75, 192, 192, 0.2)', // Fill color
        borderWidth: 2
    }]
};

// Line chart options
var incomeChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    title: {
        display: true,
        text: 'Weekly Income'
    },
    scales: {
        xAxes: [{
            type: 'category',
            scaleLabel: {
                display: true,
                labelString: 'Week of the Month'
            }
        }],
        yAxes: [{
            ticks: {
                beginAtZero: true,
                callback: function(value, index, values) {
                    return '$' + value;
                }
            },
            scaleLabel: {
                display: true,
                labelString: 'Income (USD)'
            }
        }]
    }
};

// Create the line chart
var incomeChart = new Chart(incomeCtx, {
    type: 'line',
    data: weeklyIncomeData,
    options: incomeChartOptions
});






