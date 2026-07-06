from odoo import models, fields


class FleetVehicleLogService(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    reference = fields.Char('Referencia')
    partner_id = fields.Many2one('res.partner', 'Relacionado con')
