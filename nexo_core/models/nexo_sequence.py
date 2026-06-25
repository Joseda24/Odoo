from odoo import models, fields, api


class NexoSequence(models.Model):
    _name = 'nexo.sequence'
    _description = 'Secuencia automática para documentos'
    _order = 'name'

    name = fields.Char('Nombre', required=True)
    code = fields.Char('Código', required=True, help='Código único ej: SALE, PURCHASE, INVOICE')
    prefix = fields.Char('Prefijo', default='', help='Ej: FAC-, PED-')
    suffix = fields.Char('Sufijo', default='')
    padding = fields.Integer('Relleno', default=5, help='Cantidad de dígitos')
    next_number = fields.Integer('Siguiente número', default=1, required=True)
    active = fields.Boolean('Activo', default=True)
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    _sql_constraints = [
        ('code_unique', 'unique(code, company_id)', 'El código de secuencia debe ser único por compañía')
    ]

    def _get_next_number(self):
        self.ensure_one()
        num = self.next_number
        self.next_number += 1
        return num

    def _format_number(self, num):
        self.ensure_one()
        return f'{self.prefix}{str(num).zfill(self.padding)}{self.suffix}'

    def get_next_code(self):
        self.ensure_one()
        num = self._get_next_number()
        return self._format_number(num)
