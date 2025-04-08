import csv
import random

# -------------------------------------------------------------------
# 1. INSURERS DATA
# -------------------------------------------------------------------
# We'll store them in a list of dicts:
insurers_data = [
    {
        "insurer_id": 1,
        "name": "Axis Max Life",
        "claim_settlement_ratio": 99.5,
        "amount_settlement_ratio": 95.5,
        "complaints_volume": 7.3
    },
    {
        "insurer_id": 2,
        "name": "Bajaj Allianz Life",
        "claim_settlement_ratio": 99.1,
        "amount_settlement_ratio": 93.0,
        "complaints_volume": 4.4
    },
    {
        "insurer_id": 3,
        "name": "ICICI Prudential",
        "claim_settlement_ratio": 97.5,
        "amount_settlement_ratio": 92.1,
        "complaints_volume": 14.3
    },
    {
        "insurer_id": 4,
        "name": "HDFC Life",
        "claim_settlement_ratio": 99.2,
        "amount_settlement_ratio": 87.3,
        "complaints_volume": 2.0
    }
]

# -------------------------------------------------------------------
# 2. TERM PLANS
# -------------------------------------------------------------------
# We'll create 2 plans per insurer (some random differences in min/max age & coverage).
# You can adjust as needed.
plans_data = []
plan_id_counter = 1

# We'll define possible plan "templates" we can assign randomly to each insurer
# just to give slight variety in coverage & age/term ranges.
possible_plans = [
    {
        "min_cover": 500000,   # 5L
        "max_cover": 150000000, # 15Cr
        "min_term": 5,
        "max_term": 50,
        "min_age": 18,
        "max_age": 70,
        "free_riders": "",
        "paid_riders": "Critical Illness, Accidental Death"
    },
    {
        "min_cover": 1000000,    # 10L
        "max_cover": 120000000,   # 12Cr
        "min_term": 5,
        "max_term": 55,
        "min_age": 20,
        "max_age": 75,
        "free_riders": "Critical Illness",
        "paid_riders": "Accidental Death"
    }
]

random.seed(42)  # For reproducibility

for insurer in insurers_data:
    # Fixed plans per insurer instead of random
    plans_by_insurer = {
        "ICICI Prudential": ["iProtect Smart", "iProtect Super"],
        "Bajaj Allianz Life": ["Smart Protect Goal", "Life Guard"], 
        "HDFC Life": ["Click 2 Protect Life", "HDFC Life Sanchay Plus"],
        "Axis Max Life": ["Smart Secure Plus", "Online Term Plan Plus"]
    }
    
    plan_links_by_insurer = {
        "ICICI Prudential": ["https://www.icicipru.com/insurance/term-insurance/iProtect-Smart", "https://www.icicipru.com/insurance/term-insurance/iProtect-Super"],
        "Bajaj Allianz Life": ["https://www.bajajallianz.com/term-insurance/smart-protect-goal", "https://www.bajajallianz.com/term-insurance/life-guard"], 
        "HDFC Life": ["https://www.hdfclife.com/click2protectlife", "https://www.hdfclife.com/hdfclifesanchayplus"],
        "Axis Max Life": ["https://www.axismaxlife.com/smartsecureplus", "https://www.axismaxlife.com/onlinetermplanplus"]
    }
    
    plans = plans_by_insurer[insurer["name"]]
    plan_links = plan_links_by_insurer[insurer["name"]]
    # Use both plan templates in order for each insurer's plans
    for i, plan_name in enumerate(plans):
        plan_template = possible_plans[i % 2]  # Alternates between 0 and 1
        plan_row = {
            "plan_id": plan_id_counter,
            "insurer_id": insurer["insurer_id"],
            "plan_name": plan_name,
            "plan_link": plan_links[i],
            "min_cover": plan_template["min_cover"],
            "max_cover": plan_template["max_cover"], 
            "min_term": plan_template["min_term"],
            "max_term": plan_template["max_term"],
            "min_age": plan_template["min_age"],
            "max_age": plan_template["max_age"],
            "free_riders": plan_template["free_riders"],
            "paid_riders": plan_template["paid_riders"]
        }
        plans_data.append(plan_row)
        plan_id_counter += 1


# -------------------------------------------------------------------
# 3. PREMIUMS TABLE
# -------------------------------------------------------------------
# We'll produce combos for each plan:
#   Age from 25 to 40
#   Terms in [5, 10, 15, 20, 25, 30] (some might exceed plan's max_term though)
#   Coverage amounts: 10L, 20L, 50L, 1Cr, 2Cr, 3Cr, 4Cr, 5Cr (in rupees)
#
# required_min_income => some simple formula
# annual_premium => another formula + slight randomization
# We'll skip combos that exceed plan's max_cover, or age beyond plan's max_age, or term beyond plan's max_term, etc.

