import os
import sys
import math
import random
from datetime import date, timedelta
from dotenv import load_dotenv

# Load env from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

from supabase import create_client

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
if not url or not key:
    print('ERROR: Missing SUPABASE_URL or SERVICE_ROLE_KEY in .env')
    sys.exit(1)

supabase = create_client(url, key)
print('Connected to Supabase')

# ─── CONFIG ───
random.seed(42)  # Reproducible data

CATEGORIES = {
    'filters': {
        'prefix': 'FLT', 'count': 15,
        'names': ['Oil Filter', 'Air Filter', 'Fuel Filter', 'Hydraulic Filter',
                  'Coolant Filter', 'Cabin Air Filter', 'Transmission Filter',
                  'Diesel Particulate Filter', 'Lube Filter', 'Water Separator',
                  'Breather Filter', 'Exhaust Filter', 'Intake Filter',
                  'Bypass Oil Filter', 'Centrifugal Filter'],
        'moq': (100, 500), 'weight': (0.2, 1.5),
        'cbm': (0.002, 0.01), 'price': (5, 30),
        'suppliers': ['SUP-A', 'SUP-B', 'SUP-C', 'SUP-F'],
    },
    'gaskets': {
        'prefix': 'GSK', 'count': 15,
        'names': ['Head Gasket', 'Exhaust Manifold Gasket', 'Intake Gasket',
                  'Valve Cover Gasket', 'Oil Pan Gasket', 'Water Pump Gasket',
                  'Thermostat Gasket', 'EGR Valve Gasket', 'Turbo Gasket',
                  'Timing Cover Gasket', 'Rear Main Seal', 'Front Crankshaft Seal',
                  'Rocker Cover Gasket', 'Flywheel Housing Gasket', 'Coolant Pipe Gasket'],
        'moq': (200, 800), 'weight': (0.05, 0.5),
        'cbm': (0.001, 0.005), 'price': (2, 15),
        'suppliers': ['SUP-B', 'SUP-C', 'SUP-F'],
    },
    'engine_parts': {
        'prefix': 'ENG', 'count': 15,
        'names': ['Turbo Actuator', 'Fuel Injector', 'Piston Assembly',
                  'Connecting Rod', 'Crankshaft Bearing', 'Camshaft',
                  'Cylinder Liner', 'Rocker Arm', 'Valve Spring',
                  'Push Rod', 'Flywheel', 'Oil Pump',
                  'Water Pump Assembly', 'Exhaust Manifold', 'Intake Manifold'],
        'moq': (50, 200), 'weight': (2.0, 25.0),
        'cbm': (0.01, 0.5), 'price': (30, 150),
        'suppliers': ['SUP-A', 'SUP-D', 'SUP-E'],
    },
    'electrical': {
        'prefix': 'ELC', 'count': 15,
        'names': ['ECU Module', 'Alternator', 'Starter Motor',
                  'Glow Plug', 'Wiring Harness', 'Sensor Assembly',
                  'Relay Module', 'Ignition Coil', 'Battery Cable',
                  'Solenoid Valve', 'Control Unit', 'Speed Sensor',
                  'Pressure Transducer', 'Temperature Sender', 'Voltage Regulator'],
        'moq': (50, 300), 'weight': (0.1, 2.0),
        'cbm': (0.002, 0.02), 'price': (10, 80),
        'suppliers': ['SUP-B', 'SUP-D', 'SUP-F'],
    },
}

