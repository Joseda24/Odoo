from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    nexo_code = fields.Char('Código Nexo')
