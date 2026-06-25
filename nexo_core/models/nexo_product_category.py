from odoo import models, fields


class NexoProductCategory(models.Model):
    _name = 'nexo.product.category'
    _description = 'Categoría de producto'
    _order = 'name'

    name = fields.Char('Nombre', required=True)
    parent_id = fields.Many2one('nexo.product.category', 'Categoría padre')
    child_ids = fields.One2many('nexo.product.category', 'parent_id', 'Subcategorías')
    description = fields.Text('Descripción')
    active = fields.Boolean('Activo', default=True)
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)