coverage_bands = [
    (0, 1000000),
    (1000000, 2000000),
    (2000000, 3000000),
    (3000000, 4000000),
    (4000000, 5000000),
    (5000000, 6000000),
    (6000000, 7000000),
    (7000000, 8000000),
    (8000000, 9000000),
    (9000000, 10000000),
    (10000000, 15000000),
    (15000000, 20000000),
    (20000000, 25000000),
    (25000000, 30000000),
    (30000000, 35000000),
    (35000000, 40000000),
    (40000000, 45000000),
    (45000000, 50000000),
    (50000000, 55000000),
    (55000000, 60000000),
    (60000000, 65000000),
    (65000000, 70000000),
    (70000000, 75000000),
    (75000000, 80000000),
    (80000000, 85000000),
    (85000000, 90000000),
    (90000000, 95000000),
    (95000000, 100000000)
]

age_bands = [(i, i+1) for i in range(20, 75)]

term_bands = [
    (1, 4),
    (4, 7), 
    (7, 10),
    (10, 13),
    (13, 16),
    (16, 19),
    (19, 22),
    (22, 25),
    (25, 28),
    (28, 31),
    (31, 34),
    (34, 37),
    (37, 40),
    (40, 45),
    (45, 50),
    (50, 55),
    (55, 60),
]

premiums_data = []
premium_id_counter = 1

def compute_required_income(coverage_min, coverage_max):
    # We'll approximate based on coverage_max
    return coverage_max // 20  # e.g. 1Cr => 5L

def compute_annual_premium(age_min, age_max, term_min, term_max, coverage_min, coverage_max):
    # Simple formula: base = coverage_max / 2000
    # add (age_min*50 + term_max*40) * some random factor
    base = coverage_max / 2000
    add_age = age_min * 50
    add_term = term_max * 40
    factor = random.uniform(0.9, 1.1)
    premium = (base + add_age + add_term) * factor
    return int(round(premium))

for plan in plans_data:
        plan_id = plan["plan_id"]
        # for each plan, we might skip coverage or age/term bands that exceed plan's max_age, max_cover, etc.

        for coverage_range in coverage_bands:
            cov_min, cov_max = coverage_range
            # skip if coverage range entirely above plan.max_cover
            if cov_min > plan["max_cover"]:
                continue
            # skip if coverage range entirely below plan.min_cover
            if cov_max < plan["min_cover"]:
                continue

            # clamp coverage bands to fit plan's actual min/max
            cov_min_clamped = max(cov_min, plan["min_cover"])
            cov_max_clamped = min(cov_max, plan["max_cover"])

            for age_range in age_bands:
                a_min, a_max = age_range
                # skip if age range is outside plan's min_age, max_age
                if a_min > plan["max_age"]:
                    continue
                if a_max < plan["min_age"]:
                    continue

                # clamp
                a_min_clamped = max(a_min, plan["min_age"])
                a_max_clamped = min(a_max, plan["max_age"])

                for term_range in term_bands:
                    t_min, t_max = term_range
                    # skip if term band outside plan's min_term, max_term
                    if t_min > plan["max_term"]:
                        continue
                    if t_max < plan["min_term"]:
                        continue

                    # clamp
                    t_min_clamped = max(t_min, plan["min_term"])
                    t_max_clamped = min(t_max, plan["max_term"])

                    required_min_inc = compute_required_income(cov_min_clamped, cov_max_clamped)
                    annual_prem = compute_annual_premium(
                        a_min_clamped, a_max_clamped,
                        t_min_clamped, t_max_clamped,
                        cov_min_clamped, cov_max_clamped
                    )

                    row = {
                        "premium_id": premium_id_counter,
                        "plan_id": plan_id,
                        "age_min": a_min_clamped,
                        "age_max": a_max_clamped,
                        "term_min": t_min_clamped,
                        "term_max": t_max_clamped,
                        "coverage_min": cov_min_clamped,
                        "coverage_max": cov_max_clamped,
                        "required_min_income": required_min_inc,
                        "annual_premium": annual_prem
                    }
                    premiums_data.append(row)
                    premium_id_counter += 1

# -------------------------------------------------------------------
# 4. WRITE TO CSV FILES
# -------------------------------------------------------------------
with open("data/insurers.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["insurer_id","name","claim_settlement_ratio","amount_settlement_ratio","complaints_volume"])
    for row in insurers_data:
        writer.writerow([
            row["insurer_id"],
            row["name"],
            row["claim_settlement_ratio"],
            row["amount_settlement_ratio"],
            row["complaints_volume"]
        ])

with open("data/term_plans.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "plan_id", "insurer_id", "plan_name",
        "min_cover", "max_cover",
        "min_term", "max_term",
        "min_age", "max_age",
        "free_riders", "paid_riders",
        "plan_link"
    ])
    for row in plans_data:
        writer.writerow([
            row["plan_id"],
            row["insurer_id"],
            row["plan_name"],
            row["min_cover"],
            row["max_cover"],
            row["min_term"],
            row["max_term"],
            row["min_age"],
            row["max_age"],
            row["free_riders"],
            row["paid_riders"],
            row["plan_link"]
        ])

