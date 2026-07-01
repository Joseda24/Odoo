odoo.define("nexo_dealer.dashboard_render", [], function (require) {
    "use strict";

    function loadChartJS(callback) {
        if (typeof Chart !== "undefined") {
            callback();
            return;
        }
        var script = document.createElement("script");
        script.src = "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js";
        script.onload = callback;
        document.head.appendChild(script);
    }

    function getChartData(form) {
        var data = {};
        var fields = form.querySelectorAll(
            "field[name=chart_sales_monthly], field[name=chart_vehicle_status], " +
            "field[name=chart_brand_distribution], field[name=chart_services_monthly]"
        );
        fields.forEach(function (f) {
            var name = f.getAttribute("name");
            try {
                data[name] = JSON.parse(f.textContent || f.innerHTML || "null");
            } catch (e) {
                data[name] = null;
            }
        });
        return data;
    }

    function renderCharts() {
        var form = document.querySelector(".o_form_view");
        if (!form) return;
        var chartData = getChartData(form);
        var containers = form.querySelectorAll(".nexo-chart");
        if (!containers.length) return;
        loadChartJS(function () {
            containers.forEach(function (el) {
                var type = el.getAttribute("data-chart");
                if (!type) return;
                var ctx = document.createElement("canvas");
                el.innerHTML = "";
                el.appendChild(ctx);
                var config = getChartConfig(type, chartData);
                if (config) {
                    new Chart(ctx, config);
                }
            });
        });
    }

    function getChartConfig(type, data) {
        var commonOpts = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: "bottom" } },
        };
        if (type === "sales" && data.chart_sales_monthly) {
            var labels = data.chart_sales_monthly.map(function (d) { return d.month; });
            return {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "Unidades",
                            data: data.chart_sales_monthly.map(function (d) { return d.count; }),
                            backgroundColor: "rgba(54, 162, 235, 0.5)",
                            borderColor: "rgba(54, 162, 235, 1)",
                            borderWidth: 1,
                            yAxisID: "y",
                        },
                        {
                            label: "Monto",
                            data: data.chart_sales_monthly.map(function (d) { return d.amount; }),
                            backgroundColor: "rgba(255, 159, 64, 0.5)",
                            borderColor: "rgba(255, 159, 64, 1)",
                            borderWidth: 1,
                            yAxisID: "y1",
                        },
                    ],
                },
                options: Object.assign({}, commonOpts, {
                    scales: {
                        y: { beginAtZero: true, position: "left", title: { display: true, text: "Unidades" } },
                        y1: { beginAtZero: true, position: "right", grid: { drawOnChartArea: false }, title: { display: true, text: "Monto" } },
                    },
                }),
            };
        }
        if (type === "status" && data.chart_vehicle_status) {
            return {
                type: "doughnut",
                data: {
                    labels: data.chart_vehicle_status.map(function (d) { return d.label; }),
                    datasets: [{
                        data: data.chart_vehicle_status.map(function (d) { return d.value; }),
                        backgroundColor: [
                            "rgba(75, 192, 192, 0.6)",
                            "rgba(255, 99, 132, 0.6)",
                            "rgba(255, 205, 86, 0.6)",
                            "rgba(54, 162, 235, 0.6)",
                            "rgba(153, 102, 255, 0.6)",
                        ],
                    }],
                },
                options: commonOpts,
            };
        }
        if (type === "brands" && data.chart_brand_distribution) {
            return {
                type: "bar",
                data: {
                    labels: data.chart_brand_distribution.map(function (d) { return d.label; }),
                    datasets: [{
                        label: "Vehículos",
                        data: data.chart_brand_distribution.map(function (d) { return d.value; }),
                        backgroundColor: "rgba(75, 192, 192, 0.5)",
                        borderColor: "rgba(75, 192, 192, 1)",
                        borderWidth: 1,
                    }],
                },
                options: Object.assign({}, commonOpts, {
                    indexAxis: "y",
                    scales: { x: { beginAtZero: true } },
                }),
            };
        }
        if (type === "services" && data.chart_services_monthly) {
            var labels = data.chart_services_monthly.map(function (d) { return d.month; });
            return {
                type: "line",
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "Creadas",
                            data: data.chart_services_monthly.map(function (d) { return d.count; }),
                            borderColor: "rgba(54, 162, 235, 1)",
                            backgroundColor: "rgba(54, 162, 235, 0.1)",
                            fill: true,
                            tension: 0.3,
                        },
                        {
                            label: "Completadas",
                            data: data.chart_services_monthly.map(function (d) { return d.completed; }),
                            borderColor: "rgba(75, 192, 192, 1)",
                            backgroundColor: "rgba(75, 192, 192, 0.1)",
                            fill: true,
                            tension: 0.3,
                        },
                    ],
                },
                options: Object.assign({}, commonOpts, {
                    scales: { y: { beginAtZero: true } },
                }),
            };
        }
        return null;
    }

    function startObserver() {
        var form = document.querySelector(".o_form_view");
        if (form && form.querySelector(".nexo-chart")) {
            renderCharts();
            return;
        }
        var target = document.body || document.documentElement;
        if (!target) {
            if (document.readyState === "loading") {
                document.addEventListener("DOMContentLoaded", startObserver);
            }
            return;
        }
        var observer = new MutationObserver(function () {
            var f = document.querySelector(".o_form_view");
            if (f && f.querySelector(".nexo-chart")) {
                observer.disconnect();
                renderCharts();
            }
        });
        observer.observe(target, { childList: true, subtree: true });
    }
    startObserver();
});
