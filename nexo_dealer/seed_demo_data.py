"""
Seed demo data for nexo_dealer - creates realistic dealership data
Run: odoo-bin shell -d dealer_db --path=/mnt/extra-addons < seed_demo_data.py
Or: python3 seed_demo_data.py (with Odoo env configured)
"""

import random
from datetime import datetime, timedelta

def seed(env):
    """Main seed function"""
    today = datetime.now()
    user = env.ref('base.user_admin')

    # ── helpers ──
    def rand_date(start, end):
        return start + timedelta(days=random.randint(0, int((end - start).days)))

    def rand_choice(items):
        return random.choice(items)

    def create_batch(model, data_list):
        records = env[model]
        for vals in data_list:
            records |= env[model].create(vals)
        return records

    # ──────────────────────────────────────────
    # 1. BRANDS & MODELS
    # ──────────────────────────────────────────
    brand_data = [
        {'name': 'Toyota', 'logo': False, 'description': 'Marca japonesa líder en confiabilidad'},
        {'name': 'Honda', 'logo': False, 'description': 'Innovación y eficiencia japonesa'},
        {'name': 'BMW', 'logo': False, 'description': 'Prestigio alemán y deportividad'},
        {'name': 'Mercedes-Benz', 'logo': False, 'description': 'Lujo alemán de alta gama'},
        {'name': 'Volkswagen', 'logo': False, 'description': 'El auto del pueblo alemán'},
        {'name': 'Ford', 'logo': False, 'description': 'Potencia americana'},
        {'name': 'Chevrolet', 'logo': False, 'description': 'Icono americano'},
        {'name': 'Nissan', 'logo': False, 'description': 'Tecnología japonesa'},
        {'name': 'Hyundai', 'logo': False, 'description': 'Calidad y garantía coreana'},
        {'name': 'Mazda', 'logo': False, 'description': 'Diseño y conducción japonesa'},
    ]
    brands = create_batch('fleet.vehicle.model.brand', brand_data)
    print(f'  Created {len(brands)} brands')

    model_data = [
        {'name': 'Corolla', 'brand_id': brands[0].id, 'vehicle_type': 'car'},
        {'name': 'RAV4', 'brand_id': brands[0].id, 'vehicle_type': 'car'},
        {'name': 'Hilux', 'brand_id': brands[0].id, 'vehicle_type': 'car'},
        {'name': 'Civic', 'brand_id': brands[1].id, 'vehicle_type': 'car'},
        {'name': 'CR-V', 'brand_id': brands[1].id, 'vehicle_type': 'car'},
        {'name': 'Serie 3', 'brand_id': brands[2].id, 'vehicle_type': 'car'},
        {'name': 'X5', 'brand_id': brands[2].id, 'vehicle_type': 'car'},
        {'name': 'Clase C', 'brand_id': brands[3].id, 'vehicle_type': 'car'},
        {'name': 'GLC', 'brand_id': brands[3].id, 'vehicle_type': 'car'},
        {'name': 'Golf', 'brand_id': brands[4].id, 'vehicle_type': 'car'},
        {'name': 'Tiguan', 'brand_id': brands[4].id, 'vehicle_type': 'car'},
        {'name': 'Mustang', 'brand_id': brands[5].id, 'vehicle_type': 'car'},
        {'name': 'Ranger', 'brand_id': brands[5].id, 'vehicle_type': 'car'},
        {'name': 'Camaro', 'brand_id': brands[6].id, 'vehicle_type': 'car'},
        {'name': 'Silverado', 'brand_id': brands[6].id, 'vehicle_type': 'car'},
        {'name': 'Sentra', 'brand_id': brands[7].id, 'vehicle_type': 'car'},
        {'name': 'X-Trail', 'brand_id': brands[7].id, 'vehicle_type': 'car'},
        {'name': 'Tucson', 'brand_id': brands[8].id, 'vehicle_type': 'car'},
        {'name': 'Santa Fe', 'brand_id': brands[8].id, 'vehicle_type': 'car'},
        {'name': 'Mazda3', 'brand_id': brands[9].id, 'vehicle_type': 'car'},
        {'name': 'CX-5', 'brand_id': brands[9].id, 'vehicle_type': 'car'},
    ]
    models = create_batch('fleet.vehicle.model', model_data)
    print(f'  Created {len(models)} models')

    # ──────────────────────────────────────────
    # 2. PRODUCTS
    # ──────────────────────────────────────────
    product_templates = [
        ('Toyota Corolla', 22000, 18500),
        ('Toyota RAV4', 32000, 27000),
        ('Toyota Hilux', 38000, 31000),
        ('Honda Civic', 24000, 20000),
        ('Honda CR-V', 33000, 28000),
        ('BMW Serie 3', 42000, 35000),
        ('BMW X5', 65000, 54000),
        ('Mercedes Clase C', 45000, 37000),
        ('Mercedes GLC', 55000, 46000),
        ('VW Golf', 21000, 17500),
        ('VW Tiguan', 30000, 25000),
        ('Ford Mustang', 35000, 29000),
        ('Ford Ranger', 36000, 30000),
        ('Chevrolet Camaro', 38000, 31000),
        ('Chevrolet Silverado', 42000, 35000),
        ('Nissan Sentra', 20000, 16500),
        ('Nissan X-Trail', 29000, 24000),
        ('Hyundai Tucson', 27000, 22500),
        ('Hyundai Santa Fe', 35000, 29000),
        ('Mazda Mazda3', 23000, 19000),
        ('Mazda CX-5', 31000, 26000),
    ]
    products = create_batch('product.product', [{
        'name': name,
        'list_price': list_price,
        'standard_price': cost,
        'type': 'consu',
        'categ_id': env.ref('product.product_category_all').id,
        'invoice_policy': 'order',
    } for name, list_price, cost in product_templates])
    print(f'  Created {len(products)} products')

    # ──────────────────────────────────────────
    # 3. EMPLOYEES
    # ──────────────────────────────────────────
    emp_info = [
        ('Carlos Mendoza', 'carlos@nexo.com', 'Vendedor Senior'),
        ('María García', 'maria@nexo.com', 'Vendedora'),
        ('José López', 'jose@nexo.com', 'Mecánico Jefe'),
        ('Ana Martínez', 'ana@nexo.com', 'Gerente de Ventas'),
        ('Luis Rodríguez', 'luis@nexo.com', 'Vendedor'),
        ('Sofía Hernández', 'sofia@nexo.com', 'Asesora Financiera'),
        ('Pedro Sánchez', 'pedro@nexo.com', 'Mecánico'),
        ('Diana Torres', 'diana@nexo.com', 'Gerente General'),
        ('Roberto Flores', 'roberto@nexo.com', 'Vendedor'),
        ('Laura Vargas', 'laura@nexo.com', 'Mecánica'),
    ]
    emp_partners = create_batch('res.partner', [{
        'name': name, 'email': email, 'company_type': 'person',
        'customer_rank': 0, 'supplier_rank': 0,
    } for name, email, _ in emp_info])

    employees = []
    for i, (name, email, role) in enumerate(emp_info):
        emp_partners[i].write({'employee': True})
        emp = env['hr.employee'].create({
            'name': name, 'work_email': email, 'job_title': role,
            'work_phone': f'+34 6{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)}',
        })
        employees.append(emp)
    print(f'  Created {len(employees)} employees')

    # ──────────────────────────────────────────
    # 4. CUSTOMERS
    # ──────────────────────────────────────────
    customer_info = [
        ('Juan Pérez', 'juan.perez@email.com', '+34 612 345 678', 'Madrid', 'Calle Mayor 15'),
        ('Ana Gómez', 'ana.gomez@email.com', '+34 623 456 789', 'Barcelona', 'Av. Diagonal 230'),
        ('Carlos Ruiz', 'carlos.ruiz@email.com', '+34 634 567 890', 'Valencia', 'Calle Colón 42'),
        ('Laura Díaz', 'laura.diaz@email.com', '+34 645 678 901', 'Sevilla', 'Av. de la Constitución 8'),
        ('Miguel Torres', 'miguel.torres@email.com', '+34 656 789 012', 'Bilbao', 'Gran Vía 30'),
        ('Sara López', 'sara.lopez@email.com', '+34 667 890 123', 'Málaga', 'Calle Larios 12'),
        ('David Martín', 'david.martin@email.com', '+34 678 901 234', 'Zaragoza', 'Paseo Independencia 25'),
        ('Elena Sánchez', 'elena.sanchez@email.com', '+34 689 012 345', 'Alicante', 'Av. Maisonnave 18'),
        ('Pablo Fernández', 'pablo.fernandez@email.com', '+34 690 123 456', 'Murcia', 'Gran Vía 5'),
        ('Carmen Romero', 'carmen.romero@email.com', '+34 601 234 567', 'Palma', 'Calle Jaime III 20'),
        ('Jorge Navarro', 'jorge.navarro@email.com', '+34 612 345 001', 'Granada', 'Calle Gran Vía 10'),
        ('Isabel Molina', 'isabel.molina@email.com', '+34 623 456 002', 'Valladolid', 'Calle Santiago 8'),
        ('Raúl Castillo', 'raul.castillo@email.com', '+34 634 567 003', 'Córdoba', 'Av. Gran Capitán 14'),
        ('Nuria Ortiz', 'nuria.ortiz@email.com', '+34 645 678 004', 'San Sebastián', 'Calle Getaria 3'),
        ('Alberto Vargas', 'alberto.vargas@email.com', '+34 656 789 005', 'Gijón', 'Calle Corrida 22'),
        ('Patricia Reyes', 'patricia.reyes@email.com', '+34 667 890 006', 'Santander', 'Paseo Pereda 7'),
        ('Fernando Rivas', 'fernando.rivas@email.com', '+34 678 901 007', 'Toledo', 'Calle Comercio 12'),
        ('Adriana Campos', 'adriana.campos@email.com', '+34 689 012 008', 'Salamanca', 'Plaza Mayor 5'),
        ('Héctor Delgado', 'hector.delgado@email.com', '+34 690 123 009', 'Pamplona', 'Av. Carlos III 18'),
        ('Silvia Peña', 'silvia.pena@email.com', '+34 601 234 010', 'Santiago', 'Rúa do Franco 3'),
    ]
    customers = create_batch('res.partner', [{
        'name': n, 'email': e, 'phone': p, 'city': c, 'street': s, 'customer_rank': 1,
    } for n, e, p, c, s in customer_info])
    print(f'  Created {len(customers)} customers')

    # ──────────────────────────────────────────
    # 5. VEHICLES
    # ──────────────────────────────────────────
    license_plates = set()
    def gen_plate():
        letters = 'BCDFGHJKLMNPQRSTVWXYZ'
        while True:
            plate = f'{random.randint(1000,9999)}{random.choice(letters)}{random.choice(letters)}{random.choice(letters)}'
            if plate not in license_plates:
                license_plates.add(plate)
                return plate

    colors = ['Blanco', 'Negro', 'Gris', 'Azul', 'Rojo', 'Plateado', 'Verde', 'Marrón']
    fuel_types = ['diesel', 'gasoline', 'full_hybrid', 'electric']

    vehicle_list = []
    for i, model in enumerate(models):
        status = 'sold' if i < 8 else ('in_service' if i < 10 else ('to_order' if i < 13 else 'available'))
        purchase_year = random.randint(2020, 2025)
        vehicle_list.append({
            'name': f'{model.brand_id.name} {model.name}',
            'model_id': model.id,
            'license_plate': gen_plate(),
            'vin_sn': f'VIN{random.randint(10**16, 10**17-1)}',
            'color': rand_choice(colors),
            'fuel_type': rand_choice(fuel_types),
            'vehicle_status': status,
            'seats': random.choice([4, 5, 5, 5, 7]),
            'doors': random.choice([4, 4, 4, 5]),
            'co2': random.randint(80, 220),
            'driver_id': False,
            'net_car_value': random.randint(15000, 60000),
            'car_value': random.randint(18000, 70000),
            'model_year': purchase_year,
            'acquisition_date': rand_date(datetime(purchase_year, 1, 1), datetime(purchase_year, 12, 31)),
        })
    vehicles = create_batch('fleet.vehicle', vehicle_list)
    print(f'  Created {len(vehicles)} vehicles')

    # ── Tags por estado ──
    status_tags = {
        'available': env['fleet.vehicle.tag'].create({'name': 'En stock', 'color': 10}),
        'sold': env['fleet.vehicle.tag'].create({'name': 'Vendido', 'color': 7}),
        'reserved': env['fleet.vehicle.tag'].create({'name': 'Reservado', 'color': 3}),
        'in_service': env['fleet.vehicle.tag'].create({'name': 'En servicio', 'color': 2}),
        'to_order': env['fleet.vehicle.tag'].create({'name': 'A pedir', 'color': 11}),
    }
    for v in vehicles:
        tag = status_tags.get(v.vehicle_status)
        if tag:
            v.write({'tag_ids': [(4, tag.id)]})
    print(f'  Tagged {len(vehicles)} vehicles by status')

    # ──────────────────────────────────────────
    # 6. LEADS
    # ──────────────────────────────────────────
    lead_stages = env['crm.stage'].search([], order='sequence')
    if not lead_stages:
        lead_stages = env['crm.stage'].create([
            {'name': 'Nuevo', 'sequence': 10},
            {'name': 'Calificado', 'sequence': 20},
            {'name': 'Propuesta', 'sequence': 30},
            {'name': 'Ganado', 'sequence': 40},
            {'name': 'Perdido', 'sequence': 50},
        ])

    lead_sources = ['website', 'phone', 'referral', 'social', 'walkin', 'email_marketing']

    leads = env['crm.lead']
    for _ in range(25):
        customer = rand_choice(customers)
        model = rand_choice(models)
        stage = rand_choice(lead_stages)
        expected_revenue = random.randint(15000, 65000) + random.randint(0, 30000)
        if 'Ganado' in stage.name:
            prob = 100
        elif 'Perdido' in stage.name:
            prob = 0
        elif 'Propuesta' in stage.name:
            prob = random.randint(60, 90)
        elif 'Calificado' in stage.name:
            prob = random.randint(30, 60)
        else:
            prob = random.randint(10, 30)
        try:
            leads |= env['crm.lead'].create({
                'name': f'{customer.name} - {model.brand_id.name} {model.name}',
                'partner_id': customer.id,
                'expected_revenue': expected_revenue,
                'probability': prob,
                'stage_id': stage.id,
                'source': rand_choice(lead_sources),
                'description': f'Cliente interesado en {model.brand_id.name} {model.name}',
                'city': customer.city,
                'phone': customer.phone,
                'email_from': customer.email,
                'user_id': user.id,
                'date_deadline': rand_date(today - timedelta(days=30), today + timedelta(days=60)),
            })
        except Exception as e:
            print(f'  Skip lead: {e}')
    print(f'  Created {len(leads)} leads')

    # ──────────────────────────────────────────
    # 7. SALE ORDERS
    # ──────────────────────────────────────────
    sale_states = ['draft', 'sent', 'sale', 'done']
    sale_records = []

    for i in range(20):
        customer = rand_choice(customers)
        product = rand_choice(products)
        qty = 1
        price = product.list_price * (0.9 + random.random() * 0.1)
        state = sale_states[i % 4] if random.random() > 0.2 else 'draft'
        order_date = rand_date(today - timedelta(days=120), today)
        try:
            so = env['sale.order'].create({
                'partner_id': customer.id,
                'user_id': user.id,
                'date_order': order_date.strftime('%Y-%m-%d %H:%M:%S'),
                'order_line': [(0, 0, {
                    'product_id': product.id,
                    'product_uom_qty': qty,
                    'price_unit': price,
                })],
            })
            if state in ('sale', 'done'):
                so.action_confirm()
            if state == 'done':
                inv = so._create_invoices(final=True)
                if inv:
                    inv.action_post()
            sale_records.append(so)
        except Exception as e:
            print(f'  Skip sale order: {e}')

    print(f'  Created {len(sale_records)} sale orders')

    # ──────────────────────────────────────────
    # 8. PURCHASE ORDERS
    # ──────────────────────────────────────────
    po_states = ['draft', 'sent', 'purchase', 'done']
    po_records = []

    for i in range(12):
        product = rand_choice(products)
        qty = random.randint(1, 5)
        price = product.standard_price * (0.85 + random.random() * 0.15)
        state = po_states[i % 4]
        order_date = rand_date(today - timedelta(days=90), today)
        try:
            po = env['purchase.order'].create({
                'partner_id': rand_choice(customers).id,
                'date_order': order_date.strftime('%Y-%m-%d %H:%M:%S'),
                'order_line': [(0, 0, {
                    'product_id': product.id,
                    'product_qty': qty,
                    'price_unit': price,
                    'date_planned': (order_date + timedelta(days=random.randint(7, 30))).strftime('%Y-%m-%d'),
                })],
            })
            if state in ('purchase', 'done'):
                po.button_confirm()
            po_records.append(po)
        except Exception as e:
            print(f'  Skip purchase order: {e}')

    print(f'  Created {len(po_records)} purchase orders')

    # ──────────────────────────────────────────
    # 9. REPAIR ORDERS
    # ──────────────────────────────────────────
    repair_states = ['draft', 'confirmed', 'under_repair', 'done']
    repair_records = []

    for i in range(10):
        state = rand_choice(repair_states)
        try:
            repair = env['repair.order'].create({
                'name': f'Reparación #{i+1}',
                'product_id': products[0].id,
                'partner_id': rand_choice(customers).id,
                'user_id': user.id,
                'internal_notes': f'Revisión general y mantenimiento',
                'schedule_date': rand_date(today - timedelta(days=45), today + timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S'),
                'tag_ids': [(6, 0, [])],
            })
            repair_records.append(repair)
        except Exception as e:
            print(f'  Skip repair: {e}')

    print(f'  Created {len(repair_records)} repair orders')

    # ──────────────────────────────────────────
    # 10. FINANCING
    # ──────────────────────────────────────────
    plan_types = [
        ('Plan Estándar 48 meses', 48, 5.5, 15),
        ('Plan Premium 36 meses', 36, 4.2, 25),
        ('Plan Económico 60 meses', 60, 7.0, 10),
        ('Plan Joven 72 meses', 72, 8.0, 5),
    ]
    fin_plans = create_batch('nexo.financing.plan', [{
        'name': n, 'months': m, 'interest_rate': r, 'down_payment_percent': d,
    } for n, m, r, d in plan_types])

    fin_requests = []
    for _ in range(10):
        try:
            req = env['nexo.financing.request'].create({
                'partner_id': rand_choice(customers).id,
                'plan_id': rand_choice(fin_plans).id,
                'vehicle_id': rand_choice(vehicles).id,
                'vehicle_price': random.randint(20000, 50000),
                'status': rand_choice(['draft', 'submitted', 'approved', 'rejected']),
                'salesperson_id': user.id,
                'date': rand_date(today - timedelta(days=90), today).strftime('%Y-%m-%d'),
            })
            fin_requests.append(req)
        except Exception as e:
            print(f'  Skip financing: {e}')

    print(f'  Created {len(fin_plans)} plans, {len(fin_requests)} requests')

    # ──────────────────────────────────────────
    # 11. COMMISSIONS
    # ──────────────────────────────────────────
    commissions = []
    for i in range(10):
        emp = rand_choice(employees)
        sale = rand_choice(sale_records) if sale_records else False
        if not sale:
            continue
        try:
            comm = env['nexo.commission'].create({
                'employee_id': emp.id,
                'sale_order_id': sale.id,
                'amount': round(random.uniform(100, 2000), 2),
                'base_amount': sale.amount_total,
                'paid': rand_choice([True, False]),
                'date': rand_date(today - timedelta(days=90), today).strftime('%Y-%m-%d'),
            })
            commissions.append(comm)
        except Exception as e:
            print(f'  Skip commission: {e}')

    print(f'  Created {len(commissions)} commissions')

    # ──────────────────────────────────────────
    # 12. INVENTORY MOVEMENTS
    # ──────────────────────────────────────────
    inv_types = ['purchase', 'consignment', 'transfer', 'return', 'trade_in']
    inv_moves = []
    for _ in range(10):
        vehicle = rand_choice(vehicles)
        try:
            inv = env['nexo.vehicle.inventory'].create({
                'vehicle_id': vehicle.id,
                'type': rand_choice(inv_types),
                'date_in': rand_date(today - timedelta(days=60), today).strftime('%Y-%m-%d'),
                'cost': random.randint(10000, 50000),
                'notes': f'Inventario de {vehicle.name}',
                'supplier_id': rand_choice(customers).id,
                'state': rand_choice(['draft', 'done']),
            })
            inv_moves.append(inv)
        except Exception as e:
            print(f'  Skip inventory: {e}')

    print(f'  Created {len(inv_moves)} inventory movements')

    # ──────────────────────────────────────────
    # SUMMARY
    # ──────────────────────────────────────────
    print()
    print('=== SEED COMPLETE ===')
    print(f'  Brands: {len(brands)}')
    print(f'  Models: {len(models)}')
    print(f'  Products: {len(products)}')
    print(f'  Employees: {len(employees)}')
    print(f'  Customers: {len(customers)}')
    print(f'  Vehicles: {len(vehicles)}')
    print(f'  Leads: {len(leads)}')
    print(f'  Sale Orders: {len(sale_records)}')
    print(f'  Purchase Orders: {len(po_records)}')
    print(f'  Repair Orders: {len(repair_records)}')
    print(f'  Financing Plans: {len(fin_plans)}')
    print(f'  Financing Requests: {len(fin_requests)}')
    print(f'  Commissions: {len(commissions)}')
    print(f'  Inventory Movements: {len(inv_moves)}')


if __name__ == '__main__':
    import odoo
    from odoo.tools import config as odoo_config
    odoo_config.parse_config([
        '--addons-path=/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons',
        '-d', 'dealer_db', '--db_host=db', '--db_port=5432',
        '--db_user=odoo', '--db_password=odoo',
    ])
    from odoo.modules.registry import Registry
    registry = Registry('dealer_db')
    with registry.cursor() as cr:
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        seed(env)
        cr.commit()
