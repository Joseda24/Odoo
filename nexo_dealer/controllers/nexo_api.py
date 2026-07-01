from odoo import http
from odoo.http import request
import json


class NexoApi(http.Controller):

    @http.route('/api/v1/vehicles', type='http', auth='none', cors='*', methods=['GET'], csrf=False)
    def vehicle_list(self, **kwargs):
        vehicles = request.env['nexo.vehicle'].sudo().search([
            ('vehicle_status', '=', 'available'),
        ])
        data = []
        for v in vehicles:
            data.append({
                'id': v.id,
                'name': v.name,
                'brand': v.brand_id.name,
                'model': v.model_id.name,
                'year': v.model_year,
                'price': v.sale_price,
                'vin': v.vin,
                'color': v.color,
                'mileage': v.mileage,
                'engine': v.engine,
                'transmission': v.transmission,
                'fuel': v.fuel_type,
                'doors': v.doors,
                'seats': v.seats,
                'image_url': f'/api/v1/vehicle/{v.id}/image' if v.image else None,
            })
        return http.Response(
            json.dumps(data, ensure_ascii=False),
            content_type='application/json;charset=utf-8',
            status=200,
        )

    @http.route('/api/v1/vehicle/<int:vehicle_id>', type='http', auth='none', cors='*', methods=['GET'], csrf=False)
    def vehicle_detail(self, vehicle_id, **kwargs):
        v = request.env['nexo.vehicle'].sudo().browse(vehicle_id)
        if not v.exists():
            return http.Response(
                json.dumps({'error': 'Vehicle not found'}),
                content_type='application/json;charset=utf-8',
                status=404,
            )
        data = {
            'id': v.id,
            'name': v.name,
            'brand': v.brand_id.name,
            'model': v.model_id.name,
            'year': v.model_year,
            'price': v.sale_price,
            'vin': v.vin,
            'color': v.color,
            'mileage': v.mileage,
            'engine': v.engine,
            'transmission': v.transmission,
            'fuel': v.fuel_type,
            'doors': v.doors,
            'seats': v.seats,
            'description': v.description,
            'status': v.vehicle_status,
            'location': v.location,
            'acquisition_date': str(v.acquisition_date) if v.acquisition_date else None,
            'images': [],
        }
        for img in v.image_ids:
            data['images'].append({
                'id': img.id,
                'name': img.name,
            })
        return http.Response(
            json.dumps(data, ensure_ascii=False),
            content_type='application/json;charset=utf-8',
            status=200,
        )

    @http.route('/api/v1/vehicle/<int:vehicle_id>/image', type='http', auth='none', cors='*', methods=['GET'], csrf=False)
    def vehicle_image(self, vehicle_id, **kwargs):
        v = request.env['nexo.vehicle'].sudo().browse(vehicle_id)
        if not v.exists() or not v.image:
            return http.Response(status=404)
        return http.Response(
            v.image.decode() if isinstance(v.image, bytes) else v.image,
            content_type='image/jpeg',
            status=200,
        )

    @http.route('/api/v1/brands', type='http', auth='none', cors='*', methods=['GET'], csrf=False)
    def brand_list(self, **kwargs):
        brands = request.env['nexo.vehicle.brand'].sudo().search([])
        data = [{'id': b.id, 'name': b.name} for b in brands]
        return http.Response(
            json.dumps(data, ensure_ascii=False),
            content_type='application/json;charset=utf-8',
            status=200,
        )

    @http.route('/api/v1/brand/<int:brand_id>/models', type='http', auth='none', cors='*', methods=['GET'], csrf=False)
    def model_list(self, brand_id, **kwargs):
        models = request.env['nexo.vehicle.model'].sudo().search([('brand_id', '=', brand_id)])
        data = [{'id': m.id, 'name': m.name} for m in models]
        return http.Response(
            json.dumps(data, ensure_ascii=False),
            content_type='application/json;charset=utf-8',
            status=200,
        )
