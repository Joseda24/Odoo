from odoo import models, fields


class FleetVehicleModelBrand(models.Model):
    _inherit = 'fleet.vehicle.model.brand'

    description = fields.Text('Descripción')
    logo = fields.Binary('Logo')
