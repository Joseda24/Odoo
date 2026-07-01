from odoo import models, fields, api
from odoo.exceptions import UserError


class NexoIngredientCategory(models.Model):
    _name = 'nexo.ingredient.category'
    _description = 'Categoría de ingrediente'

    name = fields.Char('Nombre', required=True)
    ingredient_ids = fields.One2many('nexo.ingredient', 'category_id', 'Ingredientes')
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)


class NexoIngredient(models.Model):
    _name = 'nexo.ingredient'
    _description = 'Ingrediente / insumo'
    _order = 'name'

    name = fields.Char('Nombre', required=True)
    category_id = fields.Many2one('nexo.ingredient.category', 'Categoría')
    stock_qty = fields.Float('Stock actual', default=0.0, required=True)
    unit = fields.Selection([
        ('kg', 'Kg'),
        ('g', 'Gramos'),
        ('l', 'Litros'),
        ('ml', 'Mililitros'),
        ('pz', 'Piezas'),
        ('un', 'Unidades'),
    ], 'Unidad', default='un', required=True)
    min_stock = fields.Float('Stock mínimo', default=10.0)
    cost_unit = fields.Float('Costo unitario', default=0.0)
    recipe_line_ids = fields.One2many('nexo.recipe.line', 'ingredient_id', 'Usado en recetas')
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    @api.depends('recipe_line_ids.ingredient_id')
    def _compute_used_in(self):
        for rec in self:
            rec.used_in_count = len(rec.recipe_line_ids)


class NexoStockMove(models.Model):
    _name = 'nexo.stock.move'
    _description = 'Movimiento de stock'

    ingredient_id = fields.Many2one('nexo.ingredient', 'Ingrediente', required=True)
    type = fields.Selection([
        ('in', 'Entrada'),
        ('out', 'Salida'),
        ('adjust', 'Ajuste'),
    ], 'Tipo', required=True)
    quantity = fields.Float('Cantidad', required=True)
    unit = fields.Selection(related='ingredient_id.unit', store=True)
    reference = fields.Char('Referencia')
    date = fields.Datetime('Fecha', default=fields.Datetime.now, required=True)
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        for move in moves:
            ing = move.ingredient_id
            if move.type == 'in':
                ing.stock_qty += move.quantity
            elif move.type == 'out':
                if ing.stock_qty < move.quantity:
                    raise UserError(f'Stock insuficiente de {ing.name}')
                ing.stock_qty -= move.quantity
            else:
                ing.stock_qty = move.quantity
        return moves
