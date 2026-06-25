from odoo import models, fields, api


class NexoProduct(models.Model):
    _name = 'nexo.product'
    _description = 'Producto / Servicio'
    _order = 'name'

    name = fields.Char('Nombre', required=True)
    code = fields.Char('Código interno')
    barcode = fields.Char('Código de barras')
    description = fields.Text('Descripción')
    sale_price = fields.Float('Precio de venta', default=0.0, required=True)
    cost_price = fields.Float('Precio de costo', default=0.0)
    type = fields.Selection([
        ('product', 'Almacenable'),
        ('consu', 'Consumible'),
        ('service', 'Servicio'),
    ], 'Tipo de producto', default='product', required=True)
    category_id = fields.Many2one('nexo.product.category', 'Categoría')
    uom_id = fields.Many2one('uom.uom', 'Unidad de medida',
                             default=lambda self: self.env.ref('uom.product_uom_unit'))
    active = fields.Boolean('Activo', default=True)
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    _sql_constraints = [
        ('code_unique', 'unique(code, company_id)', 'El código interno debe ser único por compañía'),
    ]
