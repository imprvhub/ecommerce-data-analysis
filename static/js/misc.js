function closeHtmlAndRedirect() {
    window.location.href = "/";
}

document.querySelectorAll('.table-container').forEach(element => {
    element.style.display = 'block';
});