SUPPLIERS = [
    {'id': 'SUP-A', 'name': 'Precision Parts Co.', 'region': 'North America',
     'lead_time_days': 10, 'quality_score': 95, 'delivery_performance': 92,
     'cost_rating': 70, 'contact_email': 'orders@precisionparts.com'},
    {'id': 'SUP-B', 'name': 'Global Components Ltd.', 'region': 'Europe',
     'lead_time_days': 14, 'quality_score': 85, 'delivery_performance': 88,
     'cost_rating': 82, 'contact_email': 'sales@globalcomponents.eu'},
    {'id': 'SUP-C', 'name': 'ValueSource MFG', 'region': 'Southeast Asia',
     'lead_time_days': 21, 'quality_score': 72, 'delivery_performance': 78,
     'cost_rating': 95, 'contact_email': 'orders@valuesourcemfg.asia'},
    {'id': 'SUP-D', 'name': 'RapidShip Industries', 'region': 'North America',
     'lead_time_days': 7, 'quality_score': 82, 'delivery_performance': 90,
     'cost_rating': 68, 'contact_email': 'rush@rapidship.com'},
    {'id': 'SUP-E', 'name': 'Apex Engineering', 'region': 'Europe',
     'lead_time_days': 28, 'quality_score': 98, 'delivery_performance': 85,
     'cost_rating': 60, 'contact_email': 'procurement@apexeng.eu'},
    {'id': 'SUP-F', 'name': 'SteadyFlow Supply', 'region': 'Asia Pacific',
     'lead_time_days': 14, 'quality_score': 85, 'delivery_performance': 85,
     'cost_rating': 85, 'contact_email': 'orders@steadyflow.com'},
]

SCORING_WEIGHTS = [
    {'category': 'filters', 'delivery_weight': 0.25, 'quality_weight': 0.35,
     'lead_time_weight': 0.15, 'cost_weight': 0.25},
    {'category': 'gaskets', 'delivery_weight': 0.30, 'quality_weight': 0.30,
     'lead_time_weight': 0.20, 'cost_weight': 0.20},
    {'category': 'engine_parts', 'delivery_weight': 0.20, 'quality_weight': 0.40,
     'lead_time_weight': 0.15, 'cost_weight': 0.25},
    {'category': 'electrical', 'delivery_weight': 0.30, 'quality_weight': 0.25,
     'lead_time_weight': 0.25, 'cost_weight': 0.20},
]

CONTAINER_SPECS = [
    {'type': '20ft', 'max_weight_kg': 28000, 'max_cbm': 33.2, 'base_cost_usd': 2500},
    {'type': '40ft', 'max_weight_kg': 28500, 'max_cbm': 67.6, 'base_cost_usd': 4200},
]

# ─── PRICE MULTIPLIERS PER SUPPLIER ───
PRICE_MULTIPLIERS = {
    'SUP-A': 1.15,  # Premium
    'SUP-B': 1.00,  # Baseline
    'SUP-C': 0.80,  # Cheapest
    'SUP-D': 1.20,  # Fast = expensive
    'SUP-E': 1.25,  # Best quality = most expensive
    'SUP-F': 0.95,  # Slightly below baseline
}

# ─── SEED FUNCTIONS ───

def seed_suppliers():
    print('Seeding suppliers...')
    supabase.table('suppliers').upsert(SUPPLIERS).execute()
    print(f'  {len(SUPPLIERS)} suppliers seeded')

def seed_products():
    print('Seeding products...')
    products = []
    for cat_name, cat in CATEGORIES.items():
        for i in range(cat['count']):
            sku = f"{cat['prefix']}-{i+1:03d}"
            products.append({
                'sku': sku,
                'name': cat['names'][i],
                'category': cat_name,
                'moq': random.randint(*cat['moq']),
                'unit_weight_kg': round(random.uniform(*cat['weight']), 3),
                'unit_cbm': round(random.uniform(*cat['cbm']), 6),
                'unit_price_usd': round(random.uniform(*cat['price']), 2),
            })
    supabase.table('products').upsert(products).execute()
    print(f'  {len(products)} products seeded')
    return products

