from odoo import models, fields, api


class NexoVehicle(models.Model):
    _name = 'nexo.vehicle'
    _description = 'Vehículo'
    _order = 'id desc'
    _inherit = ['nexo.product']

    vin = fields.Char('VIN / Número de serie', required=True, copy=False)
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
    location = fields.Char('Ubicación / Lote')
    warranty_expiry = fields.Date('Vencimiento de garantía')
    acquisition_date = fields.Date('Fecha de adquisición')
    trade_in_id = fields.Many2one('nexo.vehicle.trade_in', 'Proviene de trade-in', readonly=True, copy=False)
    test_drive_ids = fields.One2many('nexo.vehicle.test.drive', 'vehicle_id', 'Pruebas de manejo')
    history_ids = fields.One2many('nexo.vehicle.history', 'vehicle_id', 'Historial', readonly=True)
    service_order_ids = fields.One2many('nexo.vehicle.service.order', 'vehicle_id', 'Órdenes de servicio')
    image_ids = fields.One2many('nexo.vehicle.image', 'vehicle_id', 'Galería de imágenes')
    sale_count = fields.Integer('Ventas', compute='_compute_counts', store=True)
    service_count = fields.Integer('Servicios', compute='_compute_counts', store=True)

    _sql_constraints = [
        ('vin_unique', 'unique(vin)', 'El VIN ya existe en el sistema'),
    ]

    @api.depends('sale_count', 'service_count')
    def _compute_counts(self):
        for v in self:
            v.sale_count = self.env['nexo.sale.order'].search_count([('vehicle_id', '=', v.id)])
            v.service_count = self.env['nexo.vehicle.service.order'].search_count([('vehicle_id', '=', v.id)])

    @api.onchange('brand_id')
    def _onchange_brand_id(self):
        self.model_id = False

    def _get_owner(self):
        sale = self.env['nexo.sale.order'].search([('vehicle_id', '=', self.id)], limit=1)
        return sale.partner_id if sale else False
