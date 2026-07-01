from odoo import models, fields


class NexoPartner(models.Model):
    _inherit = 'nexo.partner'

    birthdate = fields.Date('Fecha de nacimiento')
    last_contact = fields.Date('Último contacto')
    referred_by = fields.Many2one('nexo.partner', 'Referido por')
