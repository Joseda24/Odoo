from odoo import models, fields, api


class NexoRestaurantTable(models.Model):
    _name = 'nexo.restaurant.table'
    _description = 'Mesa'
    _order = 'area_id, name'

    name = fields.Char('Nombre', required=True)
    capacity = fields.Integer('Capacidad', default=4)
    area_id = fields.Many2one('nexo.restaurant.area', 'Área')
    status = fields.Selection([
        ('free', 'Libre'),
        ('occupied', 'Ocupada'),
        ('reserved', 'Reservada'),
        ('cleaning', 'Limpieza'),
    ], 'Estado', default='free', required=True)
    current_order_id = fields.Many2one('nexo.restaurant.order', 'Pedido actual')

    def action_new_order(self):
        self.ensure_one()
        if self.current_order_id and self.current_order_id.state not in ('paid', 'cancel'):
            return self.current_order_id.action_open_tpv()
        order = self.env['nexo.restaurant.order'].create({
            'table_id': self.id,
        })
        self.current_order_id = order.id
        return order.action_open_tpv()
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)


class NexoRestaurantArea(models.Model):
    _name = 'nexo.restaurant.area'
    _description = 'Área / sala'

    name = fields.Char('Nombre', required=True)
    table_ids = fields.One2many('nexo.restaurant.table', 'area_id', 'Mesas')

    def action_new_order(self):
        self.ensure_one()
        if self.current_order_id and self.current_order_id.state not in ('paid', 'cancel'):
            return self.current_order_id.action_open_tpv()
        order = self.env['nexo.restaurant.order'].create({
            'table_id': self.id,
        })
        self.current_order_id = order.id
        return order.action_open_tpv()
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)
