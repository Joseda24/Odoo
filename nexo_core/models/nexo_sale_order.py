from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    validity_days = fields.Integer('Días de validez', default=15)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
