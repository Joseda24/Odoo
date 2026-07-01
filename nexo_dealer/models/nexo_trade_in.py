from odoo import models, fields, api


class NexoVehicleTradeIn(models.Model):
    _name = 'nexo.vehicle.trade_in'
    _description = 'Trade-in / Vehículo recibido como parte de pago'
    _order = 'date desc, id desc'

    name = fields.Char('Folio', required=True, copy=False, readonly=True, default='Nuevo')
    date = fields.Date('Fecha', default=fields.Date.today, required=True)
    incoming_vehicle_id = fields.Many2one('nexo.vehicle', 'Vehículo recibido', required=True,
                                          domain="[('vehicle_status', '=', 'available')]")
    sale_order_id = fields.Many2one('nexo.sale.order', 'Venta asociada')
    partner_id = fields.Many2one('nexo.partner', 'Cliente', required=True)
    agreed_value = fields.Float('Valor acordado', required=True)
    market_value = fields.Float('Valor de mercado')
    condition = fields.Selection([
        ('excellent', 'Excelente'),
        ('good', 'Bueno'),
        ('fair', 'Regular'),
        ('poor', 'Malo'),
    ], 'Condición', default='good')
    notes = fields.Text('Notas / evaluación')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Concretado'),
        ('cancel', 'Cancelado'),
    ], 'Estado', default='draft', required=True)
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                seq = self.env['nexo.sequence'].search([('code', '=', 'TRADE')], limit=1)
                if seq:
                    vals['name'] = seq.get_next_code()
        return super().create(vals_list)
