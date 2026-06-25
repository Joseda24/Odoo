from odoo import models, fields, api


class NexoVehicle(models.Model):
    _name = 'nexo.vehicle'
    _description = 'Vehículo'
    _order = 'id desc'
    _inherit = ['nexo.product']

    vin = fields.Char('VIN / Número de serie', required=True)
    brand_id = fields.Many2one('nexo.vehicle.brand', 'Marca', required=True)
    model_id = fields.Many2one('nexo.vehicle.model', 'Modelo', required=True,
                                domain="[('brand_id', '=', brand_id)]")
    model_year = fields.Integer('Año modelo', required=True)
    color = fields.Char('Color')
    mileage = fields.Float('Kilometraje', default=0.0)
    engine = fields.Char('Motor')
    transmission = fields.Selection([
        ('manual', 'Manual'),
        ('automatic', 'Automática'),
        ('cvt', 'CVT'),
    ], 'Transmisión', default='manual')
    fuel_type = fields.Selection([
        ('gasoline', 'Gasolina'),
        ('diesel', 'Diésel'),
        ('electric', 'Eléctrico'),
        ('hybrid', 'Híbrido'),
    ], 'Combustible', default='gasoline')
    doors = fields.Integer('Puertas', default=4)
    seats = fields.Integer('Asientos', default=5)
    license_plate = fields.Char('Placas')
    vehicle_status = fields.Selection([
        ('available', 'Disponible'),
        ('sold', 'Vendido'),
        ('reserved', 'Reservado'),
        ('in_service', 'En servicio'),
    ], 'Estado', default='available', required=True)

    _sql_constraints = [
        ('vin_unique', 'unique(vin)', 'El VIN ya existe en el sistema'),
    ]

    @api.onchange('brand_id')
    def _onchange_brand_id(self):
        self.model_id = False

    def _get_owner(self):
        """Retorna el cliente propietario del vehículo basado en ventas"""
        sale = self.env['nexo.sale.order'].search([('vehicle_id', '=', self.id)], limit=1)
        return sale.partner_id if sale else False
