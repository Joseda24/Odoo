from odoo import models, fields, api
from datetime import datetime, timedelta


class NexoDealerDashboard(models.Model):
    _name = 'nexo.dealer.dashboard'
    _description = 'Dashboard del concesionario'

    total_vehicles = fields.Integer('Total en catálogo', compute='_compute_stats')
    available_vehicles = fields.Integer('Disponibles', compute='_compute_stats')
    sold_month = fields.Integer('Vendidos este mes', compute='_compute_stats')
    sales_amount_month = fields.Float('Importe ventas del mes', compute='_compute_stats')
    pending_services = fields.Integer('Servicios pendientes', compute='_compute_stats')
    today_test_drives = fields.Integer('Pruebas hoy', compute='_compute_stats')
    low_stock_count = fields.Integer('Vehículos próximos a agotarse', compute='_compute_stats')

    chart_sales_monthly = fields.Text('Ventas mensuales', compute='_compute_charts')
    chart_vehicle_status = fields.Text('Vehículos por estado', compute='_compute_charts')
    chart_brand_distribution = fields.Text('Distribución por marca', compute='_compute_charts')
    chart_services_monthly = fields.Text('Servicios mensuales', compute='_compute_charts')

    @api.depends_context('uid')
    def _compute_stats(self):
        today = datetime.today()
        month_start = today.replace(day=1, hour=0, minute=0, second=0)
        day_start = today.replace(hour=0, minute=0, second=0)
        day_end = today.replace(hour=23, minute=59, second=59)
        for rec in self:
            rec.total_vehicles = rec.env['nexo.vehicle'].search_count([])
            rec.available_vehicles = rec.env['nexo.vehicle'].search_count([('vehicle_status', '=', 'available')])
            rec.sold_month = rec.env['nexo.sale.order'].search_count([
                ('state', '=', 'done'),
                ('date_order', '>=', month_start),
            ])
            sales = rec.env['nexo.sale.order'].search([
                ('state', '=', 'done'),
                ('date_order', '>=', month_start),
            ])
            rec.sales_amount_month = sum(s.amount_total for s in sales)
            rec.pending_services = rec.env['nexo.vehicle.service.order'].search_count([
                ('state', 'in', ['draft', 'in_progress']),
            ])
            rec.today_test_drives = rec.env['nexo.vehicle.test.drive'].search_count([
                ('state', '=', 'scheduled'),
                ('date_hour', '>=', day_start),
                ('date_hour', '<=', day_end),
            ])

    @api.depends_context('uid')
    def _compute_charts(self):
        import json
        today = datetime.today()
        for rec in self:
            # Monthly sales last 6 months
            months_data = []
            for i in range(5, -1, -1):
                m = today.month - i
                y = today.year
                while m <= 0:
                    m += 12
                    y -= 1
                m_start = datetime(y, m, 1)
                if m == 12:
                    m_end = datetime(y + 1, 1, 1)
                else:
                    m_end = datetime(y, m + 1, 1)
                sales = rec.env['nexo.sale.order'].search([
                    ('state', '=', 'done'),
                    ('date_order', '>=', m_start),
                    ('date_order', '<', m_end),
                ])
                months_data.append({
                    'month': m_start.strftime('%b %Y'),
                    'count': len(sales),
                    'amount': sum(s.amount_total for s in sales),
                })
            rec.chart_sales_monthly = json.dumps(months_data)

            # Vehicle status distribution
            status_counts = {}
            for v in rec.env['nexo.vehicle'].search([]):
                s = v.vehicle_status or 'unknown'
                status_counts[s] = status_counts.get(s, 0) + 1
            status_labels = {
                'available': 'Disponible',
                'sold': 'Vendido',
                'reserved': 'Reservado',
                'in_service': 'En servicio',
                'unknown': 'Sin estado',
            }
            status_data = [{'label': status_labels.get(k, k), 'value': v} for k, v in status_counts.items()]
            rec.chart_vehicle_status = json.dumps(status_data)

            # Brand distribution
            brands = {}
            for v in rec.env['nexo.vehicle'].search([]):
                b = v.brand_id.name or 'Sin marca'
                brands[b] = brands.get(b, 0) + 1
            brand_data = [{'label': k, 'value': v} for k, v in sorted(brands.items(), key=lambda x: -x[1])[:10]]
            rec.chart_brand_distribution = json.dumps(brand_data)

            # Monthly services last 6 months
            svc_data = []
            for i in range(5, -1, -1):
                m = today.month - i
                y = today.year
                while m <= 0:
                    m += 12
                    y -= 1
                m_start = datetime(y, m, 1)
                if m == 12:
                    m_end = datetime(y + 1, 1, 1)
                else:
                    m_end = datetime(y, m + 1, 1)
                services = rec.env['nexo.vehicle.service.order'].search([
                    ('date_in', '>=', m_start),
                    ('date_in', '<', m_end),
                ])
                svc_data.append({
                    'month': m_start.strftime('%b %Y'),
                    'count': len(services),
                    'completed': len(services.filtered(lambda s: s.state == 'done')),
                })
            rec.chart_services_monthly = json.dumps(svc_data)
