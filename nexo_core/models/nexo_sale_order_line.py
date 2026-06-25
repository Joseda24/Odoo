from odoo import models, fields, api


class NexoSaleOrderLine(models.Model):
    _name = 'nexo.sale.order.line'
    _description = 'Línea de pedido de venta'
    _order = 'order_id, id'

    order_id = fields.Many2one('nexo.sale.order', 'Pedido', required=True, ondelete='cascade')
    product_id = fields.Many2one('nexo.product', 'Producto', required=True)
    description = fields.Char('Descripción')
    quantity = fields.Float('Cantidad', default=1.0, required=True)
    price_unit = fields.Float('Precio unitario', default=0.0, required=True)
    tax_percent = fields.Float('Impuesto %', default=0.0)
    price_subtotal = fields.Float('Subtotal', compute='_compute_line_amounts', store=True)
    tax_amount = fields.Float('Importe impuesto', compute='_compute_line_amounts', store=True)
    price_total = fields.Float('Total', compute='_compute_line_amounts', store=True)
    company_id = fields.Many2one(related='order_id.company_id', store=True)

    @api.depends('quantity', 'price_unit', 'tax_percent')
    def _compute_line_amounts(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
            line.tax_amount = line.price_subtotal * (line.tax_percent / 100.0)
            line.price_total = line.price_subtotal + line.tax_amount

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name
            self.price_unit = self.product_id.sale_price
