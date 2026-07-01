from odoo import models, fields


class NexoVehicleImage(models.Model):
    _name = 'nexo.vehicle.image'
    _description = 'Imagen del vehículo'
    _order = 'sequence, id'

    vehicle_id = fields.Many2one('nexo.vehicle', 'Vehículo', required=True, ondelete='cascade')
    name = fields.Char('Nombre')
    image = fields.Binary('Imagen', required=True)
    sequence = fields.Integer('Orden', default=10)
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)
