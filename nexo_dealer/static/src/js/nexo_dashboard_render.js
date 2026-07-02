odoo.define("nexo_dealer.dashboard_render", [], function (require) {
    "use strict";

    function colorBadges() {
        var colors = {
            'Disponible': '#28a745',
            'Vendido': '#dc3545',
            'Reservado': '#ffc107',
            'En servicio': '#17a2b8',
        };
        document.querySelectorAll('.badge').forEach(function(el) {
            var text = el.textContent.trim();
            if (colors[text]) {
                el.style.backgroundColor = colors[text];
                el.style.color = '#fff';
                el.style.border = 'none';
            }
        });
    }

    var observer = new MutationObserver(function() {
        colorBadges();
    });
    observer.observe(document.body || document.documentElement, {
        childList: true,
        subtree: true,
    });

    if (document.readyState === 'loading')
        document.addEventListener('DOMContentLoaded', colorBadges);
    else
        colorBadges();
});
