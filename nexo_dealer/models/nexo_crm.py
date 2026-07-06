from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    source = fields.Selection(selection=[
        ('website', 'Sitio web'),
        ('referral', 'Referido'),
        ('phone', 'Llamada'),
        ('walkin', 'Mostrador'),
        ('social', 'Redes sociales'),
        ('email_marketing', 'Email marketing'),
        ('other', 'Otro'),
    ])
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehículo de interés')

    def action_convert_to_sale(self):
        res = super().action_convert_to_sale()
        if res and self.vehicle_id:
            order = self.env['sale.order'].browse(res.get('res_id'))
            if order:
                order.vehicle_id = self.vehicle_id.id
        return res
