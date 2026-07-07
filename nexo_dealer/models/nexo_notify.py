from odoo import models, fields, api
from datetime import date, timedelta


class NexoReminder(models.Model):
    _name = 'nexo.reminder'
    _description = 'Recordatorio'
    _order = 'date desc, id desc'

    name = fields.Char('Asunto', required=True)
    model = fields.Char('Modelo')
    res_id = fields.Integer('ID del registro')
    partner_id = fields.Many2one('res.partner', 'Cliente')
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehículo')
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


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

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

    @api.model
    def _cron_generate_reminders(self):
        today = date.today()
        configs = self.search([('active', '=', True)])
        for cfg in configs:
            if cfg.type == 'warranty':
                vehicles = self.env['fleet.vehicle'].search([
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
                        partners = self.env['sale.order'].search([
                            ('vehicle_id', '=', v.id),
                        ]).mapped('partner_id')
                        partner = partners[:1] if partners else False
                        self.env['nexo.reminder'].create({
                            'name': f'Garantía por vencer - {v.display_name}',
                            'partner_id': partner.id if partner else False,
                            'vehicle_id': v.id,
                            'date': v.warranty_expiry,
                            'type': 'warranty',
                            'notes': f'La garantía del vehículo {v.display_name} vence el {v.warranty_expiry}',
                        })
            elif cfg.type == 'maintenance':
                vehicles = self.env['fleet.vehicle'].search([
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
                            'name': f'Mantenimiento - {v.display_name}',
                            'vehicle_id': v.id,
                            'date': v.next_maintenance_date,
                            'type': 'maintenance',
                        })
            elif cfg.type == 'insurance':
                vehicles = self.env['fleet.vehicle'].search([
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
                        partners = self.env['sale.order'].search([
                            ('vehicle_id', '=', v.id),
                        ]).mapped('partner_id')
                        partner = partners[:1] if partners else False
                        self.env['nexo.reminder'].create({
                            'name': f'Seguro por vencer - {v.display_name}',
                            'partner_id': partner.id if partner else False,
                            'vehicle_id': v.id,
                            'date': v.insurance_expiry,
                            'type': 'insurance',
                        })
            elif cfg.type == 'birthday':
                target_end = today + timedelta(days=cfg.days_before)
                today_md = today.strftime('%m-%d')
                target_md = target_end.strftime('%m-%d')
                if today_md <= target_md:
                    self.env.cr.execute("""
                        SELECT id, name, birthdate
                        FROM res_partner
                        WHERE birthdate IS NOT NULL
                        AND to_char(birthdate, 'MM-DD') BETWEEN %s AND %s
                    """, (today_md, target_md))
                else:
                    self.env.cr.execute("""
                        SELECT id, name, birthdate
                        FROM res_partner
                        WHERE birthdate IS NOT NULL
                        AND (
                            to_char(birthdate, 'MM-DD') BETWEEN %s AND '12-31'
                            OR to_char(birthdate, 'MM-DD') BETWEEN '01-01' AND %s
                        )
                    """, (today_md, target_md))
                rows = self.env.cr.fetchall()
                for p_id, p_name, birthdate in rows:
                    next_bday = date(today.year, birthdate.month, birthdate.day)
                    if next_bday < today:
                        next_bday = date(today.year + 1, birthdate.month, birthdate.day)
                    existing = self.env['nexo.reminder'].search([
                        ('partner_id', '=', p_id),
                        ('type', '=', 'birthday'),
                        ('date', '=', next_bday),
                    ], limit=1)
                    if not existing:
                        self.env['nexo.reminder'].create({
                            'name': f'Cumpleaños - {p_name}',
                            'partner_id': p_id,
                            'date': next_bday,
                            'type': 'birthday',
                        })
