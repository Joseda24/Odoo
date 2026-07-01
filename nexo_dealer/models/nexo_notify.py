from odoo import models, fields, api
from datetime import date, timedelta


class NexoReminder(models.Model):
    _name = 'nexo.reminder'
    _description = 'Recordatorio'
    _order = 'date desc, id desc'

    name = fields.Char('Asunto', required=True)
    model = fields.Char('Modelo')
    res_id = fields.Integer('ID del registro')
    partner_id = fields.Many2one('nexo.partner', 'Cliente')
    vehicle_id = fields.Many2one('nexo.vehicle', 'Vehículo')
    date = fields.Date('Fecha', required=True)
    type = fields.Selection([
        ('warranty', 'Vencimiento de garantía'),
        ('maintenance', 'Mantenimiento'),
        ('insurance', 'Seguro'),
        ('birthday', 'Cumpleaños'),
        ('followup', 'Seguimiento'),
        ('other', 'Otro'),
    ], 'Tipo', default='other')
    done = fields.Boolean('Atendido', default=False)
    notes = fields.Text('Notas')
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    def action_mark_done(self):
        self.done = True


class NexoVehicle(models.Model):
    _inherit = 'nexo.vehicle'

    next_maintenance_date = fields.Date('Próximo mantenimiento')
    next_maintenance_km = fields.Float('Próximo mantenimiento (km)')
    insurance_expiry = fields.Date('Vencimiento de seguro')


class NexoReminderCron(models.Model):
    _name = 'nexo.reminder.cron'
    _description = 'Configuración de recordatorios automáticos'

    name = fields.Char('Nombre', required=True)
    days_before = fields.Integer('Días antes', default=7)
    type = fields.Selection([
        ('warranty', 'Vencimiento de garantía'),
        ('maintenance', 'Mantenimiento'),
        ('insurance', 'Seguro'),
        ('birthday', 'Cumpleaños'),
    ], 'Tipo', required=True)
    active = fields.Boolean('Activo', default=True)

    def _cron_generate_reminders(self):
        today = date.today()
        configs = self.search([('active', '=', True)])
        for cfg in configs:
            if cfg.type == 'warranty':
                vehicles = self.env['nexo.vehicle'].search([
                    ('warranty_expiry', '!=', False),
                    ('warranty_expiry', '<=', today + timedelta(days=cfg.days_before)),
                    ('warranty_expiry', '>=', today),
                ])
                for v in vehicles:
                    existing = self.env['nexo.reminder'].search([
                        ('vehicle_id', '=', v.id),
                        ('type', '=', 'warranty'),
                        ('done', '=', False),
                    ], limit=1)
                    if not existing:
                        partners = self.env['nexo.sale.order'].search([
                            ('vehicle_id', '=', v.id),
                        ]).mapped('partner_id')
                        partner = partners[:1] if partners else False
                        self.env['nexo.reminder'].create({
                            'name': f'Garantía por vencer - {v.name}',
                            'partner_id': partner.id if partner else False,
                            'vehicle_id': v.id,
                            'date': v.warranty_expiry,
                            'type': 'warranty',
                            'notes': f'La garantía del vehículo {v.name} vence el {v.warranty_expiry}',
                        })

            elif cfg.type == 'maintenance':
                vehicles = self.env['nexo.vehicle'].search([
                    ('next_maintenance_date', '!=', False),
                    ('next_maintenance_date', '<=', today + timedelta(days=cfg.days_before)),
                    ('next_maintenance_date', '>=', today),
                ])
                for v in vehicles:
                    existing = self.env['nexo.reminder'].search([
                        ('vehicle_id', '=', v.id),
                        ('type', '=', 'maintenance'),
                        ('done', '=', False),
                    ], limit=1)
                    if not existing:
                        self.env['nexo.reminder'].create({
                            'name': f'Mantenimiento - {v.name}',
                            'vehicle_id': v.id,
                            'date': v.next_maintenance_date,
                            'type': 'maintenance',
                        })

            elif cfg.type == 'insurance':
                vehicles = self.env['nexo.vehicle'].search([
                    ('insurance_expiry', '!=', False),
                    ('insurance_expiry', '<=', today + timedelta(days=cfg.days_before)),
                    ('insurance_expiry', '>=', today),
                ])
                for v in vehicles:
                    existing = self.env['nexo.reminder'].search([
                        ('vehicle_id', '=', v.id),
                        ('type', '=', 'insurance'),
                        ('done', '=', False),
                    ], limit=1)
                    if not existing:
                        partners = self.env['nexo.sale.order'].search([
                            ('vehicle_id', '=', v.id),
                        ]).mapped('partner_id')
                        partner = partners[:1] if partners else False
                        self.env['nexo.reminder'].create({
                            'name': f'Seguro por vencer - {v.name}',
                            'partner_id': partner.id if partner else False,
                            'vehicle_id': v.id,
                            'date': v.insurance_expiry,
                            'type': 'insurance',
                        })

            elif cfg.type == 'birthday':
                partners = self.env['nexo.partner'].search([])
                for p in partners:
                    if not p._fields.get('birthdate'):
                        continue
                    bday = p.birthdate
                    if not bday:
                        continue
                    next_bday = date(today.year, bday.month, bday.day)
                    if next_bday < today:
                        next_bday = date(today.year + 1, bday.month, bday.day)
                    days_until = (next_bday - today).days
                    if 0 <= days_until <= cfg.days_before:
                        existing = self.env['nexo.reminder'].search([
                            ('partner_id', '=', p.id),
                            ('type', '=', 'birthday'),
                            ('date', '=', next_bday),
                        ], limit=1)
                        if not existing:
                            self.env['nexo.reminder'].create({
                                'name': f'Cumpleaños - {p.name}',
                                'partner_id': p.id,
                                'date': next_bday,
                                'type': 'birthday',
                            })
