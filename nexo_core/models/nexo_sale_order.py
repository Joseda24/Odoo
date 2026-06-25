from odoo import models, fields, api
from odoo.exceptions import UserError


class NexoSaleOrder(models.Model):
    _name = 'nexo.sale.order'
    _description = 'Pedido de venta'
    _order = 'date_order desc, id desc'

    name = fields.Char('Folio', required=True, copy=False, readonly=True, default='Nuevo')
    partner_id = fields.Many2one('nexo.partner', 'Cliente', required=True)
    date_order = fields.Datetime('Fecha de pedido', default=fields.Datetime.now, required=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('done', 'Entregado'),
        ('cancel', 'Cancelado'),
    ], 'Estado', default='draft', required=True, copy=False)
    line_ids = fields.One2many('nexo.sale.order.line', 'order_id', 'Líneas de pedido')
    amount_subtotal = fields.Float('Subtotal', compute='_compute_amounts', store=True)
    amount_tax = fields.Float('Impuestos', compute='_compute_amounts', store=True)
    amount_total = fields.Float('Total', compute='_compute_amounts', store=True)
    notes = fields.Text('Notas')
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    @api.depends('line_ids.price_subtotal', 'line_ids.tax_amount')
    def _compute_amounts(self):
        for order in self:
            order.amount_subtotal = sum(line.price_subtotal for line in order.line_ids)
            order.amount_tax = sum(line.tax_amount for line in order.line_ids)
            order.amount_total = order.amount_subtotal + order.amount_tax

    def action_confirm(self):
        for order in self:
            if order.state != 'draft':
                raise UserError('Solo pedidos en borrador pueden confirmarse')
            order.state = 'confirmed'

    def action_done(self):
        for order in self:
            if order.state != 'confirmed':
                raise UserError('Solo pedidos confirmados pueden marcarse como entregados')
            order.state = 'done'

    def action_cancel(self):
        for order in self:
            if order.state == 'done':
                raise UserError('No se puede cancelar un pedido entregado')
            order.state = 'cancel'

    def action_draft(self):
        for order in self:
            order.state = 'draft'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                seq = self.env['nexo.sequence'].search([('code', '=', 'SALE')], limit=1)
                if seq:
                    vals['name'] = seq.get_next_code()
        return super().create(vals_list)
