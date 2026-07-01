from odoo import models, fields, api


class NexoSaleOrder(models.Model):
    _inherit = ['nexo.sale.order']

    quotation = fields.Boolean('Es cotización', default=False, copy=False)
    vehicle_id = fields.Many2one('nexo.vehicle', 'Vehículo', ondelete='restrict')
    vehicle_vin = fields.Char(related='vehicle_id.vin', string='VIN', store=False)
    salesperson_id = fields.Many2one('res.users', 'Vendedor', default=lambda self: self.env.user)
    payment_method = fields.Selection([
        ('cash', 'Contado'),
        ('finance', 'Financiamiento'),
        ('trade_in', 'Trade-in'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
    ], 'Método de pago', default='cash')
    delivery_date = fields.Date('Fecha de entrega')
    trade_in_ids = fields.One2many('nexo.vehicle.trade_in', 'sale_order_id', 'Trade-ins')
    validity_days = fields.Integer('Días de validez', default=15)

    def action_quote_to_order(self):
        for order in self:
            order.quotation = False

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            if order.vehicle_id:
                order.vehicle_id.vehicle_status = 'sold'
                self.env['nexo.vehicle.history'].log(
                    vehicle_id=order.vehicle_id.id,
                    type='sale',
                    description=f'Vendido a {order.partner_id.name}',
                    cost=order.amount_total,
                    partner_id=order.partner_id.id,
                    reference=order.name,
                )
        return res


class NexoSaleOrderLine(models.Model):
    _inherit = ['nexo.sale.order.line']

    vehicle_id = fields.Many2one('nexo.vehicle', 'Vehículo', ondelete='restrict')
    vehicle_vin = fields.Char(related='vehicle_id.vin', string='VIN', store=False)
