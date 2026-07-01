from odoo import models, fields, api


class NexoVehicleHistory(models.Model):
    _name = 'nexo.vehicle.history'
    _description = 'Historial del vehículo'
    _order = 'date desc, id desc'

    vehicle_id = fields.Many2one('nexo.vehicle', 'Vehículo', required=True, ondelete='cascade')
    date = fields.Datetime('Fecha', default=fields.Datetime.now, required=True)
    type = fields.Selection([
        ('acquisition', 'Adquisición'),
        ('sale', 'Venta'),
        ('service', 'Servicio'),
        ('test_drive', 'Prueba de manejo'),
        ('transfer', 'Transferencia'),
        ('note', 'Nota general'),
    ], 'Tipo', required=True)
    description = fields.Char('Descripción', required=True)
    cost = fields.Float('Costo / Monto')
    odometer = fields.Float('Kilometraje')
    partner_id = fields.Many2one('nexo.partner', 'Relacionado con')
    reference = fields.Char('Referencia / Documento')
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    @api.model
    def log(self, vehicle_id, type, description, cost=0, odometer=0, partner_id=False, reference=False):
        return self.create({
            'vehicle_id': vehicle_id,
            'type': type,
            'description': description,
            'cost': cost,
            'odometer': odometer,
            'partner_id': partner_id,
            'reference': reference,
        })
