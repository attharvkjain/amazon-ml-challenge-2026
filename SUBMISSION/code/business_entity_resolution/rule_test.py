import re

# Let's test on the FP examples:
fps = [
    ("3213 Ridgely Drive, Vestavia Hills, AL", "215 RIDGELY DR, VESTAVIA HILLS, AL"),
    ("6911 Chestnut Road, Independence, OH", "915 Chestnut Rd, INDEPENDENCE, OH"),
    ("1815 Mill Lane, Southold, NY", "1826 MILL LANE, SOUTHOLD, NY"),
    ("2844 Fraternity Church Road", "2853 FRATERNITY CHURCH RD"),
    ("35115 Bennington Lane", "35136 BENNINGTON LN"),
    ("2406 Tuckey Lane", "419 Tuckey Ln"),
    ("C-636, Delhi, South Delhi, Block C Sangam Vihar", "C-639, Block C Sangam Vihar, Delhi, South Delhi, DL"),
    ("Thane, Airoli Naka Airoli, Navi Mumbai, Thane, Maharashtra, H. No. 842", "El G-122, Thane, Navi Mumbai, MH"),
]

def extract_all_numbers(s):
    return set(re.findall(r'\b\d+\b', s.lower()))

for a1, a2 in fps:
    n1 = extract_all_numbers(a1)
    n2 = extract_all_numbers(a2)
    print(f"A1: {a1}")
    print(f"A2: {a2}")
    print(f"N1: {n1}, N2: {n2}")
    print(f"Shared: {n1 & n2}")
    
    # Logic: if both have numbers, and none overlap, it's a hard mismatch!
    conflict = len(n1) > 0 and len(n2) > 0 and len(n1 & n2) == 0
    print(f"Conflict: {conflict}")
    print("-" * 40)
