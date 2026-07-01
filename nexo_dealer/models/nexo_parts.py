from odoo import models, fields, api
from odoo.exceptions import UserError


class NexoPart(models.Model):
    _name = 'nexo.part'
    _description = 'Refacción / Pieza'
    _order = 'name'

    name = fields.Char('Nombre', required=True)
    code = fields.Char('Código')
    barcode = fields.Char('Código de barras')
    category = fields.Selection([
        ('engine', 'Motor'),
        ('transmission', 'Transmisión'),
        ('brake', 'Frenos'),
        ('suspension', 'Suspensión'),
        ('electric', 'Eléctrico'),
        ('body', 'Carrocería'),
        ('interior', 'Interior'),
        ('other', 'Otro'),
    ], 'Categoría', default='other')
    stock = fields.Float('Stock actual', default=0.0)
    min_stock = fields.Float('Stock mínimo', default=0.0)
    cost_price = fields.Float('Costo', default=0.0)
    sale_price = fields.Float('Precio de venta', default=0.0)
    location = fields.Char('Ubicación')
    supplier_id = fields.Many2one('nexo.partner', 'Proveedor')
    active = fields.Boolean('Activo', default=True)
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    _sql_constraints = [
        ('code_unique', 'unique(code, company_id)', 'El código debe ser único'),
    ]


class NexoPartMove(models.Model):
    _name = 'nexo.part.move'
    _description = 'Movimiento de refacción'
    _order = 'date desc, id desc'

    name = fields.Char('Folio', required=True, copy=False, readonly=True, default='Nuevo')
    part_id = fields.Many2one('nexo.part', 'Refacción', required=True)
    type = fields.Selection([
        ('in', 'Entrada'),
        ('out', 'Salida'),
    ], 'Tipo', required=True)
    quantity = fields.Float('Cantidad', required=True)
    date = fields.Date('Fecha', default=fields.Date.today)
    reference = fields.Char('Referencia')
    service_order_id = fields.Many2one('nexo.vehicle.service.order', 'Orden de servicio')
    notes = fields.Text('Notas')
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                seq = self.env['nexo.sequence'].search([('code', '=', 'MOV')], limit=1)
                if seq:
                    vals['name'] = seq.get_next_code()
        return super().create(vals_list)

    def action_validate(self):
        for move in self:
            part = move.part_id
            if move.type == 'out':
                if part.stock < move.quantity:
                    raise UserError(f'Stock insuficiente de {part.name}')
                part.stock -= move.quantity
            else:
                part.stock += move.quantity
