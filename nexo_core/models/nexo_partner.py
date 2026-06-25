from odoo import models, fields, api


class NexoPartner(models.Model):
    _name = 'nexo.partner'
    _description = 'Cliente / Proveedor'
    _order = 'name'

    name = fields.Char('Nombre', required=True)
    phone = fields.Char('Teléfono')
    email = fields.Char('Correo electrónico')
    vat = fields.Char('RFC / NIF')
    street = fields.Char('Calle')
    street2 = fields.Char('Calle 2')
    city = fields.Char('Ciudad')
    state_id = fields.Many2one('res.country.state', 'Estado / Provincia')
    zip = fields.Char('Código Postal')
    country_id = fields.Many2one('res.country', 'País', default=lambda self: self.env.ref('base.mx'))
    company_type = fields.Selection([
        ('person', 'Persona física'),
        ('company', 'Persona moral'),
    ], 'Tipo', default='person', required=True)
    is_customer = fields.Boolean('Cliente', default=True)
    is_supplier = fields.Boolean('Proveedor', default=False)
    image = fields.Binary('Imagen')
    website = fields.Char('Sitio web')
    notes = fields.Text('Notas')
    active = fields.Boolean('Activo', default=True)
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    _sql_constraints = [
        ('vat_unique', 'unique(vat, company_id)', 'El RFC/NIF ya existe para esta compañía'),
    ]
