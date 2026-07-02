from odoo import models, fields, api
from datetime import datetime, timedelta


class NexoDealerDashboard(models.Model):
    _name = 'nexo.dealer.dashboard'
    _description = 'Dashboard del concesionario'
    _rec_name = 'name'

    name = fields.Char('Nombre', default='Dashboard')

    total_vehicles = fields.Integer('Total en catálogo', compute='_compute_stats')
    available_vehicles = fields.Integer('Disponibles', compute='_compute_stats')
    sold_month = fields.Integer('Vendidos', compute='_compute_stats')
    sales_amount_month = fields.Float('Importe ventas', compute='_compute_stats')
    pending_services = fields.Integer('En servicio', compute='_compute_stats')
    today_test_drives = fields.Integer('Pruebas hoy', compute='_compute_stats')
    low_stock_count = fields.Integer('Vehículos próximos a agotarse', compute='_compute_stats')

    chart_sales_monthly = fields.Html('Ventas mensuales', compute='_compute_charts', sanitize=False, sanitize_tags=False, sanitize_attributes=False)
    chart_vehicle_status = fields.Html('Vehículos por estado', compute='_compute_charts', sanitize=False, sanitize_tags=False, sanitize_attributes=False)
    chart_brand_distribution = fields.Html('Distribución por marca', compute='_compute_charts', sanitize=False, sanitize_tags=False, sanitize_attributes=False)
    chart_services_monthly = fields.Html('Servicios mensuales', compute='_compute_charts', sanitize=False, sanitize_tags=False, sanitize_attributes=False)

    @api.depends_context('uid')
    def _compute_stats(self):
        today = datetime.today()
        day_start = today.replace(hour=0, minute=0, second=0)
        day_end = today.replace(hour=23, minute=59, second=59)
        for rec in self:
            rec.total_vehicles = rec.env['nexo.vehicle'].search_count([])
            rec.available_vehicles = rec.env['nexo.vehicle'].search_count([('vehicle_status', '=', 'available')])
            rec.sold_month = rec.env['nexo.vehicle'].search_count([('vehicle_status', '=', 'sold')])
            sold = rec.env['nexo.vehicle'].search([('vehicle_status', '=', 'sold')])
            rec.sales_amount_month = sum(v.sale_price or 0 for v in sold)
            rec.pending_services = rec.env['nexo.vehicle'].search_count([('vehicle_status', '=', 'in_service')])
            rec.today_test_drives = rec.env['nexo.vehicle.test.drive'].search_count([
                ('state', '=', 'scheduled'),
                ('date_hour', '>=', day_start),
                ('date_hour', '<=', day_end),
            ])

    @api.depends_context('uid')
    @api.depends_context('uid')
    def _compute_charts(self):
        today = datetime.today()
        for rec in self:
            months = []
            for i in range(5, -1, -1):
                m = today.month - i
                y = today.year
                while m <= 0:
                    m += 12
                    y -= 1
                ms = datetime(y, m, 1)
                if m == 12:
                    me = datetime(y + 1, 1, 1)
                else:
                    me = datetime(y, m + 1, 1)
                vehicles = rec.env['nexo.vehicle'].search([
                    ('create_date', '>=', ms), ('create_date', '<', me),
                ])
                months.append({'label': ms.strftime('%b %Y'), 'count': len(vehicles)})
            mx = max((d['count'] for d in months), default=1) or 1
            html_months = '<div class="nb-chart"><h4>Vehiculos por mes</h4><div class="nb-bars">'
            for d in months:
                h = int((d['count'] / mx) * 160)
                html_months += '<div class="nb-col"><div class="nb-bar" style="height:{}px"></div><div class="nb-val">{}</div><div class="nb-lbl">{}</div></div>'.format(h, d['count'], d['label'])
            html_months += '</div></div>'
            rec.chart_sales_monthly = html_months

            status_counts = {}
            for v in rec.env['nexo.vehicle'].search([]):
                s = v.vehicle_status or 'unknown'
                status_counts[s] = status_counts.get(s, 0) + 1
            slabels = {'available': 'Disponible', 'sold': 'Vendido', 'reserved': 'Reservado', 'in_service': 'En servicio', 'unknown': 'Sin estado'}
            scolors = {'available': '#28a745', 'sold': '#dc3545', 'reserved': '#ffc107', 'in_service': '#17a2b8', 'unknown': '#6c757d'}
            total_s = sum(status_counts.values()) or 1
            pcts = []
            legend = ''
            for k, v in status_counts.items():
                pct = round(v / total_s * 100)
                pcts.append('{} {}%'.format(scolors.get(k, '#6c757d'), pct))
                legend += '<div class="nb-ditem"><span class="nb-ddot" style="background:{}"></span>{} ({})</div>'.format(scolors.get(k, '#6c757d'), slabels.get(k, k), v)
            conic = ','.join(pcts)
            html_status = '<div class="nb-dwrap"><div class="nb-dring" style="background:conic-gradient({})"><div class="nb-dcenter">{}</div></div><div class="nb-dlegend">{}</div></div>'.format(conic, total_s, legend)
            rec.chart_vehicle_status = html_status

            brands = {}
            for v in rec.env['nexo.vehicle'].search([]):
                b = v.brand_id.name or 'Sin marca'
                brands[b] = brands.get(b, 0) + 1
            mx_b = max(brands.values(), default=1) or 1
            html_brands = '<div class="nb-chart"><h4>Top Marcas</h4>'
            for k, v in sorted(brands.items(), key=lambda x: -x[1])[:10]:
                pct = round(v / mx_b * 100)
                html_brands += '<div class="nb-row"><div class="nb-rlbl">{}</div><div class="nb-rtrack"><div class="nb-rfill" style="width:{}%"></div></div><div class="nb-rcnt">{}</div></div>'.format(k, pct, v)
            html_brands += '</div>'
            rec.chart_brand_distribution = html_brands

            svc_data = []
            for i in range(5, -1, -1):
                m = today.month - i
                y = today.year
                while m <= 0:
                    m += 12
                    y -= 1
                ms = datetime(y, m, 1)
                if m == 12:
                    me = datetime(y + 1, 1, 1)
                else:
                    me = datetime(y, m + 1, 1)
                services = rec.env['nexo.vehicle'].search([
                    ('vehicle_status', '=', 'in_service'),
                    ('write_date', '>=', ms), ('write_date', '<', me),
                ])
                svc_data.append({'label': ms.strftime('%b %Y'), 'count': len(services)})
            mx_s = max((d['count'] for d in svc_data), default=1) or 1
            html_svc = '<div class="nb-chart"><h4>Servicios mensuales</h4><div class="nb-bars">'
            for d in svc_data:
                h = int((d['count'] / mx_s) * 160)
                html_svc += '<div class="nb-col"><div class="nb-bar nb-bar-t" style="height:{}px"></div><div class="nb-val">{}</div><div class="nb-lbl">{}</div></div>'.format(h, d['count'], d['label'])
            html_svc += '</div></div>'
            rec.chart_services_monthly = html_svc

        # end for
        # end method
