from odoo import models, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class NexoDashboard(models.Model):
    _name = 'nexo.dashboard'
    _description = 'Nexo Dealer Dashboard'
    _auto = False

    @api.model
    def get_menu_ids(self):
        return {
            'fleet': self.env.ref('fleet.menu_root').id,
            'sale': self.env.ref('sale.sale_menu_root').id,
            'purchase': self.env.ref('purchase.menu_purchase_root').id,
            'crm': self.env.ref('crm.crm_menu_root').id,
            'repair': self.env.ref('repair.menu_repair_order').id,
            'stock': self.env.ref('stock.menu_stock_root').id,
        }

    @api.model
    def get_dashboard_data(self):
        today = datetime.today()
        ctx = self.env.context
        year = ctx.get('year') or today.year
        salesperson_id = ctx.get('salesperson_id')

        sp_domain = []
        if salesperson_id:
            sp_domain = [('user_id', '=', int(salesperson_id))]

        thirty_days_ago = (today - timedelta(days=30)).strftime('%Y-%m-%d')

        user_sale_domain = sp_domain[:]
        user_lead_domain = [('user_id', '=', int(salesperson_id))] if salesperson_id else []
        user_repair_domain = [('user_id', '=', int(salesperson_id))] if salesperson_id else []

        # ── Vehicles ──
        statuses = ['available', 'sold', 'reserved', 'in_service', 'to_order']
        vehicle_by_status = {}
        for s in statuses:
            vehicle_by_status[s] = self.env['fleet.vehicle'].search_count([('vehicle_status', '=', s)])
        total_vehicles = sum(vehicle_by_status.values())

        # ── Sales ──
        sale_orders = self.env['sale.order'].search(user_sale_domain[:] + [('id', '!=', False)])
        total_sale_orders = len(sale_orders)
        confirmed_sales = len(sale_orders.filtered(lambda o: o.state == 'sale'))
        draft_quotations = len(sale_orders.filtered(lambda o: o.state == 'draft'))

        month_sales = self.env['sale.order'].search(user_sale_domain[:] + [
            ('state', '=', 'sale'),
            ('date_order', '>=', today.replace(day=1).strftime('%Y-%m-%d')),
        ])
        revenue_month = round(sum(month_sales.mapped('amount_total')), 2)

        total_purchase_orders = self.env['purchase.order'].search_count([])
        total_commissions = self.env['nexo.commission'].search_count([('paid', '=', False)])
        total_leads = self.env['crm.lead'].search_count(user_lead_domain)
        service_orders = self.env['repair.order'].search_count(
            user_repair_domain[:] + [('create_date', '>=', thirty_days_ago)]
        )
        inventory_movements = self.env['nexo.vehicle.inventory'].search_count([('date_in', '>=', thirty_days_ago)])

        # ── Charts data ──

        # Vehicle status donut
        vehicle_chart = {
            'labels': ['Disponibles', 'Vendidos', 'Reservados', 'En servicio', 'A pedir'],
            'values': [vehicle_by_status.get(s, 0) for s in statuses],
            'colors': ['#28a745', '#dc3545', '#ffc107', '#17a2b8', '#6c757d'],
        }

        # Leads donut
        all_leads = self.env['crm.lead'].search(user_lead_domain)
        won = len(all_leads.filtered(lambda l: l.stage_id.is_won))
        in_progress = total_leads - won
        lead_chart = {
            'labels': ['Ganadas', 'En progreso'],
            'values': [won, max(0, in_progress)],
            'colors': ['#28a745', '#ffc107'],
        }

        # Financing donut
        financing_requests = self.env['nexo.financing.request'].search([])
        fin_approved = len(financing_requests.filtered(lambda r: r.status == 'approved'))
        fin_rejected = len(financing_requests.filtered(lambda r: r.status == 'rejected'))
        fin_pending = len(financing_requests.filtered(lambda r: r.status in ('submitted', 'draft')))
        fin_chart = {
            'labels': ['Aprobados', 'Rechazados', 'Pendientes'],
            'values': [fin_approved, fin_rejected, fin_pending],
            'colors': ['#28a745', '#dc3545', '#ffc107'],
        }

        # Commissions donut
        commissions = self.env['nexo.commission'].search([])
        comm_paid = len(commissions.filtered(lambda c: c.paid))
        comm_pending = len(commissions.filtered(lambda c: not c.paid))
        comm_chart = {
            'labels': ['Pagadas', 'Pendientes'],
            'values': [comm_paid, comm_pending],
            'colors': ['#28a745', '#ffc107'],
        }

        # Inventory movement type donut
        inv_moves = self.env['nexo.vehicle.inventory'].search([])
        inv_types = {}
        for move in inv_moves:
            move_type = move.type or 'other'
            inv_types[move_type] = inv_types.get(move_type, 0) + 1
        type_labels = {
            'purchase': 'Compra', 'consignment': 'Consignación',
            'transfer': 'Transferencia', 'return': 'Devolución',
            'trade_in': 'Trade-in', 'other': 'Otro',
        }
        inv_chart = {
            'labels': [type_labels.get(k, k) for k in inv_types.keys()],
            'values': list(inv_types.values()),
            'colors': ['#714BDF', '#17a2b8', '#fd7e14', '#20c997', '#e83e8c', '#6c757d'][:len(inv_types)],
        }

        # Monthly sales bar chart (selected year)
        monthly_sales = []
        max_month = today.month if year == today.year else 12
        for m in range(1, max_month + 1):
            start = datetime(year, m, 1)
            end = (start + relativedelta(months=1)) - timedelta(days=1)
            if end > today and year == today.year:
                end = today
            orders_in_month = self.env['sale.order'].search([
                ('state', '=', 'sale'),
                ('date_order', '>=', start.strftime('%Y-%m-%d')),
                ('date_order', '<=', end.strftime('%Y-%m-%d')),
            ] + user_sale_domain)
            monthly_sales.append({
                'label': start.strftime('%b'),
                'value': round(sum(orders_in_month.mapped('amount_total')), 2),
            })

        # ── Recent orders ──
        recent_orders = self.env['sale.order'].search_read(
            user_sale_domain[:] + [('id', '!=', 0)],
            ['name', 'partner_id', 'amount_total', 'date_order', 'state', 'vehicle_id'],
            limit=5, order='date_order desc',
        )
        recent_purchases = self.env['purchase.order'].search_read(
            [], ['name', 'partner_id', 'amount_total', 'date_order', 'state'],
            limit=5, order='date_order desc',
        )

        # ── Filter metadata ──
        current_year = today.year
        filter_years = [current_year - i for i in range(4)]
        salespersons = self.env['res.users'].search_read(
            [('share', '=', False)],
            ['id', 'name'],
            order='name',
        )

        return {
            'total_vehicles': total_vehicles,
            'vehicle_by_status': vehicle_by_status,
            'total_sale_orders': total_sale_orders,
            'confirmed_sales': confirmed_sales,
            'draft_quotations': draft_quotations,
            'revenue_month': revenue_month,
            'total_purchase_orders': total_purchase_orders,
            'total_commissions': total_commissions,
            'total_leads': total_leads,
            'service_orders': service_orders,
            'inventory_movements': inventory_movements,
            'vehicle_chart': vehicle_chart,
            'lead_chart': lead_chart,
            'fin_chart': fin_chart,
            'comm_chart': comm_chart,
            'inv_chart': inv_chart,
            'monthly_sales': monthly_sales,
            'recent_orders': recent_orders,
            'recent_purchases': recent_purchases,
            'currency': '\u20ac',
            'filter_years': filter_years,
            'filter_salespersons': [{'id': s['id'], 'name': s['name']} for s in salespersons],
        }
