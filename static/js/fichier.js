document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('forgotPass').onclick = function() {
        var link = document.getElementById('forgotPass');
        var language = document.getElementById('language');
        var href = link.href;
        link.setAttribute('href', href + '?language=' + language.value);
    };
});
