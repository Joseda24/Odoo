from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
