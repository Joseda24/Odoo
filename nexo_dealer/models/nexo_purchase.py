from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    vehicle_reception_ids = fields.One2many('nexo.vehicle.inventory', 'purchase_order_id', 'Recepciones')

    def action_receive(self):
        self.ensure_one()
        for line in self.order_line:
            if line.vehicle_id:
                self.env['nexo.vehicle.inventory'].create({
                    'purchase_order_id': self.id,
                    'vehicle_id': line.vehicle_id.id,
                    'cost': line.price_unit,
                    'supplier_id': self.partner_id.id,
                })
        return True


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehículo', ondelete='restrict')

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            self.name = self.vehicle_id.display_name
            self.price_unit = self.vehicle_id.cost_price


class NexoPurchaseRequest(models.Model):
    _name = 'nexo.purchase.request'
    _description = 'Solicitud de cotización / RFQ'
    _order = 'date desc, id desc'

    name = fields.Char('Folio', required=True, copy=False, readonly=True, default='Nuevo')
    partner_id = fields.Many2one('res.partner', 'Proveedor')
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
        self.write({'state': 'sent'})

    def action_receive(self):
        self.write({'state': 'received'})

    def action_create_order(self):
        self.ensure_one()
        order = self.env['purchase.order'].create({
            'partner_id': self.partner_id.id,
            'notes': self.notes,
        })
        for line in self.line_ids:
            self.env['purchase.order.line'].create({
                'order_id': order.id,
                'product_id': line.product_id.id,
                'vehicle_id': line.vehicle_id.id,
                'name': line.description,
                'product_qty': line.quantity,
                'price_unit': line.price_unit,
            })
        self.state = 'ordered'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': order.id,
            'view_mode': 'form',
        }


class NexoPurchaseRequestLine(models.Model):
    _name = 'nexo.purchase.request.line'
    _description = 'Línea de RFQ'

    request_id = fields.Many2one('nexo.purchase.request', 'RFQ', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Producto')
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehículo')
    description = fields.Char('Descripción')
    quantity = fields.Float('Cantidad', default=1.0, required=True)
    price_unit = fields.Float('Precio estimado')
    company_id = fields.Many2one(related='request_id.company_id', store=True)
