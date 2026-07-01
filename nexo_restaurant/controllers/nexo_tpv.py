from odoo import http
from odoo.http import request
import json


class TPVController(http.Controller):

    @http.route('/restaurant/tpv', type='http', auth='user', website=False)
    def tpv_main(self):
        return request.render('nexo_restaurant.tpv_page')

    @http.route('/restaurant/tpv/data', type='json', auth='user')
    def tpv_data(self):
        MenuItem = request.env['nexo.menu.item']
        MenuCategory = request.env['nexo.menu.category']
        Table = request.env['nexo.restaurant.table']
        Order = request.env['nexo.restaurant.order']
        Area = request.env['nexo.restaurant.area']

        categories = MenuCategory.search([])
        items = MenuItem.search([('available','=',True)])
        tables = Table.search([])
        areas = Area.search([])
        orders = Order.search([('state','not in',['paid','cancel'])])

        return {
            'categories': [{'id': c.id, 'name': c.name} for c in categories],
            'items': [{
                'id': i.id,
                'name': i.name,
                'price': i.price,
                'category_id': i.category_id.id,
            } for i in items],
            'tables': [{
                'id': t.id,
                'name': t.name,
                'status': t.status,
                'capacity': t.capacity,
                'area_id': t.area_id.id,
                'current_order_id': t.current_order_id.id if t.current_order_id else False,
            } for t in tables],
            'areas': [{'id': a.id, 'name': a.name} for a in areas],
            'orders': [{
                'id': o.id,
                'name': o.name,
                'table_id': o.table_id.id,
                'state': o.state,
                'amount_total': o.amount_total,
                'lines': [{
                    'id': l.id,
                    'menu_item_id': l.menu_item_id.id,
                    'name': l.menu_item_id.name,
                    'quantity': l.quantity,
                    'price_unit': l.price_unit,
                    'price_subtotal': l.price_subtotal,
                    'state': l.state,
                } for l in o.line_ids],
            } for o in orders],
        }

    @http.route('/restaurant/tpv/create_order', type='json', auth='user')
    def create_order(self, table_id):
        table = request.env['nexo.restaurant.table'].browse(table_id)
        if not table:
            return {'error': 'Mesa no encontrada'}
        if table.current_order_id and table.current_order_id.state not in ('paid', 'cancel'):
            order = table.current_order_id
        else:
            order = request.env['nexo.restaurant.order'].create({
                'table_id': table_id,
            })
            table.current_order_id = order.id
        return {'order_id': order.id, 'name': order.name}

    @http.route('/restaurant/tpv/add_line', type='json', auth='user')
    def add_line(self, order_id, item_id, quantity=1):
        order = request.env['nexo.restaurant.order'].browse(order_id)
        item = request.env['nexo.menu.item'].browse(item_id)
        if not order or not item:
            return {'error': 'Pedido o art\u00edculo no encontrado'}
        existing = order.line_ids.filtered(
            lambda l: l.menu_item_id.id == item_id and l.state == 'pending'
        )
        if existing:
            existing[0].quantity += quantity
        else:
            order.write({
                'line_ids': [(0, 0, {
                    'menu_item_id': item_id,
                    'quantity': quantity,
                    'price_unit': item.price,
                })]
            })
        return {
            'order_id': order.id,
            'lines': [{
                'id': l.id, 'menu_item_id': l.menu_item_id.id,
                'name': l.menu_item_id.name, 'quantity': l.quantity,
                'price_unit': l.price_unit, 'price_subtotal': l.price_subtotal,
                'state': l.state,
            } for l in order.line_ids],
            'amount_total': order.amount_total,
        }

    @http.route('/restaurant/tpv/update_line', type='json', auth='user')
    def update_line(self, line_id, quantity):
        line = request.env['nexo.restaurant.order.line'].browse(line_id)
        if not line:
            return {'error': 'L\u00ednea no encontrada'}
        if quantity <= 0:
            line.unlink()
        else:
            line.quantity = quantity
        order = line.order_id
        return {
            'lines': [{
                'id': l.id, 'menu_item_id': l.menu_item_id.id,
                'name': l.menu_item_id.name, 'quantity': l.quantity,
                'price_unit': l.price_unit, 'price_subtotal': l.price_subtotal,
                'state': l.state,
            } for l in order.line_ids],
            'amount_total': order.amount_total,
        }

    @http.route('/restaurant/tpv/send_kitchen', type='json', auth='user')
    def send_kitchen(self, order_id):
        order = request.env['nexo.restaurant.order'].browse(order_id)
        order.action_send_to_kitchen()
        return {
            'state': order.state,
            'lines': [{
                'id': l.id, 'menu_item_id': l.menu_item_id.id,
                'name': l.menu_item_id.name, 'quantity': l.quantity,
                'price_unit': l.price_unit, 'price_subtotal': l.price_subtotal,
                'state': l.state,
            } for l in order.line_ids],
            'amount_total': order.amount_total,
        }

    @http.route('/restaurant/tpv/serve', type='json', auth='user')
    def serve(self, order_id):
        order = request.env['nexo.restaurant.order'].browse(order_id)
        order.action_serve()
        return {
            'state': order.state,
            'lines': [{
                'id': l.id, 'menu_item_id': l.menu_item_id.id,
                'name': l.menu_item_id.name, 'quantity': l.quantity,
                'price_unit': l.price_unit, 'price_subtotal': l.price_subtotal,
                'state': l.state,
            } for l in order.line_ids],
            'amount_total': order.amount_total,
        }

    @http.route('/restaurant/tpv/pay', type='json', auth='user')
    def pay(self, order_id, amount, method='cash'):
        order = request.env['nexo.restaurant.order'].browse(order_id)
        if not order:
            return {'error': 'Pedido no encontrado'}
        order.write({
            'payment_ids': [(0, 0, {
                'amount': amount,
                'method': method,
            })]
        })
        order.action_paid()
        table = order.table_id
        table.current_order_id = False
        table.status = 'free'
        return {'state': order.state}

    @http.route('/restaurant/tpv/table_status', type='json', auth='user')
    def table_status(self, table_id, status):
        table = request.env['nexo.restaurant.table'].browse(table_id)
        if table:
            table.status = status
        return True
