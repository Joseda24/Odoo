from odoo import models, fields, api
from odoo.exceptions import UserError


class NexoVehicleServiceOrder(models.Model):
    _name = 'nexo.vehicle.service.order'
    _description = 'Orden de servicio / reparación'
    _order = 'date_in desc, id desc'

    name = fields.Char('Folio', required=True, copy=False, readonly=True, default='Nuevo')
    vehicle_id = fields.Many2one('nexo.vehicle', 'Vehículo', required=True)
    partner_id = fields.Many2one('nexo.partner', 'Cliente', required=True)
    date_in = fields.Datetime('Fecha de ingreso', default=fields.Datetime.now, required=True)
    date_out = fields.Datetime('Fecha de salida')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('in_progress', 'En proceso'),
        ('done', 'Finalizado'),
        ('invoiced', 'Facturado'),
        ('cancel', 'Cancelado'),
    ], 'Estado', default='draft', required=True)
    mechanic_id = fields.Many2one('res.users', 'Mecánico asignado')
    line_ids = fields.One2many('nexo.vehicle.service.line', 'order_id', 'Líneas de servicio')
    amount_subtotal = fields.Float('Subtotal', compute='_compute_amounts', store=True)
    amount_tax = fields.Float('Impuestos', compute='_compute_amounts', store=True)
    amount_total = fields.Float('Total', compute='_compute_amounts', store=True)
    notes = fields.Text('Notas / diagnóstico')
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    @api.depends('line_ids.price_subtotal', 'line_ids.tax_amount')
    def _compute_amounts(self):
        for order in self:
            order.amount_subtotal = sum(l.price_subtotal for l in order.line_ids)
            order.amount_tax = sum(l.tax_amount for l in order.line_ids)
            order.amount_total = order.amount_subtotal + order.amount_tax

    def action_start(self):
        for order in self:
            if order.state != 'draft':
                raise UserError('Solo órdenes en borrador pueden iniciarse')
            order.state = 'in_progress'

    def action_done(self):
        for order in self:
            if order.state != 'in_progress':
                raise UserError('Solo órdenes en progreso pueden finalizarse')
            order.date_out = fields.Datetime.now()
            order.state = 'done'

    def action_invoice(self):
        for order in self:
            if order.state != 'done':
                raise UserError('Solo órdenes finalizadas pueden facturarse')
            order.state = 'invoiced'

    def action_cancel(self):
        for order in self:
            if order.state == 'invoiced':
                raise UserError('No se puede cancelar una orden facturada')
            order.state = 'cancel'

    @api.onchange('vehicle_id')
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                seq = self.env['nexo.sequence'].search([('code', '=', 'SRV')], limit=1)
                if seq:
                    vals['name'] = seq.get_next_code()
        return super().create(vals_list)


class NexoVehicleServiceLine(models.Model):
    _name = 'nexo.vehicle.service.line'
    _description = 'Línea de orden de servicio'

    order_id = fields.Many2one('nexo.vehicle.service.order', 'Orden', required=True, ondelete='cascade')
    type = fields.Selection([
        ('labor', 'Mano de obra'),
        ('part', 'Refacción'),
        ('service', 'Servicio externo'),
    ], 'Tipo', default='labor', required=True)
    description = fields.Char('Descripción', required=True)
    product_id = fields.Many2one('nexo.product', 'Producto')
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
