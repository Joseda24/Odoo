from odoo import models, fields, api


class NexoVehicleTestDrive(models.Model):
    _name = 'nexo.vehicle.test.drive'
    _description = 'Prueba de manejo'
    _order = 'date_hour desc, id desc'

    name = fields.Char('Folio', required=True, copy=False, readonly=True, default='Nuevo')
    vehicle_id = fields.Many2one('nexo.vehicle', 'Vehículo', required=True)
    partner_id = fields.Many2one('nexo.partner', 'Cliente', required=True)
    salesperson_id = fields.Many2one('res.users', 'Vendedor', default=lambda self: self.env.user)
    date_hour = fields.Datetime('Fecha y hora', default=fields.Datetime.now, required=True)
    duration = fields.Float('Duración (horas)', default=1.0)
    notes = fields.Text('Notas / resultado')
    state = fields.Selection([
        ('scheduled', 'Programada'),
        ('done', 'Realizada'),
        ('cancelled', 'Cancelada'),
    ], 'Estado', default='scheduled', required=True)
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    def action_done(self):
        for rec in self:
            rec.state = 'done'
            self.env['nexo.vehicle.history'].log(
                vehicle_id=rec.vehicle_id.id,
                type='test_drive',
                description=f'Prueba de manejo con {rec.partner_id.name}',
                partner_id=rec.partner_id.id,
                reference=rec.name,
            )

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                seq = self.env['nexo.sequence'].search([('code', '=', 'TD')], limit=1)
                if seq:
                    vals['name'] = seq.get_next_code()
        return super().create(vals_list)
