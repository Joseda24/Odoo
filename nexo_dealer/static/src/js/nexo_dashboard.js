/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, onMounted, onWillUnmount, onWillStart, useRef, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadBundle } from "@web/core/assets";

class NexoDashboard extends Component {
    static template = "nexo_dealer.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.menuService = useService("menu");
        this.chartVehicles = useRef("chartVehicles");
        this.chartLeads = useRef("chartLeads");
        this.chartFinancing = useRef("chartFinancing");
        this.chartCommissions = useRef("chartCommissions");
        this.chartInventory = useRef("chartInventory");
        this.chartPurchase = useRef("chartPurchase");
        this.chartSales = useRef("chartSales");
        this.charts = [];
        this.chartLibLoaded = false;
        this.menuIds = {};
        this.state = useState({
            loading: true,
            data: {
                vehicle_by_status: { available: 0, sold: 0, reserved: 0, in_service: 0 },
                total_vehicles: 0, total_sale_orders: 0, confirmed_sales: 0,
                draft_quotations: 0, revenue_month: 0, total_purchase_orders: 0,
                total_commissions: 0, total_leads: 0, service_orders: 0,
                inventory_movements: 0, currency: "\u20ac",
                vehicle_chart: null, lead_chart: null, fin_chart: null,
                comm_chart: null, inv_chart: null, purchase_chart: null, monthly_sales: [],
                recent_orders: [], recent_purchases: [],
                filter_years: [], filter_salespersons: [],
            },
            sel_year: null,
            sel_salesperson: "",
        });

        onWillStart(async () => {
            this.menuIds = await this.orm.call("nexo.dashboard", "get_menu_ids", []);
            await this._loadData();
            await loadBundle("web.chartjs_lib");
            this.chartLibLoaded = true;
        });
        onMounted(() => this._renderCharts());
        onWillUnmount(() => this._destroyCharts());
    }

    async _loadData() {
        this.state.loading = true;
        try {
            const ctx = {};
            if (this.state.sel_year) ctx.year = parseInt(this.state.sel_year, 10);
            if (this.state.sel_salesperson) ctx.salesperson_id = parseInt(this.state.sel_salesperson, 10);
            this.state.data = await this.orm.call("nexo.dashboard", "get_dashboard_data", [], {context: ctx});
        } catch (e) {
            console.error("Dashboard data load failed", e);
        }
        this.state.loading = false;
    }

    async onFilterChange() {
        await this._loadData();
        this._renderCharts();
    }

    _renderCharts() {
        this._destroyCharts();
        if (this.state.loading || !this.chartLibLoaded) return;
        this._makeDonut(this.chartVehicles, this.state.data.vehicle_chart);
        this._makeDonut(this.chartLeads, this.state.data.lead_chart);
        this._makeDonut(this.chartFinancing, this.state.data.fin_chart);
        this._makeDonut(this.chartCommissions, this.state.data.comm_chart);
        this._makeDonut(this.chartPurchase, this.state.data.purchase_chart);
        this._makeDonut(this.chartInventory, this.state.data.inv_chart);
        this._renderSalesChart();
    }

    _makeDonut(ref, chartData) {
        const el = ref?.el;
        if (!el || !chartData || !chartData.values) return;
        const ctx = el.getContext("2d");
        this.charts.push(new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: chartData.labels,
                datasets: [{
                    data: chartData.values,
                    backgroundColor: chartData.colors,
                    borderWidth: 2,
                    borderColor: "#fff",
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "65%",
                plugins: {
                    legend: { position: "bottom", labels: { boxWidth: 10, padding: 8, font: { size: 10 } } },
                },
            },
        }));
    }

    _renderSalesChart() {
        const el = this.chartSales?.el;
        if (!el) return;
        const monthly = this.state.data.monthly_sales || [];
        const ctx = el.getContext("2d");
        this.charts.push(new Chart(ctx, {
            type: "bar",
            data: {
                labels: monthly.map(m => m.label),
                datasets: [{
                    label: "Ventas",
                    data: monthly.map(m => m.value),
                    backgroundColor: "rgba(113, 75, 223, 0.7)",
                    borderColor: "#714BDF",
                    borderWidth: 2,
                    borderRadius: 6,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => ` ${ctx.parsed.y.toLocaleString()} \u20ac`,
                        },
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: v => v.toLocaleString() + " \u20ac" },
                    },
                },
            },
        }));
    }

    _destroyCharts() {
        this.charts.forEach(c => c.destroy());
        this.charts = [];
    }

    openVehicles() { this.menuService.selectMenu(this.menuIds.fleet); }
    openSaleOrders() { this.menuService.selectMenu(this.menuIds.sale); }
    openPurchaseOrders() { this.menuService.selectMenu(this.menuIds.purchase); }
    openLeads() { this.menuService.selectMenu(this.menuIds.crm); }
    openService() { this.menuService.selectMenu(this.menuIds.repair); }
    openInventory() { this.menuService.selectMenu(this.menuIds.stock); }
    openFinancing() { this._open("nexo.financing.request", [[false, "list"], [false, "form"]], "Financiación"); }
    openCommissions() { this._open("nexo.commission", [[false, "list"], [false, "form"]], "Comisiones"); }

    _open(model, views, name) {
        this.action.doAction({ type: "ir.actions.act_window", res_model: model, views, name });
    }
}

registry.category("actions").add("nexo_dashboard.main", NexoDashboard);
