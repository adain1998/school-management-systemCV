// JavaScript to enhance user interactions with Toastr notifications

document.addEventListener('DOMContentLoaded', function () {
  // Handle alert dismiss actions
  const alertButtons = document.querySelectorAll('.btn-close');
  alertButtons.forEach(button => {
    button.addEventListener('click', function () {
      const alert = this.closest('.alert');
      alert.classList.remove('show');
      alert.classList.add('fade');
    });
  });
});

// Optional: Custom Toastr configuration for better UX
toastr.options = {
  "closeButton": true,
  "progressBar": true,
  "positionClass": "toast-top-right",
  "timeOut": "5000", // 5 seconds timeout
  "extendedTimeOut": "1000", // Time to close after mouse hover
  "showMethod": "slideDown",
  "hideMethod": "slideUp"
};

// Display flash messages with Toastr
{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    {% for category, message in messages %}
      {% if category == 'success' %}
        toastr.success("{{ message }}");
      {% elif category == 'error' %}
        toastr.error("{{ message }}");
      {% elif category == 'warning' %}
        toastr.warning("{{ message }}");
      {% else %}
        toastr.info("{{ message }}");
      {% endif %}
    {% endfor %}
  {% endif %}
{% endwith %}
