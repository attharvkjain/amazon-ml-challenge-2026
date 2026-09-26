import re

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

def extract_first_number(s):
    m = re.search(r'\b\d+\b', s)
    return m.group(0) if m else None

for a1, a2 in fps:
    n1 = extract_first_number(a1)
    n2 = extract_first_number(a2)
    conflict = (n1 is not None) and (n2 is not None) and (n1 != n2)
    print(f"{n1} vs {n2} -> Conflict: {conflict}")
