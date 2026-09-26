import re

fps = [
    ("3213 Ridgely Drive, Vestavia Hills, AL", "215 RIDGELY DR, VESTAVIA HILLS, AL"), # FP: Should conflict
    ("1815 Mill Lane, Southold, NY", "1826 MILL LANE, SOUTHOLD, NY"), # FP: Should conflict
    ("Suite 2, 100 Main St", "100 Main St, Suite 2"), # FN: Should NOT conflict
    ("3213 Ridgely Drive, 35243", "215 RIDGELY DR, 35243"), # FP: SHOULD conflict
    ("C-636, Delhi, South Delhi, Block C Sangam Vihar", "C-639, Block C Sangam Vihar, Delhi, South Delhi, DL"), # FP: SHOULD conflict
    ("PO Box 1234, 100 Main St", "100 Main St"), # FN: Should NOT conflict
    ("3213 Ridgely Drive, Vestavia Hills, AL 35243", "Vestavia Hills, AL 35243"), # FN: Should NOT conflict
]

def extract_building_number(addr):
    # 1. Remove PO Boxes
    a = re.sub(r'(?i)\b(?:p\.?o\.?\s*box|post\s*box|box)\s*\d+\b', '', addr)
    # 2. Remove Zip / PIN Codes (5 or 6 digit numbers)
    a = re.sub(r'\b\d{5,6}\b', '', a)
    # 3. Find first remaining number
    m = re.search(r'\b\d+\b', a)
    return m.group(0) if m else None

def extract_all_building_numbers(addr):
    a = re.sub(r'(?i)\b(?:p\.?o\.?\s*box|post\s*box|box)\s*\d+\b', '', addr)
    a = re.sub(r'\b\d{5,6}\b', '', a)
    return set(re.findall(r'\b\d+\b', a))

for a1, a2 in fps:
    n1 = extract_all_building_numbers(a1)
    n2 = extract_all_building_numbers(a2)
    f1 = extract_building_number(a1)
    f2 = extract_building_number(a2)
    
    conflict = False
    if f1 and f2:
        if f1 not in n2 and f2 not in n1:
            conflict = True
            
    print(f"A1: {a1}")
    print(f"A2: {a2}")
    print(f"Extracted firsts: {f1}, {f2}")
    print(f"Conflict: {conflict}")
    print("-" * 40)
