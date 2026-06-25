from odoo import models, fields, api
from odoo.exceptions import UserError


class NexoInvoice(models.Model):
    _name = 'nexo.invoice'
    _description = 'Factura'
    _order = 'date_invoice desc, id desc'

    name = fields.Char('Folio', required=True, copy=False, readonly=True, default='Nuevo')
    partner_id = fields.Many2one('nexo.partner', 'Cliente', required=True)
    date_invoice = fields.Date('Fecha de factura', default=fields.Date.today, required=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('posted', 'Contabilizada'),
        ('paid', 'Pagada'),
        ('cancel', 'Cancelada'),
    ], 'Estado', default='draft', required=True, copy=False)
    type = fields.Selection([
        ('out_invoice', 'Factura cliente'),
        ('in_invoice', 'Factura proveedor'),
    ], 'Tipo', default='out_invoice', required=True)
    line_ids = fields.One2many('nexo.invoice.line', 'invoice_id', 'Líneas')
    amount_subtotal = fields.Float('Subtotal', compute='_compute_amounts', store=True)
    amount_tax = fields.Float('Impuestos', compute='_compute_amounts', store=True)
    amount_total = fields.Float('Total', compute='_compute_amounts', store=True)
    notes = fields.Text('Notas')
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self: self.env.company)

    @api.depends('line_ids.price_subtotal', 'line_ids.tax_amount')
    def _compute_amounts(self):
        for inv in self:
            inv.amount_subtotal = sum(l.price_subtotal for l in inv.line_ids)
            inv.amount_tax = sum(l.tax_amount for l in inv.line_ids)
            inv.amount_total = inv.amount_subtotal + inv.amount_tax

    def action_post(self):
        for inv in self:
            if inv.state != 'draft':
                raise UserError('Solo borradores pueden contabilizarse')
            inv.state = 'posted'

    def action_paid(self):
        for inv in self:
            if inv.state != 'posted':
                raise UserError('Solo facturas contabilizadas pueden marcarse como pagadas')
            inv.state = 'paid'

    def action_cancel(self):
        for inv in self:
            if inv.state == 'paid':
                raise UserError('No se puede cancelar una factura pagada')
            inv.state = 'cancel'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                seq = self.env['nexo.sequence'].search([('code', '=', 'INVOICE')], limit=1)
                if seq:
                    vals['name'] = seq.get_next_code()
        return super().create(vals_list)


class NexoInvoiceLine(models.Model):
    _name = 'nexo.invoice.line'
    _description = 'Línea de factura'

    invoice_id = fields.Many2one('nexo.invoice', 'Factura', required=True, ondelete='cascade')
    product_id = fields.Many2one('nexo.product', 'Producto')
    description = fields.Char('Descripción', required=True)
    quantity = fields.Float('Cantidad', default=1.0, required=True)
    price_unit = fields.Float('Precio unitario', default=0.0, required=True)
    tax_percent = fields.Float('Impuesto %', default=0.0)
    price_subtotal = fields.Float('Subtotal', compute='_compute_line_amounts', store=True)
    tax_amount = fields.Float('Importe impuesto', compute='_compute_line_amounts', store=True)
    price_total = fields.Float('Total', compute='_compute_line_amounts', store=True)
    company_id = fields.Many2one(related='invoice_id.company_id', store=True)

    @api.depends('quantity', 'price_unit', 'tax_percent')
    def _compute_line_amounts(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
            line.tax_amount = line.price_subtotal * (line.tax_percent / 100.0)
            line.price_total = line.price_subtotal + line.tax_amount

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name
            self.price_unit = self.product_id.sale_price
