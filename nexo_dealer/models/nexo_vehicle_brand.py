from odoo import models, fields


class NexoVehicleBrand(models.Model):
    _name = 'nexo.vehicle.brand'
    _description = 'Marca de vehículo'
    _order = 'name'

    name = fields.Char('Marca', required=True)
    description = fields.Text('Descripción')
    logo = fields.Binary('Logo')
    active = fields.Boolean('Activo', default=True)
    model_ids = fields.One2many('nexo.vehicle.model', 'brand_id', 'Modelos')
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)
