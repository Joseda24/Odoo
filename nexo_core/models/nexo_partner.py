from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    birthdate = fields.Date('Fecha de nacimiento')
    last_contact = fields.Date('Último contacto')
    referred_by = fields.Many2one('res.partner', 'Referido por')
