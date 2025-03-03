document.addEventListener("DOMContentLoaded", function () {
    toastr.options = {
        "closeButton": true,
        "debug": false,
        "newestOnTop": true,
        "progressBar": true,
        "positionClass": "toast-top-right",
        "preventDuplicates": true,
        "onclick": null,
        "showDuration": "300",
        "hideDuration": "1000",
        "timeOut": "5000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    };

    document.querySelector("form").addEventListener("submit", function (event) {
        event.preventDefault();
        toastr.info("Filtrage en cours...");
        setTimeout(() => {
            this.submit();
        }, 1000);
    });

    document.querySelectorAll(".table tbody tr").forEach(row => {
        row.addEventListener("click", function () {
            let paymentId = this.cells[0].textContent;
            toastr.success(`Paiement ID: ${paymentId} sélectionné.`);
        });
    });
});