from odoo import models, fields, api


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    odometer_in = fields.Float('Kilometraje ingreso')
    odometer_out = fields.Float('Kilometraje salida')
    priority = fields.Selection(selection_add=[
        ('low', 'Baja'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ], string='Prioridad', default='normal')

    def action_done(self):
        res = super().action_done()
        for order in self:
            if order.vehicle_id:
                order.vehicle_id.vehicle_status = 'available'
        return res