with open("data/premiums.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "premium_id","plan_id","age_min","age_max","term_min","term_max","coverage_min","coverage_max",
        "required_min_income","annual_premium"
    ])
    for row in premiums_data:
        writer.writerow([
            row["premium_id"],
            row["plan_id"],
            row["age_min"],
            row["age_max"],
            row["term_min"],
            row["term_max"],
            row["coverage_min"],
            row["coverage_max"],
            row["required_min_income"],
            row["annual_premium"]
        ])

import sqlite3

def create_tables(conn):
    cursor = conn.cursor()
    
    # ---- Drop tables if they already exist (in reverse FK order)
    cursor.execute("DROP TABLE IF EXISTS premiums;")
    cursor.execute("DROP TABLE IF EXISTS term_plans;")
    cursor.execute("DROP TABLE IF EXISTS insurers;")

    # -- Create insurers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS insurers (
        insurer_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        claim_settlement_ratio REAL,
        amount_settlement_ratio REAL,
        complaints_volume REAL
    );
    """)

    # -- Create term_plans table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS term_plans (
        plan_id INTEGER PRIMARY KEY,
        insurer_id INTEGER NOT NULL,
        plan_name TEXT NOT NULL,
        min_cover INTEGER NOT NULL,
        max_cover INTEGER NOT NULL,
        min_term INTEGER NOT NULL,
        max_term INTEGER NOT NULL,
        min_age INTEGER NOT NULL,
        max_age INTEGER NOT NULL,
        free_riders TEXT,
        paid_riders TEXT,
        plan_link TEXT,
        FOREIGN KEY (insurer_id) REFERENCES insurers(insurer_id)
    );
    """)

    # -- Create premiums table
    cursor.execute("""
    CREATE TABLE premiums (
        premium_id INTEGER PRIMARY KEY,
        plan_id INTEGER NOT NULL,
        age_min INTEGER NOT NULL,
        age_max INTEGER NOT NULL,
        term_min INTEGER NOT NULL,
        term_max INTEGER NOT NULL,
        coverage_min INTEGER NOT NULL,
        coverage_max INTEGER NOT NULL,
        required_min_income INTEGER NOT NULL,
        annual_premium INTEGER NOT NULL,
        FOREIGN KEY (plan_id) REFERENCES term_plans(plan_id)
    );
    """)

    conn.commit()
    print("✅ Tables created successfully.")

def insert_data_into_db(conn, insurers_data, plans_data, premiums_data):
    cursor = conn.cursor()

    # -- INSERT INTO insurers
    for row in insurers_data:
        cursor.execute("""
            INSERT INTO insurers (
                insurer_id, name, claim_settlement_ratio, amount_settlement_ratio, complaints_volume
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            row['insurer_id'],
            row['name'],
            row['claim_settlement_ratio'],
            row['amount_settlement_ratio'],
            row['complaints_volume']
        ))

    # -- INSERT INTO term_plans
    for row in plans_data:
        cursor.execute("""
            INSERT INTO term_plans (
                plan_id, insurer_id, plan_name,
                min_cover, max_cover,
                min_term, max_term,
                min_age, max_age,
                free_riders, paid_riders,
                plan_link
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row['plan_id'],
            row['insurer_id'],
            row['plan_name'],
            row['min_cover'],
            row['max_cover'],
            row['min_term'],
            row['max_term'],
            row['min_age'],
            row['max_age'],
            row['free_riders'],
            row['paid_riders'],
            row['plan_link']
        ))

    # -- INSERT INTO premiums
    for row in premiums_data:
        cursor.execute("""
            INSERT INTO premiums (
                premium_id, plan_id, age_min, age_max, term_min, term_max, coverage_min, coverage_max, required_min_income, annual_premium
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row['premium_id'],
            row['plan_id'],
            row['age_min'],
            row['age_max'],
            row['term_min'],
            row['term_max'],
            row['coverage_min'],
            row['coverage_max'],
            row['required_min_income'],
            row['annual_premium']
        ))

    conn.commit()
    print("✅ All mock data inserted into database successfully.")
    
# Step 1: Open or create your SQLite DB
conn = sqlite3.connect("data/term_insurance.db")

# Step 2: (Optional) Create tables first if not already done
create_tables(conn)

# Step 3: Call the insertion function
insert_data_into_db(conn, insurers_data, plans_data, premiums_data)

# Step 4: Done
conn.close()