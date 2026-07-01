from odoo import models, fields, api


class NexoMenuCategory(models.Model):
    _name = 'nexo.menu.category'
    _description = 'Categoría de carta'
    _order = 'sequence, name'

    name = fields.Char('Nombre', required=True, translate=True)
    sequence = fields.Integer('Secuencia', default=10)
    description = fields.Text('Descripción', translate=True)
    item_ids = fields.One2many('nexo.menu.item', 'category_id', 'Artículos')
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)


class NexoMenuItem(models.Model):
    _name = 'nexo.menu.item'
    _description = 'Artículo de carta'
    _order = 'category_id, name'

    name = fields.Char('Nombre', required=True, translate=True)
    description = fields.Text('Descripción', translate=True)
    category_id = fields.Many2one('nexo.menu.category', 'Categoría', required=True)
    price = fields.Float('Precio', required=True, default=0.0)
    cost = fields.Float('Costo estimado', default=0.0)
    image = fields.Binary('Imagen')
    available = fields.Boolean('Disponible', default=True)
    preparation_time = fields.Integer('Tiempo preparación (min)', default=15)
    recipe_line_ids = fields.One2many('nexo.recipe.line', 'menu_item_id', 'Receta')
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)
