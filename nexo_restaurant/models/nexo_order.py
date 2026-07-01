from odoo import models, fields, api


class NexoRestaurantOrder(models.Model):
    _name = 'nexo.restaurant.order'
    _description = 'Pedido de restaurante'
    _order = 'id desc'

    name = fields.Char('Folio', required=True, copy=False, readonly=True, default='Nuevo')
    table_id = fields.Many2one('nexo.restaurant.table', 'Mesa', required=True)
    waiter_id = fields.Many2one('res.users', 'Mesero', default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('in_progress', 'En preparación'),
        ('done', 'Servido'),
        ('paid', 'Pagado'),
        ('cancel', 'Cancelado'),
    ], 'Estado', default='draft', required=True)
    line_ids = fields.One2many('nexo.restaurant.order.line', 'order_id', 'Líneas')
    payment_ids = fields.One2many('nexo.restaurant.payment', 'order_id', 'Pagos')
    amount_subtotal = fields.Float('Subtotal', compute='_compute_amounts', store=True)
    amount_tax = fields.Float('Impuestos', compute='_compute_amounts', store=True)
    amount_total = fields.Float('Total', compute='_compute_amounts', store=True)
    amount_paid = fields.Float('Pagado', compute='_compute_paid', store=True)
    amount_due = fields.Float('Pendiente', compute='_compute_amounts', store=True)
    notes = fields.Text('Notas')
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    @api.depends('line_ids.price_subtotal', 'line_ids.tax_amount')
    def _compute_amounts(self):
        for order in self:
            order.amount_subtotal = sum(l.price_subtotal for l in order.line_ids)
            order.amount_tax = sum(l.tax_amount for l in order.line_ids)
            order.amount_total = order.amount_subtotal + order.amount_tax
            order.amount_due = order.amount_total - order.amount_paid

    @api.depends('payment_ids.amount')
    def _compute_paid(self):
        for order in self:
            order.amount_paid = sum(p.amount for p in order.payment_ids)

    def action_confirm(self):
        for order in self:
            order.state = 'in_progress'

    def action_done(self):
        for order in self:
            order.state = 'done'

    def action_paid(self):
        for order in self:
            order.state = 'paid'


    def action_open_tpv(self):
        self.ensure_one()
        if self.state == 'draft':
            self.state = 'in_progress'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'nexo.restaurant.order',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_send_to_kitchen(self):
        for order in self:
            order.line_ids.filtered(lambda l: l.state == 'pending').write({'state': 'cooking'})

    def action_serve(self):
        for order in self:
            order.line_ids.filtered(lambda l: l.state == 'cooking').write({'state': 'served'})
            order.state = 'done'

    def add_menu_item(self, item_id):
        item = self.env['nexo.menu.item'].browse(item_id)
        if not item:
            return
        self.write({
            'line_ids': [(0, 0, {
                'menu_item_id': item.id,
                'quantity': 1,
                'price_unit': item.price,
            })]
        })

    def action_cancel(self):
        for order in self:
            order.state = 'cancel'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                seq = self.env['nexo.sequence'].search([('code', '=', 'ORD')], limit=1)
                if seq:
                    vals['name'] = seq.get_next_code()
        return super().create(vals_list)


class NexoRestaurantOrderLine(models.Model):
    _name = 'nexo.restaurant.order.line'
    _description = 'Línea de pedido'

    order_id = fields.Many2one('nexo.restaurant.order', 'Pedido', required=True, ondelete='cascade')
    menu_item_id = fields.Many2one('nexo.menu.item', 'Artículo', required=True)
    quantity = fields.Float('Cantidad', default=1.0, required=True)
    price_unit = fields.Float('Precio unit.', required=True)
    tax_percent = fields.Float('Impuesto %', default=16.0)
    price_subtotal = fields.Float('Subtotal', compute='_compute_amounts', store=True)
    tax_amount = fields.Float('Impuesto', compute='_compute_amounts', store=True)
    price_total = fields.Float('Total', compute='_compute_amounts', store=True)
    notes = fields.Char('Notas')
    state = fields.Selection([
        ('pending', 'Pendiente'),
        ('cooking', 'Cocinando'),
        ('served', 'Servido'),
        ('cancel', 'Cancelado'),
    ], 'Estado', default='pending')
    company_id = fields.Many2one(related='order_id.company_id', store=True)

    @api.depends('quantity', 'price_unit', 'tax_percent')
    def _compute_amounts(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
            line.tax_amount = line.price_subtotal * (line.tax_percent / 100.0)
            line.price_total = line.price_subtotal + line.tax_amount

    @api.onchange('menu_item_id')
    def _onchange_menu_item_id(self):
        if self.menu_item_id:
            self.price_unit = self.menu_item_id.price


class NexoRestaurantPayment(models.Model):
    _name = 'nexo.restaurant.payment'
    _description = 'Pago de pedido'

    order_id = fields.Many2one('nexo.restaurant.order', 'Pedido', required=True, ondelete='cascade')
    amount = fields.Float('Monto', required=True)
    method = fields.Selection([
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
        ('other', 'Otro'),
    ], 'Método', default='cash', required=True)
    reference = fields.Char('Referencia')
    payment_date = fields.Datetime('Fecha', default=fields.Datetime.now)
    company_id = fields.Many2one(related='order_id.company_id', store=True)
