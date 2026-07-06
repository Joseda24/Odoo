from odoo import models, fields, api, _


class NexoQuickSale(models.TransientModel):
    _name = 'nexo.quick.sale'
    _description = 'Venta rápida'

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehículo', required=True,
        domain=[('vehicle_status', 'in', ('available', 'reserved'))])
    partner_id = fields.Many2one('res.partner', 'Cliente', required=True)
    salesperson_id = fields.Many2one('res.users', 'Vendedor',
        default=lambda self: self.env.user, required=True)
    sale_price = fields.Float('Precio de venta', required=True)
    payment_method = fields.Selection([
        ('cash', 'Contado'),
        ('finance', 'Financiamiento'),
        ('trade_in', 'Trade-in'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
    ], 'Método de pago', default='cash')
    financing_plan_id = fields.Many2one('nexo.financing.plan', 'Plan de financiamiento')
    notes = fields.Text('Notas')

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            self.sale_price = self.vehicle_id.car_value or self.vehicle_id.sale_price or 0

    def action_create_sale(self):
        self.ensure_one()

        if self.vehicle_id.vehicle_status == 'sold':
            raise models.ValidationError(
                _('El vehículo "%s" ya ha sido vendido.') % self.vehicle_id.display_name
            )

        if self.env['sale.order'].search_count([
            ('vehicle_id', '=', self.vehicle_id.id),
            ('state', 'in', ('sale', 'done')),
        ]):
            raise models.ValidationError(
                _('El vehículo "%s" ya tiene una orden de venta confirmada.') % self.vehicle_id.display_name
            )

        product = self.env['product.product'].search([
            ('name', '=', self.vehicle_id.name)
        ], limit=1)
        if not product:
            product = self.env['product.product'].create({
                'name': self.vehicle_id.name,
                'list_price': self.sale_price,
                'type': 'consu',
                'categ_id': self.env.ref('product.product_category_all').id,
            })

        order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'user_id': self.salesperson_id.id,
            'vehicle_id': self.vehicle_id.id,
            'payment_method': self.payment_method,
            'note': self.notes,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'name': self.vehicle_id.name,
                'product_uom_qty': 1,
                'price_unit': self.sale_price,
            })],
        })

        order.action_confirm()

        if self.payment_method == 'finance' and self.financing_plan_id:
            self.env['nexo.financing.request'].create({
                'partner_id': self.partner_id.id,
                'vehicle_id': self.vehicle_id.id,
                'sale_order_id': order.id,
                'plan_id': self.financing_plan_id.id,
                'vehicle_price': self.sale_price,
                'salesperson_id': self.salesperson_id.id,
                'status': 'approved',
            })

        employee = self.salesperson_id.employee_id
        comm_rate = employee.nexo_commission_rate or 5.0
        self.env['nexo.commission'].create({
            'employee_id': employee.id,
            'sale_order_id': order.id,
            'vehicle_id': self.vehicle_id.id,
            'base_amount': self.sale_price,
            'rate': comm_rate,
            'amount': self.sale_price * comm_rate / 100,
            'date': fields.Date.today(),
            'paid': False,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': order.id,
            'view_mode': 'form',
            'view_id': self.env.ref('sale.view_order_form').id,
            'target': 'current',
        }
