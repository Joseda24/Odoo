from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    nexo_position = fields.Selection([
        ('sales', 'Vendedor'),
        ('mechanic', 'Mecánico'),
        ('manager', 'Gerente'),
        ('admin', 'Administrativo'),
    ], 'Puesto', default='sales')
    nexo_code = fields.Char('Código')
    nexo_commission_type = fields.Selection([
        ('percentage', 'Porcentaje'),
        ('fixed', 'Monto fijo'),
    ], 'Tipo de comisión', default='percentage')
    nexo_commission_rate = fields.Float('% Comisión', default=5.0)
    nexo_fixed_commission = fields.Float('Comisión fija', default=0.0)


class NexoCommission(models.Model):
    _name = 'nexo.commission'
    _description = 'Comisión'
    _order = 'date desc, id desc'

    name = fields.Char('Folio', required=True, copy=False, readonly=True, default='Nuevo')
    employee_id = fields.Many2one('hr.employee', 'Empleado', required=True)
    sale_order_id = fields.Many2one('sale.order', 'Venta', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehículo')
    date = fields.Date('Fecha', default=fields.Date.today)
    commission_type = fields.Selection(related='employee_id.nexo_commission_type', string='Tipo')
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
