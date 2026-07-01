from odoo import models, fields, api


class NexoEmployee(models.Model):
    _name = 'nexo.employee'
    _description = 'Empleado'
    _order = 'name'

    name = fields.Char('Nombre', required=True)
    code = fields.Char('Código')
    phone = fields.Char('Teléfono')
    email = fields.Char('Correo')
    position = fields.Selection([
        ('sales', 'Vendedor'),
        ('mechanic', 'Mecánico'),
        ('manager', 'Gerente'),
        ('admin', 'Administrativo'),
    ], 'Puesto', default='sales')
    user_id = fields.Many2one('res.users', 'Usuario')
    commission_type = fields.Selection([
        ('percentage', 'Porcentaje'),
        ('fixed', 'Monto fijo'),
    ], 'Tipo de comisión', default='percentage')
    commission_rate = fields.Float('% Comisión', default=5.0)
    fixed_commission = fields.Float('Comisión fija', default=0.0)
    active = fields.Boolean('Activo', default=True)
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    _sql_constraints = [
        ('code_unique', 'unique(code, company_id)', 'El código de empleado debe ser único'),
    ]


class NexoCommission(models.Model):
    _name = 'nexo.commission'
    _description = 'Comisión'
    _order = 'date desc, id desc'

    name = fields.Char('Folio', required=True, copy=False, readonly=True, default='Nuevo')
    employee_id = fields.Many2one('nexo.employee', 'Empleado', required=True)
    sale_order_id = fields.Many2one('nexo.sale.order', 'Venta', required=True)
    vehicle_id = fields.Many2one('nexo.vehicle', 'Vehículo')
    date = fields.Date('Fecha', default=fields.Date.today)
    commission_type = fields.Selection(related='employee_id.commission_type', string='Tipo')
    base_amount = fields.Float('Monto base', readonly=True)
    rate = fields.Float('Tasa', readonly=True)
    amount = fields.Float('Comisión', readonly=True)
    paid = fields.Boolean('Pagada', default=False)
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                seq = self.env['nexo.sequence'].search([('code', '=', 'COM')], limit=1)
                if seq:
                    vals['name'] = seq.get_next_code()
        return super().create(vals_list)

    def action_set_paid(self):
        self.paid = True
