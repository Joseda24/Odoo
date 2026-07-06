from odoo import models, fields, api


class NexoVehicleInventory(models.Model):
    _name = 'nexo.vehicle.inventory'
    _description = 'Inventario de vehículos'
    _order = 'date_in desc, id desc'

    name = fields.Char('Folio', required=True, copy=False, readonly=True, default='Nuevo')
    date_in = fields.Date('Fecha de ingreso', default=fields.Date.today, required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehículo', required=True, ondelete='restrict')
    type = fields.Selection([
        ('purchase', 'Compra'),
        ('consignment', 'Consignación'),
        ('transfer', 'Transferencia'),
        ('return', 'Devolución'),
        ('trade_in', 'Trade-in'),
    ], 'Tipo de ingreso', default='purchase', required=True)
    cost = fields.Float('Costo de adquisición', required=True)
    supplier_id = fields.Many2one('res.partner', 'Proveedor / Origen')
    purchase_order_id = fields.Many2one('purchase.order', 'Orden de compra')
    notes = fields.Text('Notas')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Registrado'),
        ('cancel', 'Cancelado'),
    ], 'Estado', default='draft', required=True)
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    def action_done(self):
        for rec in self:
            rec.state = 'done'
            rec.vehicle_id.vehicle_status = 'available'
            rec.vehicle_id.acquisition_date = rec.date_in
            rec.vehicle_id.cost_price = rec.cost

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                seq = self.env['nexo.sequence'].search([('code', '=', 'MOV')], limit=1)
                if seq:
                    vals['name'] = seq.get_next_code()
        return super().create(vals_list)
