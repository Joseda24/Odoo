from odoo import models, fields


class NexoVehicleModel(models.Model):
    _name = 'nexo.vehicle.model'
    _description = 'Modelo de vehículo'
    _order = 'brand_id, name'

    name = fields.Char('Modelo', required=True)
    brand_id = fields.Many2one('nexo.vehicle.brand', 'Marca', required=True)
    year_from = fields.Integer('Año desde')
    year_to = fields.Integer('Año hasta')
    vehicle_type = fields.Selection([
        ('sedan', 'Sedán'),
        ('suv', 'SUV'),
        ('hatchback', 'Hatchback'),
        ('pickup', 'Pickup'),
        ('coupe', 'Coupé'),
        ('convertible', 'Convertible'),
        ('van', 'Van'),
        ('motorcycle', 'Motocicleta'),
        ('other', 'Otro'),
    ], 'Tipo', default='sedan')
    active = fields.Boolean('Activo', default=True)
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)
