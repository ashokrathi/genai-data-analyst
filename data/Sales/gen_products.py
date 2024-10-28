import random
import string

# Function to generate random UPC (12 digits)
def generate_upc():
    return ''.join(random.choices(string.digits, k=12))

# Sample list of auto industry product names
product_names = [
    "Engine Oil", "Brake Pads", "Air Filter", "Spark Plug", "Windshield Wipers",
    "Car Battery", "Radiator", "Tire", "Alternator", "Headlight Bulb",
    "Fuel Pump", "Brake Rotors", "Ignition Coil", "Oil Filter", "Transmission Fluid",
    "Wheel Hub", "Exhaust Pipe", "Shock Absorbers", "Clutch Kit", "Muffler",
    "Timing Belt", "Steering Wheel", "Fuel Injector", "Turbocharger", "Car Jack",
    "Seat Covers", "Dash Cam", "Floor Mats", "Car Stereo", "GPS Navigation"
]

# Generate 30 records
products = []
for i in range(1, 31):
    product_id = f'P{i:03d}'  # Example product_id format: P001, P002, ...
    upc = generate_upc()
    name = product_names[i % len(product_names)]
    products.append((product_id, upc, name))

# Display the generated records
for product in products:
    print(product)

