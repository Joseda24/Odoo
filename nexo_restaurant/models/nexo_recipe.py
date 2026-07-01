from odoo import models, fields, api


class NexoRecipeLine(models.Model):
    _name = 'nexo.recipe.line'
    _description = 'Línea de receta'

    menu_item_id = fields.Many2one('nexo.menu.item', 'Artículo', required=True, ondelete='cascade')
    ingredient_id = fields.Many2one('nexo.ingredient', 'Ingrediente', required=True)
    quantity = fields.Float('Cantidad', required=True, default=1.0)
    unit = fields.Selection(related='ingredient_id.unit', store=True)
    company_id = fields.Many2one(related='menu_item_id.company_id', store=True)
