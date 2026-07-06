from odoo import models, fields, api


_TAG_MAP = {
    'available': 'En stock',
    'sold': 'Vendido',
    'reserved': 'Reservado',
    'in_service': 'En servicio',
    'to_order': 'A pedir',
}


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    @api.model
    def _ensure_status_tags(self):
        for _status, tag_name in _TAG_MAP.items():
            existing = self.env['fleet.vehicle.tag'].search([('name', '=', tag_name)], limit=1)
            if not existing:
                self.env['fleet.vehicle.tag'].create({'name': tag_name})

    def write(self, vals):
        if 'vehicle_status' in vals:
            new_tag_name = _TAG_MAP.get(vals['vehicle_status'])
            if new_tag_name:
                new_tag = self.env['fleet.vehicle.tag'].search([('name', '=', new_tag_name)], limit=1)
                if new_tag:
                    status_tags = self.env['fleet.vehicle.tag'].search([('name', 'in', list(_TAG_MAP.values()))])
                    status_tag_ids = status_tags.ids
                    old_ids = self.tag_ids.ids
                    tag_ids = [t for t in old_ids if t not in status_tag_ids]
                    if new_tag.id not in tag_ids:
                        tag_ids.append(new_tag.id)
                    vals['tag_ids'] = [(6, 0, tag_ids)]
        return super().write(vals)

    model_year = fields.Integer('Año modelo')
    engine = fields.Char('Motor')
    vehicle_status = fields.Selection([
        ('available', 'Disponible'),
        ('sold', 'Vendido'),
        ('reserved', 'Reservado'),
        ('in_service', 'En servicio'),
        ('to_order', 'A pedir'),
    ], 'Estado', default='available', required=True)
    sale_price = fields.Float('Precio de venta', default=0.0)
    cost_price = fields.Float('Precio de costo', default=0.0)
    location = fields.Char('Ubicación / Lote')
    warranty_expiry = fields.Date('Vencimiento de garantía')
