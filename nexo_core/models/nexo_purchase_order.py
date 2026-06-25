from odoo import models, fields, api
from odoo.exceptions import UserError


class NexoPurchaseOrder(models.Model):
    _name = 'nexo.purchase.order'
    _description = 'Orden de compra'
    _order = 'date_order desc, id desc'

    name = fields.Char('Folio', required=True, copy=False, readonly=True, default='Nuevo')
    partner_id = fields.Many2one('nexo.partner', 'Proveedor', required=True)
    date_order = fields.Datetime('Fecha de orden', default=fields.Datetime.now, required=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('received', 'Recibido'),
        ('cancel', 'Cancelado'),
    ], 'Estado', default='draft', required=True, copy=False)
    line_ids = fields.One2many('nexo.purchase.order.line', 'order_id', 'Líneas')
    amount_total = fields.Float('Total', compute='_compute_amount_total', store=True)
    notes = fields.Text('Notas')
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    @api.depends('line_ids.price_total')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(line.price_total for line in order.line_ids)

    def action_confirm(self):
        for order in self:
            order.state = 'confirmed'

    def action_receive(self):
        for order in self:
            order.state = 'received'

    def action_cancel(self):
        for order in self:
            if order.state == 'received':
                raise UserError('No se puede cancelar una orden ya recibida')
            order.state = 'cancel'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                seq = self.env['nexo.sequence'].search([('code', '=', 'PURCHASE')], limit=1)
                if seq:
                    vals['name'] = seq.get_next_code()
        return super().create(vals_list)


class NexoPurchaseOrderLine(models.Model):
    _name = 'nexo.purchase.order.line'
    _description = 'Línea de orden de compra'

    order_id = fields.Many2one('nexo.purchase.order', 'Orden', required=True, ondelete='cascade')
    product_id = fields.Many2one('nexo.product', 'Producto', required=True)
    description = fields.Char('Descripción')
    quantity = fields.Float('Cantidad', default=1.0, required=True)
    price_unit = fields.Float('Precio unitario', default=0.0, required=True)
    price_total = fields.Float('Total', compute='_compute_total', store=True)
    company_id = fields.Many2one(related='order_id.company_id', store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_total(self):
        for line in self:
            line.price_total = line.quantity * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name
            self.price_unit = self.product_id.cost_price
