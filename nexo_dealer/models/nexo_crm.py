from odoo import models, fields, api


class NexoCrmStage(models.Model):
    _name = 'nexo.crm.stage'
    _description = 'Etapa del pipeline'
    _order = 'sequence, id'

    name = fields.Char('Nombre', required=True)
    sequence = fields.Integer('Secuencia', default=10)
    probability = fields.Float('Probabilidad (%)', default=100.0)
    fold = fields.Boolean('Plegado en kanban')


class NexoLead(models.Model):
    _name = 'nexo.lead'
    _description = 'Lead / Oportunidad'
    _order = 'date desc, id desc'

    name = fields.Char('Asunto', required=True)
    partner_id = fields.Many2one('nexo.partner', 'Cliente')
    contact_name = fields.Char('Nombre de contacto')
    email = fields.Char('Correo')
    phone = fields.Char('Teléfono')
    source = fields.Selection([
        ('website', 'Sitio web'),
        ('referral', 'Referido'),
        ('phone', 'Llamada'),
        ('walkin', 'Mostrador'),
        ('social', 'Redes sociales'),
        ('email_marketing', 'Email marketing'),
        ('other', 'Otro'),
    ], 'Origen', default='walkin')
    stage_id = fields.Many2one('nexo.crm.stage', 'Etapa', default=lambda s: s._default_stage())
    probability = fields.Float('Probabilidad (%)', default=10.0)
    expected_revenue = fields.Float('Ingreso esperado')
    vehicle_id = fields.Many2one('nexo.vehicle', 'Vehículo de interés')
    salesperson_id = fields.Many2one('res.users', 'Vendedor', default=lambda self: self.env.user)
    date = fields.Date('Fecha', default=fields.Date.today)
    description = fields.Text('Notas')
    active = fields.Boolean('Activo', default=True)
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)
    color = fields.Integer('Color')

    @api.model
    def _default_stage(self):
        return self.env['nexo.crm.stage'].search([], order='sequence', limit=1)

    def action_convert_to_sale(self):
        sale_order = self.env['nexo.sale.order']
        for lead in self:
            partner = lead.partner_id
            if not partner:
                partner = self.env['nexo.partner'].create({
                    'name': lead.contact_name or lead.name,
                    'email': lead.email,
                    'phone': lead.phone,
                    'is_customer': True,
                })
            order_vals = {
                'partner_id': partner.id,
                'salesperson_id': lead.salesperson_id.id or self.env.user.id,
                'vehicle_id': lead.vehicle_id.id,
                'notes': lead.description,
            }
            order = sale_order.create(order_vals)
            lead.stage_id = self.env['nexo.crm.stage'].search([], order='sequence desc', limit=1)
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'nexo.sale.order',
                'res_id': order.id,
                'view_mode': 'form',
                'target': 'current',
            }
