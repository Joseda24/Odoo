from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date, timedelta


class NexoFinancingPlan(models.Model):
    _name = 'nexo.financing.plan'
    _description = 'Plan de financiamiento'
    _order = 'name'

    name = fields.Char('Nombre', required=True)
    months = fields.Integer('Plazo (meses)', required=True)
    interest_rate = fields.Float('Tasa de interés anual %', required=True)
    down_payment_percent = fields.Float('% Enganche', default=20.0)
    active = fields.Boolean('Activo', default=True)


class NexoFinancingRequest(models.Model):
    _name = 'nexo.financing.request'
    _description = 'Solicitud de financiamiento'
    _order = 'date desc, id desc'

    name = fields.Char('Folio', required=True, copy=False, readonly=True, default='Nuevo')
    partner_id = fields.Many2one('nexo.partner', 'Cliente', required=True)
    vehicle_id = fields.Many2one('nexo.vehicle', 'Vehículo', required=True)
    sale_order_id = fields.Many2one('nexo.sale.order', 'Pedido de venta')
    plan_id = fields.Many2one('nexo.financing.plan', 'Plan', required=True)
    vehicle_price = fields.Float('Precio del vehículo', required=True)
    down_payment = fields.Float('Enganche', compute='_compute_amounts', store=True, readonly=True)
    financed_amount = fields.Float('Monto a financiar', compute='_compute_amounts', store=True, readonly=True)
    monthly_payment = fields.Float('Pago mensual', compute='_compute_amounts', store=True, readonly=True)
    total_interest = fields.Float('Interés total', compute='_compute_amounts', store=True, readonly=True)
    total_payable = fields.Float('Total a pagar', compute='_compute_amounts', store=True, readonly=True)
    status = fields.Selection([
        ('draft', 'Borrador'),
        ('submitted', 'En revisión'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('active', 'Activo'),
        ('paid', 'Pagado'),
    ], 'Estado', default='draft')
    date = fields.Date('Fecha', default=fields.Date.today)
    salesperson_id = fields.Many2one('res.users', 'Vendedor', default=lambda self: self.env.user)
    notes = fields.Text('Notas')
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    @api.depends('vehicle_price', 'plan_id')
    def _compute_amounts(self):
        for req in self:
            if req.plan_id:
                req.down_payment = req.vehicle_price * req.plan_id.down_payment_percent / 100.0
                req.financed_amount = req.vehicle_price - req.down_payment
                monthly_rate = req.plan_id.interest_rate / 100.0 / 12
                n = req.plan_id.months
                if monthly_rate > 0:
                    payment = req.financed_amount * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
                else:
                    payment = req.financed_amount / n
                req.monthly_payment = round(payment, 2)
                req.total_payable = round(payment * n, 2)
                req.total_interest = round(req.total_payable - req.financed_amount, 2)
            else:
                req.down_payment = 0
                req.financed_amount = 0
                req.monthly_payment = 0
                req.total_interest = 0
                req.total_payable = 0

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            self.vehicle_price = self.vehicle_id.sale_price

    def action_submit(self):
        self.status = 'submitted'

    def action_approve(self):
        self.status = 'approved'

    def action_reject(self):
        self.status = 'rejected'

    def action_activate(self):
        self.status = 'active'

    def action_mark_paid(self):
        self.status = 'paid'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                seq = self.env['nexo.sequence'].search([('code', '=', 'FIN')], limit=1)
                if seq:
                    vals['name'] = seq.get_next_code()
        return super().create(vals_list)
