from odoo import models, fields, api


class NexoPurchaseOrder(models.Model):
    _inherit = 'nexo.purchase.order'

    vehicle_reception_ids = fields.One2many('nexo.vehicle.inventory', 'purchase_order_id', 'Recepciones')

    def action_receive(self):
        res = super().action_receive()
        for order in self:
            for line in order.line_ids:
                if line.vehicle_id:
                    self.env['nexo.vehicle.inventory'].create({
                        'purchase_order_id': order.id,
                        'vehicle_id': line.vehicle_id.id,
                        'quantity': line.quantity,
                        'cost': line.price_unit,
                        'partner_id': order.partner_id.id,
                    })
        return res


class NexoPurchaseOrderLine(models.Model):
    _inherit = 'nexo.purchase.order.line'

    vehicle_id = fields.Many2one('nexo.vehicle', 'Vehículo', ondelete='restrict')

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            self.product_id = self.vehicle_id.product_id
            self.description = self.vehicle_id.name
            self.price_unit = self.vehicle_id.cost_price


class NexoPurchaseRequest(models.Model):
    _name = 'nexo.purchase.request'
    _description = 'Solicitud de cotización / RFQ'
    _order = 'date desc, id desc'

    name = fields.Char('Folio', required=True, copy=False, readonly=True, default='Nuevo')
    partner_id = fields.Many2one('nexo.partner', 'Proveedor')
    date = fields.Date('Fecha', default=fields.Date.today, required=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('sent', 'Enviado'),
        ('received', 'Respuesta recibida'),
        ('ordered', 'Ordenado'),
        ('cancel', 'Cancelado'),
    ], 'Estado', default='draft')
    line_ids = fields.One2many('nexo.purchase.request.line', 'request_id', 'Líneas')
    notes = fields.Text('Notas')
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                seq = self.env['nexo.sequence'].search([('code', '=', 'RFQ')], limit=1)
                if seq:
                    vals['name'] = seq.get_next_code()
        return super().create(vals_list)

    def action_send(self):
        self.state = 'sent'

    def action_receive(self):
        self.state = 'received'

    def action_create_order(self):
        self.ensure_one()
        order = self.env['nexo.purchase.order'].create({
            'partner_id': self.partner_id.id,
            'notes': self.notes,
        })
        for line in self.line_ids:
            self.env['nexo.purchase.order.line'].create({
                'order_id': order.id,
                'product_id': line.product_id.id,
                'vehicle_id': line.vehicle_id.id,
                'description': line.description,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
            })
        self.state = 'ordered'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'nexo.purchase.order',
            'res_id': order.id,
            'view_mode': 'form',
        }


class NexoPurchaseRequestLine(models.Model):
    _name = 'nexo.purchase.request.line'
    _description = 'Línea de RFQ'

    request_id = fields.Many2one('nexo.purchase.request', 'RFQ', required=True, ondelete='cascade')
    product_id = fields.Many2one('nexo.product', 'Producto')
    vehicle_id = fields.Many2one('nexo.vehicle', 'Vehículo')
    description = fields.Char('Descripción')
    quantity = fields.Float('Cantidad', default=1.0, required=True)
    price_unit = fields.Float('Precio estimado')
    company_id = fields.Many2one(related='request_id.company_id', store=True)
