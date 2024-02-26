function toggleDarkMode() {
    const body = document.body;
    const darkGraph = document.getElementById('graph-dark');
    const lightGraph = document.getElementById('graph-light');
    const figDarkGraph = document.getElementById('data_products_dark');
    const figLightGraph = document.getElementById('data_products_light');
    const countryDarkGraph = document.getElementById('country-graph-dark');
    const countryLightGraph = document.getElementById('country-graph-light');
    const darkModeIcon = document.getElementById('dark-mode-icon');
    const lightModeIcon = document.getElementById('light-mode-icon');
    const darkModeButton = document.getElementById('dark-mode-button');

    body.classList.toggle('dark-mode');

    const isDarkMode = body.classList.contains('dark-mode');

    darkGraph.style.display = isDarkMode ? 'block' : 'none';
    lightGraph.style.display = isDarkMode ? 'none' : 'block';
    figDarkGraph.style.display = isDarkMode ? 'block' : 'none';
    figLightGraph.style.display = isDarkMode ? 'none' : 'block';
    countryDarkGraph.style.display = isDarkMode ? 'block' : 'none';
    countryLightGraph.style.display = isDarkMode ? 'none' : 'block';
    darkModeIcon.style.display = isDarkMode ? 'inline' : 'none';
    lightModeIcon.style.display = isDarkMode ? 'none' : 'inline';
}

document.addEventListener('DOMContentLoaded', function () {
    var countryTable = document.querySelector('.table-container4 table');
    var countryRows = Array.from(countryTable.querySelectorAll('tr:nth-child(n+2)'));

    countryRows.sort(function (a, b) {
        var aValue = parseFloat(b.cells[3].textContent.replace(/[^\d.-]/g, '')) || 0;
        var bValue = parseFloat(a.cells[3].textContent.replace(/[^\d.-]/g, '')) || 0;
        return aValue - bValue;
    });

    countryRows.forEach(function (row) {
        countryTable.appendChild(row);
    });

    var winnerCountry = countryRows[0].cells[0].textContent;
    var winnerOrderCount = countryRows[0].cells[1].textContent;
    var winnerPercentage = countryRows[0].cells[2].textContent;
    var winnerTotalRevenue = countryRows[0].cells[3].textContent;

    var winnerContainer = document.querySelector('.table-container4');

    var h4Element = document.createElement('h4');

    h4Element.textContent = `${winnerCountry} with a total of ${winnerOrderCount} paid purchase orders was the country that contributed the most profit to the stores, with an amount of ${winnerTotalRevenue} USD, reaching ${winnerPercentage} of the total sales across all stores.`;
    h4Element.setAttribute("data-translate", "WinnerCountryInfo");
    h4Element.style.textAlign = 'center';
    h4Element.style.margin = '10px';
    winnerContainer.appendChild(h4Element);
});

document.addEventListener('DOMContentLoaded', function () {
    var table = document.querySelector('.table-container3 table');
    var rows = Array.from(table.querySelectorAll('tr:nth-child(n+2)'));

    rows.sort(function (a, b) {
        var aValue = parseFloat(b.cells[3].textContent.replace(/[^\d.-]/g, '')) || 0;
        var bValue = parseFloat(a.cells[3].textContent.replace(/[^\d.-]/g, '')) || 0;
        return aValue - bValue;
    });

    rows.forEach(function (row) {
        table.appendChild(row);
    });

    var winnerProduct = rows[0].cells[1].textContent;
    var winnerStore = rows[0].cells[0].textContent;
    var winnerTotalSales = rows[0].cells[3].textContent;
    var winnerPercentage = rows[0].cells[2].textContent;

    var graphContainer = document.querySelector('.graph-container2');

    var h3Element = document.createElement('h4');
    h3Element.textContent = `The product '${winnerProduct}' from the store '${winnerStore}' was the best-selling product with a total of ${winnerTotalSales} sales and a sales percentage of ${winnerPercentage} in the overall store.`;
    graphContainer.appendChild(h3Element);
});

document.addEventListener('DOMContentLoaded', function () {
    var revenueTable = document.querySelector('.table-container2 table');
    var revenueRows = Array.from(revenueTable.querySelectorAll('tr:nth-child(n+2)'));

    revenueRows.sort(function (a, b) {
        var aValue = parseFloat(a.cells[2].textContent.replace(/[^\d.-]/g, '')) || 0;
        var bValue = parseFloat(b.cells[2].textContent.replace(/[^\d.-]/g, '')) || 0;
        return bValue - aValue;
    });

    revenueRows.forEach(function (row) {
        revenueTable.appendChild(row);
    });

    var winnerUserName = revenueRows[0].cells[0].textContent;
    var winnerStoreName = revenueRows[0].cells[1].textContent;
    var winnerTotalRevenue = revenueRows[0].cells[2].textContent;

    var graphContainer = document.querySelector('.graph-container1');

    var h3Element = document.createElement('h4');
    h3Element.textContent = `'${winnerUserName}' from the store '${winnerStoreName}' achieved the best performance as a store manager with a total revenue of ${winnerTotalRevenue} USD.`;
    graphContainer.appendChild(h3Element);
});

document.addEventListener('DOMContentLoaded', function () {
    var accordionLinks = document.querySelectorAll('.accordion-container a');

    accordionLinks.forEach(function (link) {
        link.addEventListener('click', function (event) {
            event.preventDefault();

            var navbarHeight = document.querySelector('.navbar').offsetHeight;

            var targetId = link.getAttribute('href').substring(1);

            var targetElement = document.getElementById(targetId);

            if (targetElement) {
                var offsetTop = targetElement.offsetTop - navbarHeight;

                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth' 
                });
            }
        });
    });
});
