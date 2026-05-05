function filterTable() {
    const input = document.getElementById("searchInput").value.toUpperCase();
    const statusFilter = document.getElementById("statusFilter").value.toUpperCase();
    const table = document.querySelector(".soc-table");
    const tr = table.getElementsByTagName("tr");

    for (let i = 1; i < tr.length; i++) {
        const row = tr[i];
        const rowText = row.innerText.toUpperCase();
        const statusCell = row.getElementsByTagName("td")[2];

        if (statusCell) {
            const statusText = statusCell.innerText.toUpperCase();
            const matchesSearch = input === "" || rowText.indexOf(input) > -1;
            const matchesStatus = statusFilter === "" || statusText.indexOf(statusFilter) > -1;

            row.style.display = matchesSearch && matchesStatus ? "" : "none";
        }
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("searchInput");
    if (!searchInput) {
        return;
    }

    searchInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            filterTable();
        }
    });
});