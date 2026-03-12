import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime
import os

fake = Faker()

np.random.seed()
random.seed()

# random rows between 29 and 1700
rows_to_generate = random.randint(29,1700)

specialties = [
    "Cardiology",
    "Endocrinology",
    "Oncology",
    "Psychiatry",
    "Dermatology",
    "Primary Care"
]

payer_types = [
    "Commercial",
    "Medicare",
    "Medicaid",
    "Cash"
]

records = []

current_time = datetime.utcnow()

for _ in range(rows_to_generate):

    trx = np.random.poisson(3)
    nrx = max(0, int(trx * np.random.uniform(0.2,0.7)))

    records.append({
        "run_timestamp": current_time,
        "rx_date": current_time.date(),
        "npi": random.randint(1000000000,9999999999),
        "ndc": f"{random.randint(10000,99999)}-{random.randint(1000,9999)}",
        "pharmacy_id": f"PH{random.randint(1,1200):05}",
        "trx": trx,
        "nrx": nrx,
        "patient_age_group": random.choice(["0-18","19-35","36-50","51-65","65+"]),
        "payer_type": random.choice(payer_types),
        "zip": random.randint(10000,99999),
        "territory_id": f"T{random.randint(0,49):03}",
        "specialty": random.choice(specialties)
    })

df = pd.DataFrame(records)

file_path = "prescriptions_stream.csv"

# append instead of overwrite
if os.path.exists(file_path):
    df.to_csv(file_path, mode="a", header=False, index=False)
else:
    df.to_csv(file_path, index=False)

print(f"{rows_to_generate} rows generated")