def seed_supplier_products(products):
    print('Seeding supplier-product mappings...')
    mappings = []
    for prod in products:
        cat = CATEGORIES[prod['category']]
        for sup_id in cat['suppliers']:
            mult = PRICE_MULTIPLIERS[sup_id]
            mappings.append({
                'supplier_id': sup_id,
                'sku': prod['sku'],
                'unit_price': round(prod['unit_price_usd'] * mult, 2),
                'moq_override': None,
            })
    supabase.table('supplier_products').upsert(mappings).execute()
    print(f'  {len(mappings)} supplier-product mappings seeded')

def seed_forecasts(products):
    print('Seeding forecasts...')
    forecasts = []
    start_date = date(2025, 4, 1)  # 12 months: Apr 2025 - Mar 2026
    historical_months = 9  # Apr 2025 - Dec 2025 have actuals

    for prod in products:
        base_demand = random.randint(100, 2000)
        amplitude = random.uniform(0.2, 0.4)
        noise_std = base_demand * random.uniform(0.10, 0.25)

        for m in range(12):
            period = date(start_date.year + (start_date.month + m - 1) // 12,
                         (start_date.month + m - 1) % 12 + 1, 1)
            seasonal = 1 + amplitude * math.sin(2 * math.pi * m / 12)
            forecast_qty = max(1, int(base_demand * seasonal))

            actual_qty = None
            if m < historical_months:
                noise = random.gauss(0, noise_std)
                actual_qty = max(0, int(forecast_qty + noise))

            forecasts.append({
                'sku': prod['sku'],
                'period': period.isoformat(),
                'forecast_qty': forecast_qty,
                'actual_qty': actual_qty,
            })

    # Upsert in batches of 200 (Supabase limit)
    for i in range(0, len(forecasts), 200):
        batch = forecasts[i:i+200]
        supabase.table('forecasts').upsert(batch, on_conflict='sku,period').execute()
    print(f'  {len(forecasts)} forecast rows seeded')
    return forecasts

def seed_inventory(products, forecasts):
    print('Seeding inventory...')
    # Calculate average monthly demand per SKU from historical actuals
    demand_by_sku = {}
    for f in forecasts:
        if f['actual_qty'] is not None:
            demand_by_sku.setdefault(f['sku'], []).append(f['actual_qty'])

    inventory = []
    for prod in products:
        actuals = demand_by_sku.get(prod['sku'], [100])
        avg_demand = sum(actuals) / len(actuals)

        inventory.append({
            'sku': prod['sku'],
            'current_stock': int(avg_demand * random.uniform(0.3, 0.8)),
            'in_transit': int(avg_demand * random.uniform(0, 0.3)),
            'safety_stock': int(avg_demand * random.uniform(0.10, 0.20)),
            'buffer_stock': 0,   # Agent 1 will calculate
            'reorder_point': 0,  # Agent 1 will calculate
        })

    supabase.table('inventory').upsert(inventory).execute()
    print(f'  {len(inventory)} inventory records seeded')

def seed_container_specs():
    print('Seeding container specs...')
    supabase.table('container_specs').upsert(CONTAINER_SPECS).execute()
    print(f'  {len(CONTAINER_SPECS)} container specs seeded')

def seed_scoring_weights():
    print('Seeding scoring weights...')
    supabase.table('supplier_scoring_weights').upsert(SCORING_WEIGHTS).execute()
    print(f'  {len(SCORING_WEIGHTS)} scoring weight configs seeded')

# ─── MAIN ───
if __name__ == '__main__':
    print('=== Seeding Supply Chain PO Database ===')
    print()
    seed_suppliers()
    products = seed_products()
    seed_supplier_products(products)
    forecasts = seed_forecasts(products)
    seed_inventory(products, forecasts)
    seed_container_specs()
    seed_scoring_weights()
    print()
    print('=== Seeding Complete ===')
    print('Verify in Supabase Table Editor:')
    print('  - 60 products')
    print('  - 6 suppliers')
    print('  - 180+ supplier_products mappings')
    print('  - 720 forecast rows')
    print('  - 60 inventory records')
    print('  - 2 container specs')
    print('  - 4 scoring weight configs')