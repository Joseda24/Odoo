from odoo import models, fields, api


class NexoSaleOrder(models.Model):
    _inherit = ['nexo.sale.order']

    vehicle_id = fields.Many2one('nexo.vehicle', 'Vehículo', ondelete='restrict')
    vehicle_brand_id = fields.Many2one(related='vehicle_id.brand_id', string='Marca', store=False)
    vehicle_model_id = fields.Many2one(related='vehicle_id.model_id', string='Modelo', store=False)
    vehicle_vin = fields.Char(related='vehicle_id.vin', string='VIN', store=False)

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            if order.vehicle_id:
                order.vehicle_id.vehicle_status = 'sold'
        return res


class NexoSaleOrderLine(models.Model):
    _inherit = ['nexo.sale.order.line']

    vehicle_id = fields.Many2one('nexo.vehicle', 'Vehículo', ondelete='restrict')
    vehicle_vin = fields.Char(related='vehicle_id.vin', string='VIN', store=False)
