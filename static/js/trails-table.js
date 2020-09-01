$(document).ready(function () {
    $('#trails-table').DataTable();
});

$('#trails-table').dataTable({
    "lengthMenu": [10, 20, 30, 40, 50, 75, 100]
});

$('#trails-table').dataTable({
    "autoWidth": False
})