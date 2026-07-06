from odoo import models, fields


class FleetVehicleModel(models.Model):
    _inherit = 'fleet.vehicle.model'

    year_from = fields.Integer('Año desde')
    year_to = fields.Integer('Año hasta')
    vehicle_type = fields.Selection(selection_add=[
        ('sedan', 'Sedán'),
        ('suv', 'SUV'),
        ('hatchback', 'Hatchback'),
        ('pickup', 'Pickup'),
        ('coupe', 'Coupé'),
        ('convertible', 'Convertible'),
        ('van', 'Van'),
        ('motorcycle', 'Motocicleta'),
        ('other', 'Otro'),
    ], ondelete={'sedan': 'set default', 'suv': 'cascade', 'hatchback': 'cascade', 'pickup': 'cascade', 'coupe': 'cascade', 'convertible': 'cascade', 'van': 'cascade', 'motorcycle': 'cascade', 'other': 'cascade'}, string='Tipo', default='sedan')
