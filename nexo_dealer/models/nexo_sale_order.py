from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    quotation = fields.Boolean('Es cotización', default=False, copy=False)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehículo', ondelete='restrict')
    vehicle_vin = fields.Char(related='vehicle_id.vin_sn', string='VIN', store=False)
    salesperson_id = fields.Many2one('res.users', 'Vendedor', default=lambda self: self.env.user)
    payment_method = fields.Selection([
        ('cash', 'Contado'),
        ('finance', 'Financiación'),
        ('trade_in', 'Trade-in'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
    ], 'Método de pago', default='cash')
    delivery_date = fields.Date('Fecha de entrega')
    validity_days = fields.Integer('Días de validez', default=15)

    def action_quote_to_order(self):
        for order in self:
            order.quotation = False

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            if order.vehicle_id:
                order.vehicle_id.vehicle_status = 'sold'
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehículo', ondelete='restrict')
    vehicle_vin = fields.Char(related='vehicle_id.vin_sn', string='VIN', store=False)
