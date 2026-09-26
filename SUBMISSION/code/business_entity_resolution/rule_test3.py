import re

fps = [
    ("Suite 2, 100 Main St", "100 Main St, Suite 2"), # Should NOT conflict
    ("3213 Ridgely Drive, 35243", "215 RIDGELY DR, 35243"), # SHOULD conflict
    ("C-636, Delhi, South Delhi, Block C Sangam Vihar", "C-639, Block C Sangam Vihar, Delhi, South Delhi, DL"), # SHOULD conflict
]

def extract_all_numbers(s):
    return set(re.findall(r'\b\d+\b', s.lower()))

def extract_first_number(s):
    m = re.search(r'\b\d+\b', s)
    return m.group(0) if m else None

for a1, a2 in fps:
    n1 = extract_all_numbers(a1)
    n2 = extract_all_numbers(a2)
    f1 = extract_first_number(a1)
    f2 = extract_first_number(a2)
    
    conflict = False
    if f1 and f2:
        if f1 not in n2 and f2 not in n1:
            conflict = True
            
    print(f"A1: {a1}")
    print(f"A2: {a2}")
    print(f"Conflict: {conflict}")
    print("-" * 40)
