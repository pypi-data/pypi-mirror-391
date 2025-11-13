import json
import random
from pathlib import Path

# Load the template data
with open("data/nested_data.json", "r") as f:
    template_data = json.load(f)

# Extract templates from existing headphones
templates = template_data["headphones"]

# Lists for randomization
brands = [
    "AudioZen",
    "FitSound",
    "ProTune",
    "CityBeat",
    "PicoAudio",
    "GameForce",
    "GlobeTrek",
    "ClarityAudio",
    "ValueAudio",
    "PandaPlay",
    "SonicWave",
    "BeatBox",
    "EchoTech",
]
colors = [
    "Matte Black",
    "Neon Green",
    "Silver",
    "Ocean Blue",
    "White",
    "Cosmic Red",
    "Sand Beige",
    "Wood Grain",
    "Black",
    "Rainbow",
    "Rose Gold",
    "Midnight Blue",
    "Pearl White",
]
types = ["Over-Ear", "In-Ear (TWS)", "On-Ear", "Over-Ear (Open-Back)", "In-Ear"]
connections = [
    "Bluetooth 5.2",
    "Bluetooth 5.0",
    "Bluetooth 5.1",
    "Bluetooth 4.2",
    "Wired (3.5mm)",
    "Wired (6.35mm)",
    "USB-C/Wireless 2.4GHz",
]
warehouse_locations = (
    [f"HP-Aisle-{i}{chr(65+j)}" for i in range(1, 6) for j in range(4)]
    + [f"HP-Bin-{i}{chr(65+j)}" for i in range(1, 6) for j in range(4)]
    + [f"HP-Rack-{i}{chr(65+j)}" for i in range(1, 6) for j in range(4)]
)

tag_options = [
    "wireless",
    "premium",
    "travel",
    "noise-cancelling",
    "sport",
    "waterproof",
    "true-wireless",
    "budget",
    "studio",
    "wired",
    "professional",
    "monitoring",
    "commute",
    "bluetooth",
    "active-noise-cancellation",
    "value",
    "mini",
    "cheap",
    "everyday",
    "gaming",
    "pc",
    "console",
    "foldable",
    "audiophile",
    "hifi",
    "basic",
    "in-ear",
    "earbuds",
    "kids",
    "on-ear",
    "safe-volume",
]

adjectives = [
    "Ultra",
    "Pro",
    "Elite",
    "Premium",
    "Classic",
    "Modern",
    "Vintage",
    "Smart",
    "Advanced",
    "Supreme",
]
nouns = [
    "Voyager",
    "Buds",
    "Monitor",
    "Flow",
    "Headset",
    "Companion",
    "Aura",
    "Sound",
    "Wave",
    "Beat",
]


def generate_product_name():
    return f"{random.choice(adjectives)} {random.choice(nouns)} {random.choice(['X', 'Pro', 'Plus', 'Max', 'Air', ''])}"


def generate_headphone():
    product_id = f"HP{random.randint(1, 99999):05d}"
    headphone_type = random.choice(types)
    is_wireless = "Bluetooth" in (connection := random.choice(connections))
    is_wired = "Wired" in connection

    return {
        "product_id": product_id,
        "name": generate_product_name().strip(),
        "type": headphone_type,
        "price": round(random.uniform(19.99, 599.99), 2),
        "specs": {
            "brand": random.choice(brands),
            "color": random.choice(colors),
            "connection": connection,
            "noise_cancellation": (
                random.choice([True, False]) if is_wireless else False
            ),
            "battery_hours": random.randint(4, 40) if is_wireless else 0,
            "driver_size_mm": random.choice([6, 8, 9, 30, 40, 50, 60]),
            "impedance_ohms": random.choice([16, 18, 20, 24, 32, 80, 250]),
            "mic_included": random.choice([True, False]),
            "foldable_design": random.choice([True, False]),
            "warranty_years": random.randint(1, 5),
        },
        "inventory": {
            "stock_level": random.randint(0, 1000),
            "warehouse_location": random.choice(warehouse_locations),
        },
        "tags": random.sample(tag_options, k=random.randint(2, 5)),
    }


# Generate 10,000 records
print("Generating 10,000 headphone records...")
headphones = [generate_headphone() for _ in range(10000)]

output_data = {"headphones": headphones}

# Save to file
output_path = Path("data/nested_10k.json")
with open(output_path, "w") as f:
    json.dump(output_data, f, indent=2)

print(f"✓ Generated {len(headphones)} records")
print(f"✓ Saved to {output_path}")
print(f"✓ File size: {output_path.stat().st_size / (1024*1024):.2f} MB")
