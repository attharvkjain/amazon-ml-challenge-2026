# Business Entity Matching

**User:** Anonymous  
**Created:** 9/25/2026 11:54:51  
**Updated:** 9/25/2026 11:54:52  
**Exported:** 9/25/2026 12:27:44  
**Link:** [https://chatgpt.com/share/6ab613b3-0b58-83ee-a4e5-959f7daf0d2a](https://chatgpt.com/share/6ab613b3-0b58-83ee-a4e5-959f7daf0d2a)  

## Prompt:
25/09/2026, 03:27:18

I have a data source coming from 3 different aggregators that data contains a unique_key, Business_name, Business_address, country we have to bucket the same businesses which might be stored differently with suttle change in name. we have to match same context business in a bucket how should we appraoch it

## Response:
25/09/2026, 03:27:18

The right framing is **entity resolution / record linkage**: first normalize the three feeds, then generate plausible matches, score them using name + address + country, and finally cluster records into one canonical business entity.

Yes. This is a classic **Entity Resolution / Record Linkage** problem. Your goal is not simply to find duplicate strings. You want to determine whether two records represent the **same real-world business**, even when each aggregator stores that business slightly differently.

For example:

| Aggregator | unique_key | Business_name | Business_address | country |
|---|---|---|---|---|
| A | A1023 | Starbucks Coffee | Shop 12, Linking Road, Bandra West, Mumbai | India |
| B | B7781 | Starbucks Coffee Mumbai | 12 Linking Rd., Bandra W., Mumbai | India |
| C | C9912 | STARBUCKS COFFEE | Shop No 12 Linking Road Bandra West | IN |

These should end up in one bucket, such as:

```text
ENTITY_000184
 ├── A1023
 ├── B7781
 └── C9912
```

## Recommended architecture

I would build the pipeline in **6 stages**:

```text
3 Aggregator Data
       │
       ▼
1. Standardization / Normalization
       │
       ▼
2. Blocking / Candidate Generation
       │
       ▼
3. Pairwise Similarity Calculation
       │
       ▼
4. Match Scoring / Classification
       │
       ▼
5. Clustering / Entity Assignment
       │
       ▼
Canonical Business ID
```

The most important thing is **not to compare every record with every other record**.

If you have 1 million records, comparing every pair would be enormous. Instead, first identify records that could plausibly represent the same business.

---

# 1. Normalize the data first

This is probably the most important stage.

Two strings can look different while representing exactly the same value.

### Business name normalization

Convert:

```text
"McDonald's Restaurant"
"McDonald's - Bandra"
"MCDONALDS RESTAURANT"
"McDonalds"
```

into something closer to:

```text
mcdonalds
```

Typical operations:

```text
lowercase
remove punctuation
remove extra spaces
normalize accents
standardize abbreviations
normalize apostrophes
remove irrelevant business suffixes
```

For example:

```text
"Starbucks® Coffee Pvt. Ltd."
```

could become:

```text
starbucks coffee
```

Be careful with removing words. Words such as:

```text
mall
airport
hospital
restaurant
clinic
hotel
```

may actually distinguish different businesses.

So I would **not aggressively remove all contextual words**.

---

# 2. Normalize the address

Addresses are often more difficult than names.

For example:

```text
Shop 12, Linking Road, Bandra West, Mumbai
```

and

```text
12 Linking Rd., Bandra W., Mumbai
```

should ideally become something like:

```text
12 linking road bandra west mumbai
```

Normalize things like:

```text
road → rd
street → st
building → bldg
number → no
apartment → apt
```

Also:

```text
remove punctuation
lowercase
normalize whitespace
standardize unit numbers
standardize postal codes
```

### Ideally split the address

Rather than treating the entire address as one string:

```text
Business_address
```

extract components such as:

```text
house_number
building
street
locality
city
state
postal_code
```

Then you can compare the components independently.

For example:

```text
Aggregator A

street = linking road
locality = bandra west
postal_code = 400050
```

versus:

```text
Aggregator B

street = linking rd
locality = bandra w
postal_code = 400050
```

This gives you a much better comparison than raw string matching.

---

# 3. Country should be a blocking condition

Country is extremely useful.

You probably don't want:

```text
Starbucks, India
```

being compared with:

```text
Starbucks, USA
```

So initially:

```text
candidate pairs = records with same country
```

But I would **normalize country codes** first.

For example:

```text
India
IND
IN
```

→

```text
IN
```

---

# 4. Use blocking to generate candidates

After country filtering, create smaller candidate groups.

For example:

```text
same country
+
same postal code
```

or:

```text
same country
+
similar business-name prefix
```

or:

```text
same country
+
address token overlap
```

You can have several blocking strategies.

### Example

For:

```text
Starbucks Coffee
```

possible candidates could be records with:

```text
country = IN
AND
postal_code = 400050
```

or perhaps:

```text
country = IN
AND
first normalized name token = starbucks
```

This gives you a manageable set of potential matches.

---

# 5. Calculate multiple similarity measures

Do **not** depend on a single fuzzy matching algorithm.

You want to calculate several features.

For example:

### Name similarity

Use algorithms such as:

- Jaro-Winkler
- Levenshtein
- token sort ratio
- token set ratio
- character n-gram cosine similarity

Example:

```text
"Starbucks Coffee"
"Starbucks Coffee Mumbai"
```

would have high similarity.

But:

```text
"Starbucks Coffee"
"Star India"
```

would be low.

---

### Address similarity

Likewise calculate:

```text
address_similarity
```

For example:

```text
"12 Linking Road Bandra West"
"12 Linking Rd Bandra W"
```

should be very high.

You can also calculate individual similarities:

```text
street_similarity
locality_similarity
city_similarity
postal_code_match
house_number_match
```

---

### Country similarity

Usually this is binary:

```text
country_match = 1
country_mismatch = 0
```

Country mismatch should probably be a very strong negative signal.

---

# 6. Create a composite match score

For a first version, you could use something like:

```text
match_score =
      0.50 × name_similarity
    + 0.35 × address_similarity
    + 0.15 × country_match
```

But I would eventually make the weighting more sophisticated.

For example:

```text
if postal_code matches:
    increase score

if house number matches:
    increase score

if normalized address exactly matches:
    increase score substantially
```

Example:

```text
Name similarity       = 0.94
Address similarity    = 0.91
Country match         = 1
Postal code match     = 1

Score = 0.50(0.94)
      + 0.35(0.91)
      + 0.15(1)

      = 0.9375
```

Then define thresholds.

```text
score >= 0.90       → MATCH
0.75 - 0.90         → REVIEW
score < 0.75        → NOT MATCH
```

The actual thresholds should be determined from your data, rather than assuming these values are optimal.

---

# 7. Be very careful with business branches

This is one of the biggest problems you'll encounter.

Suppose you have:

```text
McDonald's
Andheri West, Mumbai
```

and:

```text
McDonald's
Bandra West, Mumbai
```

Their names are essentially identical.

A naive fuzzy matcher might say:

```text
MATCH
```

but they are **different business entities / locations**.

Therefore your model needs to understand:

```text
same brand
```

is not necessarily:

```text
same business location
```

Address becomes extremely important here.

For example:

```text
Name similarity = 0.99
Address similarity = 0.20
```

should almost certainly **not** be merged.

Whereas:

```text
Name similarity = 0.82
Address similarity = 0.98
```

may very well be the same business.

This is why I would avoid:

```text
name-only matching
```

---

# 8. Don't immediately cluster from fuzzy name similarity

There is another subtle problem.

Imagine:

```text
A = Starbucks Coffee
B = Starbucks Coffee Mumbai
C = Starbucks Mumbai Airport
```

You could get:

```text
A ≈ B
B ≈ C
```

but:

```text
A ≠ C
```

This creates a dangerous "chain merge."

So rather than blindly doing:

```text
A → B → C
```

you should have **cluster validation rules**.

For example:

```text
Same entity requires:

country compatible
AND
address sufficiently compatible
AND
name sufficiently compatible
```

Then create the entity cluster only when those conditions hold.

---

# 9. Use a graph for the final bucketing

A very natural representation is a graph.

Each record is a node:

```text
A1023
B7781
C9912
```

Create an edge when two records are judged to represent the same business:

```text
A1023 ───── B7781
   \          /
    \        /
      C9912
```

Then derive entity groups from high-confidence matches.

The result could be:

```text
ENTITY_001

A1023
B7781
C9912
```

while another branch:

```text
ENTITY_002

A2044
B1201
C8122
```

gets its own bucket.

A Union-Find / Disjoint Set structure is useful for this stage.

---

# 10. Store a canonical entity separately

I would **not overwrite the aggregator records**.

Keep two logical tables.

### Raw / source records

```text
source_record
---------------------------
source
unique_key
business_name
business_address
country
normalized_name
normalized_address
```

### Canonical entity

```text
business_entity
----------------------------
entity_id
canonical_business_name
canonical_address
country
```

And a mapping table:

```text
business_entity_mapping
--------------------------------
entity_id
source
unique_key
match_score
match_method
confidence
```

For example:

```text
entity_id    source    unique_key    score    method
-------------------------------------------------------
E000184      A         A1023         0.97     fuzzy
E000184      B         B7781         0.94     fuzzy
E000184      C         C9912         1.00     exact-normalized
```

This is much easier to audit.

---

# 11. I would use a two-stage matching system

For your problem, I would recommend:

### Stage 1: Rule-based high-confidence matches

Catch obvious cases:

```text
normalized_name exact
AND
normalized_address exact
AND
country exact
```

or:

```text
postal_code exact
AND
house_number exact
AND
name highly similar
```

These become:

```text
HIGH CONFIDENCE
```

---

### Stage 2: Fuzzy / ML matching

For the remaining cases, create features:

```text
name_jaro_winkler
name_token_similarity
name_ngram_similarity

address_similarity
street_similarity
locality_similarity
postal_code_match
house_number_match

country_match
```

Then train a model such as:

```text
Logistic Regression
Random Forest
XGBoost
LightGBM
```

with:

```text
1 = same business
0 = different business
```

This is often better than manually deciding weights.

---

# 12. The most important part: create labeled pairs

If you can manually label even a few thousand pairs, your system will improve dramatically.

Create something like:

| Record A | Record B | Same business? |
|---|---|---|
| Starbucks Coffee | Starbucks Coffee Mumbai | 1 |
| McDonalds Andheri | McDonald's Andheri W | 1 |
| McDonald's Bandra | McDonald's Andheri | 0 |
| ABC Pharmacy | ABC Pharmacy Ltd | 1 |
| ABC Pharmacy Mumbai | ABC Pharmacy Pune | 0 |

Then use those labels to learn the threshold or train the classifier.

---

# 13. A practical Python stack

A first implementation could use:

```text
pandas
rapidfuzz
scikit-learn
numpy
recordlinkage
```

Potentially later:

```text
Splink
```

for a more sophisticated entity-resolution pipeline.

You don't necessarily need embeddings or an LLM initially.

In fact, I would **start with deterministic normalization + fuzzy matching + ML classification** before introducing embeddings.

---

# 14. Example matching logic

Conceptually:

```python
def compare(a, b):

    if a["country"] != b["country"]:
        return 0.0

    name_score = name_similarity(
        a["normalized_name"],
        b["normalized_name"]
    )

    address_score = address_similarity(
        a["normalized_address"],
        b["normalized_address"]
    )

    postal_match = (
        a["postal_code"] == b["postal_code"]
    )

    house_match = (
        a["house_number"] == b["house_number"]
    )

    score = (
        0.45 * name_score +
        0.35 * address_score +
        0.10 * postal_match +
        0.10 * house_match
    )

    return score
```

Then:

```python
if score >= HIGH_THRESHOLD:
    match

elif score >= REVIEW_THRESHOLD:
    manual_review

else:
    no_match
```

The actual scoring should be calibrated on labeled examples.

---

# 15. What I would build for your specific dataset

Since you have exactly:

```text
unique_key
Business_name
Business_address
country
```

I'd structure it like this:

```text
                ┌─────────────────┐
Aggregator A ──►                 │
                │                 │
Aggregator B ──►   Normalization  ├──► Candidate Generation
                │                 │
Aggregator C ──►                 │
                └─────────────────┘
                          │
                          ▼
                ┌──────────────────┐
                │ Pair Comparison  │
                │                  │
                │ Name             │
                │ Address          │
                │ Country          │
                │ Postal           │
                │ House Number     │
                └────────┬─────────┘
                         ▼
                ┌──────────────────┐
                │ Match Classifier │
                └────────┬─────────┘
                         ▼
                ┌──────────────────┐
                │ Entity Clustering│
                └────────┬─────────┘
                         ▼
                ┌──────────────────┐
                │ Canonical Entity │
                │    ENTITY_ID     │
                └──────────────────┘
```

### The final output could look like

| entity_id | source | unique_key | original_name | original_address | confidence |
|---|---|---|---|---|---:|
| E001 | A | A1023 | Starbucks Coffee | Shop 12, Linking Road... | 0.99 |
| E001 | B | B7781 | Starbucks Coffee Mumbai | 12 Linking Rd... | 0.96 |
| E001 | C | C9912 | STARBUCKS COFFEE | Shop No 12 Linking Road... | 0.98 |
| E002 | A | A2044 | McDonalds | Andheri West... | 0.98 |
| E002 | B | B5543 | McDonald's Restaurant | Andheri W... | 0.95 |
| E003 | A | A3091 | McDonalds | Bandra West... | 0.97 |

---

# One improvement I strongly recommend

If you can obtain **any additional attributes**, entity resolution becomes significantly better.

Especially:

```text
phone_number
website
email
latitude
longitude
postal_code
city
state
category
```

For businesses, **latitude/longitude + name** is particularly powerful.

For example:

```text
Name similarity = 0.85
Distance = 12 meters
Country = same
```

is much stronger evidence than name similarity alone.

---

## My recommended implementation strategy

For your project, I would build it in this order:

```text
Phase 1
Normalization
        ↓
Phase 2
Exact + rule-based matching
        ↓
Phase 3
Fuzzy candidate matching
        ↓
Phase 4
Generate labeled match/non-match pairs
        ↓
Phase 5
Train XGBoost/LightGBM classifier
        ↓
Phase 6
High-confidence clustering
        ↓
Phase 7
Canonical ENTITY_ID generation
        ↓
Phase 8
Manual review for borderline cases
```

The key idea is:

> **Don't try to answer "are these names similar?"**
>
> Answer **"what is the probability that these two records refer to the same real-world business?"**

That distinction will make the system much more reliable, especially when you have chains, multiple branches, abbreviations, spelling variations, and different address formats.

For your dataset size, I would next design the **exact normalization rules + blocking strategy + similarity features + scoring formula** around your actual three aggregator files, because those choices will determine whether this scales cleanly or produces false merges.

## Prompt:
25/09/2026, 03:31:47

should we appraoch it by embeddings or is there open source model that we can use to perfrom it

## Response:
25/09/2026, 03:31:49

Yes, embeddings can help, but I would **not use embeddings alone** for this problem. The strongest practical design is usually a hybrid: deterministic normalization + candidate blocking + embeddings/fuzzy features + a match classifier.

> **Searched 3 websites**
>
> 
>
> Worked for 7s

Yes. **Embeddings are a good component for this problem**, especially when aggregator data contains subtle name variations, transliteration, abbreviations, or multilingual text. But I would not make the system "embedding similarity = same business."

For your use case, I would build a **hybrid entity-resolution system**.

### The models/tools I would consider

| Option | What it does | Good for your case |
|---|---|---|
| **Splink** | Full probabilistic record-linkage framework | ⭐⭐⭐⭐⭐ |
| **BGE-M3** | Multilingual embeddings | ⭐⭐⭐⭐ |
| **multilingual-e5-large** | Multilingual semantic embeddings | ⭐⭐⭐⭐ |
| **Ditto** | Transformer-based pairwise entity matcher | ⭐⭐⭐⭐⭐ once you have labels |
| RapidFuzz | String similarity | ⭐⭐⭐⭐⭐ as a supporting feature |

Splink is particularly interesting because it is specifically designed for record linkage, including blocking, fuzzy comparisons, probabilistic scoring, thresholding, and evaluation. It is designed to scale to very large datasets. ([Moj Analytical Services](https://moj-analytical-services.github.io/splink/topic_guides/topic_guides_index.html?utm_source=chatgpt.com))

Ditto takes a different approach: it treats entity matching as a **pair classification problem** and fine-tunes a pretrained language model to decide whether two records refer to the same entity. It explicitly supports business/entity matching and uses blocking before pairwise matching. ([GitHub](https://github.com/megagonlabs/ditto/blob/master/README.md?utm_source=chatgpt.com))

For embeddings, BGE-M3 is multilingual, supports 100+ languages, and provides dense and sparse representations. ([Hugging Face](https://huggingface.co/BAAI/bge-m3/blob/refs%2Fpr%2F1/README.md?utm_source=chatgpt.com)) Multilingual-E5-large supports 94 languages and can be used directly with Sentence Transformers. ([Hugging Face](https://huggingface.co/intfloat/multilingual-e5-large/tree/main?utm_source=chatgpt.com))

## How I would actually use embeddings

Suppose:

```text
Record A

Business_name:
Starbucks Coffee

Business_address:
Shop 12, Linking Road, Bandra West, Mumbai

country:
India
```

and:

```text
Record B

Business_name:
Starbucks Coffee Mumbai

Business_address:
12 Linking Rd., Bandra W., Mumbai

country:
IN
```

Don't concatenate everything and simply ask:

```text
cosine_similarity(A, B) > 0.85
```

Instead, create **separate representations**.

```text
             Record
                |
       ┌────────┼─────────┐
       ↓        ↓         ↓
     Name    Address    Country
       |        |         |
   embedding embedding  exact
       |        |
       └────┬───┘
            ↓
       similarity
```

For example:

```text
name_embedding_similarity       = 0.96
address_embedding_similarity    = 0.93

name_fuzzy_similarity            = 0.94
address_fuzzy_similarity         = 0.89

postal_code_match                = 1
country_match                    = 1
house_number_match               = 1
```

These become features for your final matcher.

---

# Why embeddings alone are dangerous

Consider:

```text
McDonald's Andheri West
McDonald's Bandra West
```

An embedding model may consider these highly similar because semantically they are almost identical.

But they are **different physical businesses**.

Likewise:

```text
Apollo Pharmacy
Apollo Pharmacy
```

could represent dozens of locations.

Embeddings are excellent at understanding:

> "These two descriptions probably refer to the same thing."

They are less reliable at enforcing:

> "These two records are the same exact physical business location."

That second problem needs structured evidence.

---

# The architecture I recommend

I would make your pipeline:

```text
                 3 Aggregators
                      │
                      ▼
              Data normalization
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
      Exact rules            Blocking
                                  │
                                  ▼
                         Candidate pairs
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
              Fuzzy features              Embeddings
                    │                           │
                    ├─────────────┬─────────────┤
                                  ▼
                           Match classifier
                                  │
                   ┌──────────────┼─────────────┐
                   ▼              ▼             ▼
                 MATCH         REVIEW        NO MATCH
                   │
                   ▼
             Entity clustering
                   │
                   ▼
             Canonical ENTITY_ID
```

This is much safer than:

```text
embedding → cosine similarity → bucket
```

---

# Which embedding model?

For your specific scenario, I would start with **BGE-M3** if your aggregators can contain businesses/addresses from multiple countries and languages. BGE-M3 is explicitly multilingual and supports more than 100 languages. ([Hugging Face](https://huggingface.co/BAAI/bge-m3/blob/refs%2Fpr%2F1/README.md?utm_source=chatgpt.com))

A second model worth benchmarking is:

```text
intfloat/multilingual-e5-large
```

It supports 94 languages and is available through Sentence Transformers. ([Hugging Face](https://huggingface.co/intfloat/multilingual-e5-large/tree/main?utm_source=chatgpt.com))

I would actually benchmark both on your own business pairs rather than assuming one will win.

---

# But there is something even better than generic embeddings

Once you have some labeled examples, train a **specialized entity-matching model**.

This is where Ditto becomes interesting.

You can provide:

```text
Record A:
name = Starbucks Coffee
address = Shop 12 Linking Road Bandra West
country = India

Record B:
name = Starbucks Coffee Mumbai
address = 12 Linking Rd Bandra W
country = IN

label = 1
```

and:

```text
Record A:
name = McDonald's Andheri
address = Andheri West Mumbai

Record B:
name = McDonald's Bandra
address = Bandra West Mumbai

label = 0
```

Ditto is designed specifically for this pairwise entity-matching setup and fine-tunes a pretrained language model for it. ([GitHub](https://github.com/megagonlabs/ditto/blob/master/README.md?utm_source=chatgpt.com))

This means your progression can be:

```text
Phase 1
Rules + RapidFuzz

        ↓

Phase 2
Rules + RapidFuzz + embeddings

        ↓

Phase 3
Create labeled pairs

        ↓

Phase 4
Train entity-matching model

        ↓

Phase 5
Use model + rules together
```

---

# An interesting option: Splink

You may not even need to build the entire matching framework yourself.

Splink already provides:

```text
blocking
fuzzy comparison
probabilistic linkage
match weights
thresholding
evaluation
```

and is intended specifically for record linkage/deduplication. ([Moj Analytical Services](https://moj-analytical-services.github.io/splink/topic_guides/topic_guides_index.html?utm_source=chatgpt.com))

For example, Splink can learn that:

```text
country exact match
```

is useful, while:

```text
name slightly different
```

may still be compatible with a match. Its probabilistic framework estimates the relative importance of different comparison signals. ([Moj Analytical Services](https://moj-analytical-services.github.io/splink/demos/tutorials/04_Estimating_model_parameters.html?utm_source=chatgpt.com))

So instead of manually inventing:

```text
name = 0.5
address = 0.35
country = 0.15
```

you can let a linkage model learn evidence weights from your data.

---

# What I would choose for your project

Given your columns:

```text
unique_key
Business_name
Business_address
country
```

I'd start with:

```text
Normalization
       +
Blocking
       +
RapidFuzz
       +
BGE-M3 embeddings
       +
XGBoost/LightGBM
       +
Union-Find clustering
```

Then, once you have enough labeled pairs:

```text
Normalization
       +
Blocking
       +
Ditto / fine-tuned transformer
       +
Rule validation
       +
Clustering
```

### One particularly strong design

Use embeddings primarily for **candidate retrieval**, not final decision-making.

For example:

```text
10 million records
       │
       ▼
country + city/postcode blocking
       │
       ▼
50,000 plausible candidates
       │
       ▼
BGE-M3 nearest-neighbor search
       │
       ▼
Top 20 candidates per record
       │
       ▼
Detailed matcher
       │
       ├── name similarity
       ├── address similarity
       ├── postal match
       ├── house-number match
       ├── country match
       └── embedding similarity
               │
               ▼
           MATCH / NO MATCH
```

That gives you both **scalability and accuracy**. Blocking is especially important because pairwise comparison count is a major driver of record-linkage runtime. ([Moj Analytical Services](https://moj-analytical-services.github.io/splink/topic_guides/performance/drivers_of_performance.html?utm_source=chatgpt.com))

### And there is a very important distinction

Think of the system as solving **three different problems**:

```text
1. Candidate Retrieval
   "Which records could be the same?"

2. Entity Matching
   "Are these two records actually the same?"

3. Entity Clustering
   "Which records belong to the same business bucket?"
```

Embeddings are excellent for **#1**, useful for **#2**, and should not be trusted alone for **#3**.

For your use case, I'd build **#1 with BGE-M3, #2 with a hybrid matcher, and #3 with constrained clustering**.

If you share roughly how many records you have per aggregator, such as **100K / 1M / 10M+**, I can lay out the exact architecture, model choice, FAISS/vector-index strategy, blocking keys, and training pipeline for that scale.

---

**Sources:**

- [Introduction - Splink](https://moj-analytical-services.github.io/splink/topic_guides/topic_guides_index.html?utm_source=chatgpt.com)
- [ditto/README.md at master · megagonlabs/ditto · GitHub](https://github.com/megagonlabs/ditto/blob/master/README.md?utm_source=chatgpt.com)
- [README.md · BAAI/bge-m3 at refs/pr/1](https://huggingface.co/BAAI/bge-m3/blob/refs%2Fpr%2F1/README.md?utm_source=chatgpt.com)

## Prompt:
25/09/2026, 03:50:13

![41ca469d-b33a-40b6-a0d7-cf0c437f8ab8.png](https://sdmntprcentralindia.oaiusercontent.com/files/00000000-ae6c-8208-9f15-a1fa5ee4999e/raw?se=2026-09-25T07%3A02%3A44Z&sp=r&sv=2026-02-06&sr=b&scid=3c871cf8-fb9a-4f6e-a6a7-45e57d3bb4c4&skoid=ca37c3ec-ab43-496e-be5f-4684c5519a26&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2026-09-25T02%3A58%3A08Z&ske=2026-09-26T02%3A58%3A08Z&sks=b&skv=2026-02-06&sig=Ea/54CAqeuQ5OR%2Btni7HyLQXnU2uv8M72Ak5n8kOyJ0%3D)

I do have ground truth in above format so should we go forward with Ditto? (just to clear the confusion source1 will be our reference and we'll one map for source1)

## Response:
25/09/2026, 03:50:14

Yes. **Now that you have ground truth, Ditto becomes a very reasonable choice**, and your clarification about Source 1 changes the design in an important way.

Your problem is essentially:

```text
Source 1 = reference/master side

S1-730934468
    ├── S2-356983532
    └── S3-352439310

S1-7293388
    ├── S2-7028416
    ├── S2-442723188
    ├── S2-157073701
    └── S3-23120965
```

So the task is **not general deduplication across all records**.

It is:

> For every Source 1 business, identify all records from Source 2 and Source 3 that refer to that same real-world business.

That is a much cleaner **reference-to-source entity matching** problem.

## I would use Ditto, but in a hybrid pipeline

I would structure it as:

```text
                    SOURCE 1
                 Reference Data
                      │
                      │
                      ▼
              Candidate Generation
                      │
          ┌───────────┴───────────┐
          │                       │
       Source 2                Source 3
          │                       │
          └───────────┬───────────┘
                      ▼
               Candidate Pairs
                      │
                      ▼
              ┌───────────────┐
              │    Ditto      │
              │ Pair Matcher  │
              └───────┬───────┘
                      ▼
             Match probability
                      │
             ┌────────┴────────┐
             ▼                 ▼
          MATCH            NO MATCH
             │
             ▼
      Source1 → matched IDs
```

The important point is:

**Do not run Ditto against every S1 × S2/S3 combination.**

First generate candidates, then let Ditto make the final decision.

---

# Your ground truth is excellent for training

Your current ground truth:

```text
source1_entity_id | matched_entity_ids
```

can be transformed into pair-level training data.

For example:

```text
S1-7293388 → S2-7028416
```

becomes:

```text
record_A = S1-7293388
record_B = S2-7028416
label = 1
```

and:

```text
S1-7293388 → S2-123456789
```

where `S2-123456789` is not in the ground-truth list becomes:

```text
record_A = S1-7293388
record_B = S2-123456789
label = 0
```

Same for Source 3.

So your training dataset becomes:

| S1 | Other source | Match |
|---|---|---:|
| S1-7293388 | S2-7028416 | 1 |
| S1-7293388 | S2-442723188 | 1 |
| S1-7293388 | S3-23120965 | 1 |
| S1-7293388 | S2-987654321 | 0 |
| S1-7293388 | S3-555555555 | 0 |

This is exactly the kind of pair classification setup Ditto is designed around.

---

# One thing is especially important in your case

Your positives are **one-to-many from Source 1**.

So don't structure the model as:

```text
S1 → exactly one S2/S3
```

Instead:

```text
S1
 ├── candidate S2 #1 → MATCH
 ├── candidate S2 #2 → MATCH
 ├── candidate S2 #3 → NO MATCH
 ├── candidate S3 #1 → MATCH
 ├── candidate S3 #2 → NO MATCH
 └── candidate S3 #3 → MATCH
```

Then at inference:

```python
matched_entity_ids = [
    candidate_id
    for candidate_id, probability in predictions
    if probability >= threshold
]
```

So you retain **all matching S2/S3 records** for each S1.

---

# The biggest challenge will be negative sampling

Your positive ground truth tells us:

```text
S1-7293388 ↔ S2-7028416    1
```

But you need good examples of:

```text
S1-7293388 ↔ S2-XXXXXXXX    0
```

This is where I would be careful.

Don't generate only random negatives.

Suppose:

```text
S1:
Starbucks Coffee
Bandra West Mumbai
```

and the negative is:

```text
ABC Furniture
Pune
```

That's trivial.

Ditto learns very little from it.

Instead create **hard negatives**:

```text
Starbucks Coffee
Andheri West Mumbai

Starbucks Coffee
Bandra East Mumbai

Starbucks Cafe
Bandra West Mumbai

Starbucks Coffee
Bandra West Pune
```

These are much more useful because they force the model to understand the subtle distinction between:

```text
same business
```

and

```text
same/similar business name but different location
```

---

# Your existing ground truth gives us another huge advantage

We can evaluate the model properly.

For each Source 1:

```text
Ground truth:

S1-7293388
    S2-7028416
    S2-442723188
    S3-23120965
```

Model prediction:

```text
S1-7293388
    S2-7028416
    S2-442723188
    S3-23120965
    S3-99999999
```

Then:

```text
TP = 3
FP = 1
FN = 0
```

So we can calculate:

```text
Precision
Recall
F1
```

But I would also calculate **Recall@K / Precision@K** during candidate retrieval, because your pipeline has two stages.

---

# I would actually use embeddings before Ditto

This is where the previous discussion becomes useful.

I'd make the architecture:

```text
                 Source 1
                    │
                    ▼
             Normalize fields
                    │
                    ▼
           Embedding generation
                    │
                    ▼
              Vector search
                    │
             Top K candidates
                    │
                    ▼
               Ditto model
                    │
          ┌─────────┴──────────┐
          ▼                    ▼
       MATCH               NO MATCH
          │
          ▼
       Mapping
```

For example:

```text
S1 business
      │
      ▼
BGE-M3 embedding
      │
      ▼
FAISS / vector DB
      │
      ▼
top 50 S2 candidates
+
top 50 S3 candidates
      │
      ▼
Ditto
      │
      ▼
final matches
```

This gives you the strengths of both approaches:

**Embeddings**

Good for:

```text
candidate retrieval
language variation
spelling differences
abbreviations
multilingual names
semantic similarity
```

**Ditto**

Good for:

```text
pair-level decision
name + address interaction
subtle differences
learning from your actual ground truth
```

---

# How I would represent the Ditto input

Don't give Ditto only:

```text
Starbucks Coffee
```

Give it structured fields.

For example:

```text
COL name VAL Starbucks Coffee
COL address VAL Shop 12 Linking Road Bandra West Mumbai
COL country VAL India
```

and:

```text
COL name VAL Starbucks Coffee Mumbai
COL address VAL 12 Linking Rd Bandra W Mumbai
COL country VAL IN
```

Then the model learns from the combination.

You can potentially include normalized fields as well:

```text
COL name VAL ...
COL normalized_name VAL ...
COL address VAL ...
COL normalized_address VAL ...
COL country VAL ...
```

I would test whether the raw + normalized combination improves validation performance.

---

# Very important: split your dataset correctly

Because one S1 may have multiple S2/S3 positive records, **do not randomly split individual pairs**.

Bad:

```text
Train:
S1-100 → S2-1

Validation:
S1-100 → S2-2
```

This leaks information about S1 into validation.

Instead:

```text
Train Source1 entities
----------------------
S1-1
S1-2
S1-3
...
S1-80000

Validation Source1 entities
---------------------------
S1-80001
S1-80002
...
```

In other words:

> **Split by `source1_entity_id`, not by pair.**

This is extremely important for getting a realistic measurement.

---

# The final mapping you want

Your production output remains exactly in your current format:

```text
source1_entity_id    matched_entity_ids
-----------------------------------------------------------
S1-730934468         S2-356983532,S3-352439310
S1-7293388            S2-7028416,S2-442723188,S2-157073701,S3-23120965
...
```

So you're essentially building a learned function:

```text
f(Source1, Candidate) → P(same business)
```

and then:

```text
For each S1:
    retrieve candidates
    score every candidate
    keep candidates above threshold
    aggregate IDs
```

---

# One more architectural decision

I would **not necessarily train one model for both S2 and S3 initially**.

I'd first experiment with:

```text
Model A:
Source1 ↔ Source2

Model B:
Source1 ↔ Source3
```

Why?

The aggregators may have different data quality.

For example:

```text
Source 2:
Business name = very good
Address = noisy

Source 3:
Business name = noisy
Address = very structured
```

A single model may work, but separate models let the system learn source-specific matching patterns.

Later you can compare that against a single:

```text
Source1 ↔ {Source2, Source3}
```

model with a source identifier feature.

---

# My recommendation for your project

Given that you already have this ground truth, I'd go with:

```text
                 Ground Truth
                      │
                      ▼
              Generate pair labels
                      │
            ┌─────────┴──────────┐
            ▼                    ▼
        Positive             Hard Negative
            │                    │
            └─────────┬──────────┘
                      ▼
                Train / Val / Test
                split by S1 entity
                      │
                      ▼
             Candidate retrieval
            Embedding + Blocking
                      │
                      ▼
                  Top-K pairs
                      │
                      ▼
                    Ditto
                      │
                      ▼
              probability score
                      │
                      ▼
               threshold tuning
                      │
                      ▼
            S1 → [S2, S3, ...]
```

### In other words

I **would proceed with Ditto**, but **not Ditto alone**.

The combination I'd recommend is:

**BGE-M3 / multilingual embedding → candidate retrieval → Ditto → threshold → S1 mapping**

And your ground truth is exactly what we need to train, tune, and objectively evaluate it.

The next concrete step should be to take your actual three datasets plus this ground-truth mapping and build the **training-pair generator**. That will let us determine how many positive/negative pairs we have, how severe the class imbalance is, and what hard-negative strategy makes sense before we touch Ditto training.

## Prompt:
25/09/2026, 04:00:02

![167ac0ea-0e0a-4a2a-820a-0a2eddeb4189.png](https://sdmntprcentralindia.oaiusercontent.com/files/00000000-1710-8208-af8e-b78d59d98f74/raw?se=2026-09-25T07%3A02%3A43Z&sp=r&sv=2026-02-06&sr=b&scid=622e4d0a-5604-40ea-937a-9c55b59503c5&skoid=ca37c3ec-ab43-496e-be5f-4684c5519a26&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2026-09-25T01%3A20%3A20Z&ske=2026-09-26T01%3A20%3A20Z&sks=b&skv=2026-02-06&sig=J64CVzGFO6BrI7qWUrad48vjRL6ZGkLkO0GrxVqqjfI%3D)

![d2750ea8-0c22-4e07-9c91-a8cefc47635c.png](https://sdmntprcentralindia.oaiusercontent.com/files/00000000-0e58-8208-a6d1-bdc59bbf42a2/raw?se=2026-09-25T07%3A02%3A44Z&sp=r&sv=2026-02-06&sr=b&scid=588605ba-272f-4370-a203-98e19bd9411a&skoid=ca37c3ec-ab43-496e-be5f-4684c5519a26&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2026-09-25T04%3A02%3A37Z&ske=2026-09-26T04%3A02%3A37Z&sks=b&skv=2026-02-06&sig=vuqNCN1H5YjoWPpEK7x3d0VsL2oemXfq4BsHzseCKow%3D)

how should I proceed it let's start with coding if everything is prepared( if there are any clearifications needed before starting to code ask now)

## Response:
25/09/2026, 04:00:02

Yes, we have enough information to define the architecture. Before we write the first line of code, I only need to lock down a few **data and training assumptions** so we don't build the pipeline around the wrong interpretation.

From your examples, I understand the setup as:

```text
Source 1 = reference/master side
Source 2 = aggregator
Source 3 = aggregator

Goal:
For every S1 entity, find ALL matching S2 and S3 entities.

Output:
S1-ID → [matched S2 IDs + matched S3 IDs]
```

Your ground truth is therefore **one-to-many**, exactly as in:

```text
S1-7293388
    ├── S2-7028416
    ├── S2-442723188
    ├── S2-157073701
    └── S3-23120965
```

### I need these 6 answers before coding

**1. What format are the actual three datasets?**

For example:

```text
source1.csv
source2.csv
source3.csv
ground_truth.csv
```

or Parquet / JSON / Excel?

And what are the exact filenames/paths?

---

**2. What is the approximate size of each dataset?**

For example:

```text
Source 1: 500K rows
Source 2: 2M rows
Source 3: 3M rows
```

This matters because the blocking and embedding strategy will be very different for 100K rows versus 10M rows.

---

**3. Is the ground truth complete?**

This is the most important question.

For a row such as:

```text
S1-730934468 → S2-356983532,S3-352439310
```

does that mean:

> These are **all known correct matches** for S1-730934468?

Or does it mean:

> These are some positive matches, but there might be additional matches that aren't listed?

I strongly prefer the first interpretation if that is how the ground truth was generated.

---

**4. Are unmatched Source 1 businesses present in the ground truth?**

For example:

```text
S1-123456789    NaN
```

or:

```text
S1-123456789    ""
```

Would that mean **no matching S2/S3 business exists**?

This determines how we generate negative examples.

---

**5. Are these the only fields we have?**

Currently I see:

```text
entity_id
business_name
business_address
country
```

Do you have anything else available, even if it isn't currently displayed?

Things like:

```text
city
state
postal_code
latitude
longitude
phone
website
category
```

Especially **latitude/longitude, phone, postal code, city** would materially improve the matching system.

---

**6. What hardware/environment are we training on?**

For example:

```text
Windows/Linux
Python version
NVIDIA GPU?
GPU VRAM?
CPU/RAM?
```

This matters because Ditto is transformer-based. If you have something like a 16/24 GB NVIDIA GPU, we can design the training pipeline accordingly. If you're CPU-only, I'd structure it differently.

---

## One decision I would make now

I recommend **not jumping directly into Ditto training**.

We'll first build and validate:

```text
Step 1  Load + inspect all datasets
Step 2  Normalize names/addresses/country
Step 3  Parse the ground truth
Step 4  Generate positive pairs
Step 5  Generate hard negative pairs
Step 6  Split by S1 entity
Step 7  Build candidate blocking
Step 8  Establish a RapidFuzz baseline
Step 9  Add embeddings
Step 10 Train Ditto
Step 11 Tune threshold
Step 12 Generate final S1 → S2/S3 mapping
Step 13 Evaluate against your ground truth
```

This is important because we'll then know whether Ditto is actually improving over a simpler baseline rather than assuming the transformer is better.

### One thing I'm already noticing from your sample

Your data is clearly **multilingual and internationally distributed**:

```text
आदित्य प्रॉपर्टीज एलएलपी
LLC Moncada Learning Center
International South Consultants Private Ltd
```

and addresses span countries such as US and India. That makes a **multilingual embedding model** worth including in the experiment rather than using an English-only model.

Send me the answers to the 6 points above, and then we can start with **Step 1: loading and profiling Source 1, Source 2, Source 3, and the ground truth**.

## Prompt:
25/09/2026, 04:22:04

Answers to the asked questions:
1) format is .tsv and seprated by sep="\t"
2) source1 2M, source2 5M, source3 5M
3) by the reference of source1 ground_truth is complete source1 and ground_truth has exact same number of entity_id
4) yes
5) yes
6) we have best hardware and we'll be working on windows, python 3.13.14, 24GB VRAM

maybe lets directly move forward with direct model building and we are working in python notebook as this is data scientist assigment

## Response:
25/09/2026, 04:22:06

One adjustment before coding: the original Ditto repository is pinned to a very old stack, including Python 3.7 and PyTorch 1.9, so I would **not install that package into your Python 3.13 environment**. 

Instead, we can build the same core **Ditto-style pair-classification approach directly with current Hugging Face Transformers**, which is cleaner for this assignment and gives us control over the multilingual model, sampling, and evaluation.

> **Planning the notebook**
>
> I’m going to verify Ditto’s current compatibility, then design a Windows-friendly notebook around a modern multilingual transformer. I’ll include data loading, pair formatting, fine-tuning, evaluation, checkpointing, inference, and advice for Python 3.13.
>
> **Planned the notebook**
>
> 
>
> **Searched 4 websites**
>
> 
>
> **Designing efficient data handling**
>
> I’m planning Polars-based processing to keep millions of rows manageable. I’ll preserve relevant attributes, parse multi-ID ground truth, validate one-to-one source records, and generate sampled hard negatives without loading everything into pandas.
>
> **Structuring the baseline**
>
> I’m choosing a modern Ditto-style pair classifier rather than relying on an older package stack. The notebook will use Polars, sampled training pairs, multilingual text encoding, and a manageable first training run for your large datasets.
>
> **Building the baseline**
>
> I’m settling on a practical Ditto-style cross-encoder using multilingual XLM-R, with compatibility checks for current libraries. The first notebook section will cover configuration, loading, normalization, pair generation, tokenization, and training.
>
> **Structured the baseline**
>
> 
>
> **Searched 1 website**
>
> 
>
> Worked for 1m 11s

Yes. With the ground truth you have, we can move directly into supervised model building.

One important implementation choice: I would **not install the original `megagonlabs/ditto` repository** into your Python 3.13 environment. Its documented stack is based on Python 3.7.7, PyTorch 1.9, Transformers 4.9.2, etc. ([GitHub](https://github.com/megagonlabs/ditto/blob/master/README.md?utm_source=chatgpt.com))

Instead, we'll implement the same core idea directly with current Hugging Face Transformers:

```text
Source 1 + Source 2/3
        ↓
structured text pair
        ↓
XLM-RoBERTa cross-encoder
        ↓
MATCH / NO MATCH
```

XLM-R is a good starting model here because it is multilingual and was pretrained across roughly 100 languages. ([Hugging Face](https://huggingface.co/FacebookAI/xlm-roberta-base/blame/main/README.md?utm_source=chatgpt.com))

Our eventual architecture will be:

```text
                  ┌─────────────┐
                  │   Source 1  │
                  │  2M records │
                  └──────┬──────┘
                         │
                  Candidate Retrieval
                         │
             ┌───────────┴───────────┐
             │                       │
          Source 2                Source 3
           5M                       5M
             │                       │
             └───────────┬───────────┘
                         │
                    Candidate pairs
                         │
                         ▼
                 XLM-R Cross Encoder
                         │
                         ▼
                   Match Probability
                         │
                 ┌───────┴────────┐
                 ▼                ▼
               MATCH          NO MATCH
                 │
                 ▼
       S1 → [S2 IDs, S3 IDs]
```

For now, we will build and validate the **matching model**. Full 12M-record candidate retrieval comes immediately after this.

---

# Notebook Cell 1: Install dependencies

Run this once.

```python
%pip install -U pandas polars pyarrow numpy scikit-learn rapidfuzz
%pip install -U torch transformers datasets accelerate sentencepiece
```

Do not reinstall PyTorch with a CPU command if your CUDA-enabled PyTorch is already working.

---

# Notebook Cell 2: Environment check

```python
import sys
import torch
import transformers
import polars as pl
import pandas as pd

print("Python:", sys.version)
print("PyTorch:", torch.__version__)
print("Transformers:", transformers.__version__)
print("Polars:", pl.__version__)

print("\nCUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    print("VRAM:",
          round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2),
          "GB")
```

You want to see:

```text
CUDA available: True
GPU: <your GPU>
VRAM: ~24 GB
```

---

# Notebook Cell 3: Configuration

Change only the paths here.

```python
from pathlib import Path

# ============================================================
# FILE PATHS
# ============================================================

SOURCE1_PATH = Path(r"C:\YOUR_PATH\source1.tsv")
SOURCE2_PATH = Path(r"C:\YOUR_PATH\source2.tsv")
SOURCE3_PATH = Path(r"C:\YOUR_PATH\source3.tsv")
GROUND_TRUTH_PATH = Path(r"C:\YOUR_PATH\ground_truth.tsv")

OUTPUT_DIR = Path("./entity_matching_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# COLUMN NAMES
# ============================================================

ID_COL = "entity_id"

NAME_COL = "business_name"
ADDRESS_COL = "business_address"
COUNTRY_COL = "country"

GT_S1_COL = "source1_entity_id"
GT_MATCH_COL = "matched_entity_ids"

# ============================================================
# OPTIONAL FEATURES
# ============================================================

OPTIONAL_FIELDS = [
    "city",
    "state",
    "postal_code",
    "latitude",
    "longitude",
    "phone",
    "website",
    "category"
]

# ============================================================
# TRAINING CONFIGURATION
# ============================================================

SEED = 42

# First experiment.
# Once validated, increase this substantially.
TRAIN_S1_LIMIT = 300_000

MAX_POSITIVE_PAIRS_PER_SOURCE = 500_000

# 1 random + 1 hard negative per positive
RANDOM_NEGATIVES_PER_POSITIVE = 1
HARD_NEGATIVES_PER_POSITIVE = 1

TEST_SIZE = 0.15
VALID_SIZE = 0.15

MODEL_NAME = "FacebookAI/xlm-roberta-base"

MAX_LENGTH = 256

TRAIN_BATCH_SIZE = 16
EVAL_BATCH_SIZE = 32

GRADIENT_ACCUMULATION_STEPS = 2

LEARNING_RATE = 2e-5
NUM_EPOCHS = 2
WEIGHT_DECAY = 0.01
```

---

# Notebook Cell 4: Discover the actual columns

Since you mentioned additional attributes, let's automatically detect which optional columns exist.

```python
def get_columns(path):
    return pl.read_csv(
        path,
        separator="\t",
        n_rows=0
    ).columns

s1_columns = get_columns(SOURCE1_PATH)
s2_columns = get_columns(SOURCE2_PATH)
s3_columns = get_columns(SOURCE3_PATH)

print("Source 1 columns:")
print(s1_columns)

print("\nSource 2 columns:")
print(s2_columns)

print("\nSource 3 columns:")
print(s3_columns)

available_optional = [
    c for c in OPTIONAL_FIELDS
    if c in s1_columns and c in s2_columns and c in s3_columns
]

print("\nCommon optional fields:")
print(available_optional)
```

We only use fields common to all three sources.

---

# Notebook Cell 5: Load the datasets

We're using Polars because we're dealing with approximately:

```text
2M + 5M + 5M = 12M records
```

and we don't want unnecessary pandas overhead at the raw-data stage.

```python
MATCH_FIELDS = [
    ID_COL,
    NAME_COL,
    ADDRESS_COL,
    COUNTRY_COL,
    *available_optional
]

print("Fields used:")
print(MATCH_FIELDS)

source1 = pl.read_csv(
    SOURCE1_PATH,
    separator="\t",
    columns=MATCH_FIELDS,
    infer_schema_length=100_000,
    null_values=["", "NA", "NaN", "NULL"]
)

source2 = pl.read_csv(
    SOURCE2_PATH,
    separator="\t",
    columns=MATCH_FIELDS,
    infer_schema_length=100_000,
    null_values=["", "NA", "NaN", "NULL"]
)

source3 = pl.read_csv(
    SOURCE3_PATH,
    separator="\t",
    columns=MATCH_FIELDS,
    infer_schema_length=100_000,
    null_values=["", "NA", "NaN", "NULL"]
)

print("Source 1:", source1.shape)
print("Source 2:", source2.shape)
print("Source 3:", source3.shape)
```

---

# Notebook Cell 6: Basic sanity checks

```python
def inspect_source(df, name):
    print(f"\n{'=' * 60}")
    print(name)
    print(f"{'=' * 60}")

    print("Rows:", df.height)
    print("Columns:", df.columns)

    print("\nDuplicate IDs:")
    print(
        df.select(
            pl.col(ID_COL).n_unique().alias("unique_ids"),
            pl.len().alias("rows")
        )
    )

    print("\nNull counts:")
    print(
        df.select([
            pl.col(c).null_count().alias(c)
            for c in MATCH_FIELDS
        ])
    )

    print("\nSample:")
    print(df.head(5))

inspect_source(source1, "SOURCE 1")
inspect_source(source2, "SOURCE 2")
inspect_source(source3, "SOURCE 3")
```

---

# Notebook Cell 7: Normalize strings

We will preserve the original values for XLM-R.

Normalization is only used for:

```text
blocking
hard-negative generation
exact comparisons
additional model features
```

```python
import re

def add_normalized_columns(df):

    df = df.with_columns([
        pl.col(NAME_COL)
        .cast(pl.String)
        .fill_null("")
        .str.to_lowercase()
        .str.replace_all(r"[^\p{L}\p{N}]+", " ")
        .str.replace_all(r"\s+", " ")
        .str.strip_chars()
        .alias("name_normalized"),

        pl.col(ADDRESS_COL)
        .cast(pl.String)
        .fill_null("")
        .str.to_lowercase()
        .str.replace_all(r"[^\p{L}\p{N}]+", " ")
        .str.replace_all(r"\s+", " ")
        .str.strip_chars()
        .alias("address_normalized"),

        pl.col(COUNTRY_COL)
        .cast(pl.String)
        .fill_null("")
        .str.to_uppercase()
        .str.strip_chars()
        .alias("country_normalized")
    ])

    df = df.with_columns([
        pl.col("name_normalized")
        .str.replace_all(" ", "")
        .str.slice(0, 6)
        .alias("name_block"),

        pl.col("country_normalized")
        .str.slice(0, 3)
        .alias("country_block")
    ])

    df = df.with_columns(
        (
            pl.col("country_block")
            + "|"
            + pl.col("name_block")
        ).alias("block_key")
    )

    return df

source1 = add_normalized_columns(source1)
source2 = add_normalized_columns(source2)
source3 = add_normalized_columns(source3)
```

---

# Notebook Cell 8: Inspect normalization

```python
source1.select([
    ID_COL,
    NAME_COL,
    "name_normalized",
    ADDRESS_COL,
    "address_normalized",
    COUNTRY_COL,
    "country_normalized",
    "block_key"
]).head(20)
```

Pay attention to things such as:

```text
Starbucks Coffee
starbucks coffee

STARBUCKS COFFEE
starbucks coffee

McDonald's Restaurant
mcdonalds restaurant
```

We don't want to destroy useful information. The original fields remain intact.

---

# Notebook Cell 9: Load the ground truth

```python
ground_truth = pl.read_csv(
    GROUND_TRUTH_PATH,
    separator="\t",
    columns=[GT_S1_COL, GT_MATCH_COL],
    infer_schema_length=100_000,
    null_values=["", "NA", "NaN", "NULL"]
)

print(ground_truth.shape)
print(ground_truth.head(10))
```

---

# Notebook Cell 10: Verify the most important ground-truth condition

You said ground truth contains exactly the same 2M Source 1 entities.

Let's verify it programmatically.

```python
s1_count = source1.select(pl.col(ID_COL).n_unique()).item()
gt_s1_count = ground_truth.select(pl.col(GT_S1_COL).n_unique()).item()

print("Source 1 unique entities:", s1_count)
print("Ground truth unique Source 1 entities:", gt_s1_count)

assert s1_count == gt_s1_count, (
    f"Mismatch: Source1={s1_count}, GroundTruth={gt_s1_count}"
)

print("✓ Ground truth covers every Source 1 entity.")
```

Also check for duplicates:

```python
duplicate_gt_s1 = (
    ground_truth
    .group_by(GT_S1_COL)
    .agg(pl.len().alias("count"))
    .filter(pl.col("count") > 1)
)

print("Source1 IDs appearing multiple times in GT:",
      duplicate_gt_s1.height)
```

If this prints `0`, excellent.

---

# Notebook Cell 11: Convert ground truth to pair-level data

Your current ground truth is:

```text
S1 → S2,S2,S3
```

The model needs:

```text
S1 ↔ S2 → 1
S1 ↔ S2 → 1
S1 ↔ S3 → 1
```

```python
gt_pairs = (
    ground_truth
    .with_columns(
        pl.col(GT_MATCH_COL)
        .fill_null("")
        .str.split(",")
        .alias("matched_list")
    )
    .explode("matched_list")
    .rename({"matched_list": "matched_entity_id"})
    .with_columns(
        pl.col("matched_entity_id")
        .cast(pl.String)
        .str.strip_chars()
    )
    .filter(
        (pl.col("matched_entity_id") != "") &
        pl.col("matched_entity_id").is_not_null()
    )
    .with_columns(
        pl.when(
            pl.col("matched_entity_id").str.starts_with("S2-")
        )
        .then(pl.lit("S2"))
        .when(
            pl.col("matched_entity_id").str.starts_with("S3-")
        )
        .then(pl.lit("S3"))
        .otherwise(pl.lit("UNKNOWN"))
        .alias("target_source")
    )
    .filter(pl.col("target_source") != "UNKNOWN")
)

print("Total positive pairs:", gt_pairs.height)

print(
    gt_pairs
    .group_by("target_source")
    .agg(pl.len().alias("positive_pairs"))
)
```

---

# Notebook Cell 12: Validate matched IDs against Source 2/3

This is important. We don't want a typo or missing record to silently become training noise.

```python
s2_ids = source2.select(ID_COL).unique()
s3_ids = source3.select(ID_COL).unique()

gt_s2 = (
    gt_pairs
    .filter(pl.col("target_source") == "S2")
    .select(["matched_entity_id"])
    .unique()
)

gt_s3 = (
    gt_pairs
    .filter(pl.col("target_source") == "S3")
    .select(["matched_entity_id"])
    .unique()
)

missing_s2 = (
    gt_s2
    .join(
        s2_ids,
        left_on="matched_entity_id",
        right_on=ID_COL,
        how="anti"
    )
)

missing_s3 = (
    gt_s3
    .join(
        s3_ids,
        left_on="matched_entity_id",
        right_on=ID_COL,
        how="anti"
    )
)

print("Missing S2 ground-truth IDs:", missing_s2.height)
print("Missing S3 ground-truth IDs:", missing_s3.height)
```

Ideally:

```text
Missing S2 ground-truth IDs: 0
Missing S3 ground-truth IDs: 0
```

---

# Notebook Cell 13: Select Source 1 entities for the first training run

We have 2M Source 1 records. For our first model run, don't immediately train on all of them.

Start with:

```text
300K Source 1 entities
```

This is enough to establish whether the approach works.

```python
import numpy as np

rng = np.random.default_rng(SEED)

s1_train = (
    source1
    .sample(
        n=min(TRAIN_S1_LIMIT, source1.height),
        seed=SEED
    )
)

print("Training Source 1 entities:", s1_train.height)
```

---

# Notebook Cell 14: Extract positive pairs for the sampled Source 1

```python
sampled_s1_ids = s1_train.select(
    pl.col(ID_COL).alias(GT_S1_COL)
)

sampled_gt_pairs = (
    gt_pairs
    .join(
        sampled_s1_ids,
        on=GT_S1_COL,
        how="inner"
    )
)

print("Positive pairs before limiting:")
print(
    sampled_gt_pairs
    .group_by("target_source")
    .agg(pl.len().alias("count"))
)
```

Now cap the number so one extremely duplicated business doesn't dominate training.

```python
def cap_positive_pairs(df, max_pairs, seed=42):

    if df.height <= max_pairs:
        return df

    return df.sample(
        n=max_pairs,
        seed=seed
    )

gt_s2_train = cap_positive_pairs(
    sampled_gt_pairs.filter(
        pl.col("target_source") == "S2"
    ),
    MAX_POSITIVE_PAIRS_PER_SOURCE,
    SEED
)

gt_s3_train = cap_positive_pairs(
    sampled_gt_pairs.filter(
        pl.col("target_source") == "S3"
    ),
    MAX_POSITIVE_PAIRS_PER_SOURCE,
    SEED
)

print("S2 positives:", gt_s2_train.height)
print("S3 positives:", gt_s3_train.height)
```

---

# Notebook Cell 15: Build positive pair records

```python
base_s1 = source1.rename({
    c: f"s1_{c}"
    for c in source1.columns
})

base_s2 = source2.rename({
    c: f"s2_{c}"
    for c in source2.columns
})

base_s3 = source3.rename({
    c: f"s3_{c}"
    for c in source3.columns
})
```

Helper:

```python
def build_positive_pairs(gt_subset, target_df, target_prefix):

    pairs = (
        gt_subset
        .join(
            base_s1,
            left_on=GT_S1_COL,
            right_on=f"s1_{ID_COL}",
            how="inner"
        )
        .join(
            target_df,
            left_on="matched_entity_id",
            right_on=f"{target_prefix}_{ID_COL}",
            how="inner"
        )
    )

    return pairs
```

Build them:

```python
positive_s2 = build_positive_pairs(
    gt_s2_train,
    base_s2,
    "s2"
)

positive_s3 = build_positive_pairs(
    gt_s3_train,
    base_s3,
    "s3"
)

print("Positive S2 rows:", positive_s2.height)
print("Positive S3 rows:", positive_s3.height)
```

---

# Notebook Cell 16: Build candidate pools for hard negatives

This is where we deliberately create difficult negative examples.

For example:

```text
Starbucks Coffee, Bandra
vs
Starbucks Coffee, Andheri
```

is much more useful than:

```text
Starbucks Coffee
vs
ABC Plumbing
```

Create a small candidate pool per block.

```python
BLOCK_POOL_SIZE = 20
```

```python
def create_block_pool(target_df):

    pool = (
        target_df
        .group_by("block_key")
        .agg(
            pl.col(ID_COL)
            .sample(
                n=BLOCK_POOL_SIZE,
                with_replacement=False,
                seed=SEED
            )
            .alias("candidate_ids")
        )
        .explode("candidate_ids")
        .rename({"candidate_ids": "negative_entity_id"})
    )

    return pool
```

Build:

```python
s2_block_pool = create_block_pool(source2)
s3_block_pool = create_block_pool(source3)

print("S2 block candidates:", s2_block_pool.height)
print("S3 block candidates:", s3_block_pool.height)
```

---

# Notebook Cell 17: Generate hard negatives

```python
def create_hard_negatives(
    s1_subset,
    target_df,
    block_pool,
    target_prefix,
    n_per_entity=1
):

    candidates = (
        s1_subset
        .select([
            ID_COL,
            "block_key"
        ])
        .join(
            block_pool,
            on="block_key",
            how="inner"
        )
        .filter(
            pl.col("negative_entity_id") != pl.col(ID_COL)
        )
    )

    # Retrieve target records
    target_small = target_df.rename({
        c: f"{target_prefix}_{c}"
        for c in target_df.columns
    })

    candidates = (
        candidates
        .join(
            target_small,
            left_on="negative_entity_id",
            right_on=f"{target_prefix}_{ID_COL}",
            how="inner"
        )
    )

    # Avoid using true positive pairs
    return candidates
```

We need to remove known positives after generating candidates.

```python
positive_s2_lookup = (
    gt_s2_train
    .select([
        pl.col(GT_S1_COL),
        pl.col("matched_entity_id")
    ])
)

positive_s3_lookup = (
    gt_s3_train
    .select([
        pl.col(GT_S1_COL),
        pl.col("matched_entity_id")
    ])
)
```

Generate candidate hard negatives:

```python
hard_s2_candidates = create_hard_negatives(
    s1_train,
    source2,
    s2_block_pool,
    "s2"
)

hard_s3_candidates = create_hard_negatives(
    s1_train,
    source3,
    s3_block_pool,
    "s3"
)

print("Hard S2 candidates:", hard_s2_candidates.height)
print("Hard S3 candidates:", hard_s3_candidates.height)
```

Filter known true matches:

```python
hard_s2_candidates = (
    hard_s2_candidates
    .join(
        positive_s2_lookup,
        left_on=[ID_COL, "negative_entity_id"],
        right_on=[GT_S1_COL, "matched_entity_id"],
        how="anti"
    )
)

hard_s3_candidates = (
    hard_s3_candidates
    .join(
        positive_s3_lookup,
        left_on=[ID_COL, "negative_entity_id"],
        right_on=[GT_S1_COL, "matched_entity_id"],
        how="anti"
    )
)
```

Now select one hard negative per Source 1 entity:

```python
hard_s2 = (
    hard_s2_candidates
    .group_by(ID_COL)
    .agg(
        pl.col("negative_entity_id")
        .sample(n=HARD_NEGATIVES_PER_POSITIVE, seed=SEED)
        .alias("negative_ids")
    )
    .explode("negative_ids")
)

hard_s3 = (
    hard_s3_candidates
    .group_by(ID_COL)
    .agg(
        pl.col("negative_entity_id")
        .sample(n=HARD_NEGATIVES_PER_POSITIVE, seed=SEED)
        .alias("negative_ids")
    )
    .explode("negative_ids")
)

print("Hard S2 negatives:", hard_s2.height)
print("Hard S3 negatives:", hard_s3.height)
```

---

# Notebook Cell 18: Random negatives

Hard negatives won't exist for every S1, especially when a block is unique.

So we'll also create random negatives from the same country.

```python
COUNTRY_POOL_SIZE = 100
```

```python
def create_country_pool(target_df):

    return (
        target_df
        .group_by("country_normalized")
        .agg(
            pl.col(ID_COL)
            .sample(
                n=COUNTRY_POOL_SIZE,
                with_replacement=False,
                seed=SEED
            )
            .alias("candidate_ids")
        )
        .explode("candidate_ids")
        .rename({"candidate_ids": "negative_entity_id"})
    )

s2_country_pool = create_country_pool(source2)
s3_country_pool = create_country_pool(source3)
```

```python
def random_country_negatives(
    s1_df,
    target_df,
    country_pool,
    target_prefix,
    positive_lookup
):

    candidates = (
        s1_df
        .select([
            ID_COL,
            "country_normalized"
        ])
        .join(
            country_pool,
            on="country_normalized",
            how="inner"
        )
    )

    candidates = (
        candidates
        .join(
            positive_lookup,
            left_on=[ID_COL, "negative_entity_id"],
            right_on=[GT_S1_COL, "matched_entity_id"],
            how="anti"
        )
    )

    return candidates
```

Generate:

```python
random_s2_candidates = random_country_negatives(
    s1_train,
    source2,
    s2_country_pool,
    "s2",
    positive_s2_lookup
)

random_s3_candidates = random_country_negatives(
    s1_train,
    source3,
    s3_country_pool,
    "s3",
    positive_s3_lookup
)
```

Pick one per S1:

```python
random_s2 = (
    random_s2_candidates
    .group_by(ID_COL)
    .agg(
        pl.col("negative_entity_id")
        .sample(n=RANDOM_NEGATIVES_PER_POSITIVE, seed=SEED)
        .alias("negative_ids")
    )
    .explode("negative_ids")
)

random_s3 = (
    random_s3_candidates
    .group_by(ID_COL)
    .agg(
        pl.col("negative_entity_id")
        .sample(n=RANDOM_NEGATIVES_PER_POSITIVE, seed=SEED)
        .alias("negative_ids")
    )
    .explode("negative_ids")
)

print("Random S2 negatives:", random_s2.height)
print("Random S3 negatives:", random_s3.height)
```

---

# Notebook Cell 19: Create pair dataframe

Now we'll turn everything into:

```text
text_a
text_b
label
source1_entity_id
target_entity_id
target_source
```

First, define our serialization.

```python
def clean_value(value):
    if value is None:
        return ""
    return str(value).strip()

def serialize_record(row, prefix):

    parts = []

    fields = [
        NAME_COL,
        ADDRESS_COL,
        COUNTRY_COL,
        "name_normalized",
        "address_normalized"
    ]

    for field in fields:
        col = f"{prefix}_{field}"

        if col in row:
            value = clean_value(row[col])

            if value:
                parts.append(
                    f"COL {field} VAL {value}"
                )

    # Optional structured fields
    for field in available_optional:

        col = f"{prefix}_{field}"

        if col in row:
            value = clean_value(row[col])

            if value:
                parts.append(
                    f"COL {field} VAL {value}"
                )

    return " ".join(parts)
```

For a first run, convert only the pair records to pandas.

---

# Notebook Cell 20: Build positive pair dataframe

```python
def positive_to_pandas(pairs, target_prefix, target_source):

    pdf = pairs.to_pandas()

    rows = []

    for _, row in pdf.iterrows():

        text_a = serialize_record(row, "s1_")
        text_b = serialize_record(row, f"{target_prefix}_")

        rows.append({
            "source1_entity_id": row[f"s1_{ID_COL}"],
            "target_entity_id": row[f"{target_prefix}_{ID_COL}"],
            "target_source": target_source,
            "text_a": text_a,
            "text_b": text_b,
            "label": 1
        })

    return pd.DataFrame(rows)
```

```python
pos_df_s2 = positive_to_pandas(
    positive_s2,
    "s2",
    "S2"
)

pos_df_s3 = positive_to_pandas(
    positive_s3,
    "s3",
    "S3"
)

positive_df = pd.concat(
    [pos_df_s2, pos_df_s3],
    ignore_index=True
)

print(positive_df.shape)
positive_df.head()
```

---

# Notebook Cell 21: Retrieve hard-negative records

```python
def negative_records_to_pairs(
    candidate_df,
    target_df,
    target_prefix,
    target_source
):

    candidate_ids = (
        candidate_df
        .select([
            ID_COL,
            "negative_ids"
        ])
        .rename({
            ID_COL: "source1_entity_id",
            "negative_ids": "target_entity_id"
        })
    )

    pair_data = (
        candidate_ids
        .join(
            source1.rename({
                c: f"s1_{c}"
                for c in source1.columns
            }),
            left_on="source1_entity_id",
            right_on=f"s1_{ID_COL}",
            how="inner"
        )
        .join(
            target_df.rename({
                c: f"{target_prefix}_{c}"
                for c in target_df.columns
            }),
            left_on="target_entity_id",
            right_on=f"{target_prefix}_{ID_COL}",
            how="inner"
        )
    )

    pdf = pair_data.to_pandas()

    rows = []

    for _, row in pdf.iterrows():

        text_a = serialize_record(row, "s1_")
        text_b = serialize_record(row, f"{target_prefix}_")

        rows.append({
            "source1_entity_id": row["source1_entity_id"],
            "target_entity_id": row["target_entity_id"],
            "target_source": target_source,
            "text_a": text_a,
            "text_b": text_b,
            "label": 0
        })

    return pd.DataFrame(rows)
```

---

# Notebook Cell 22: Build negative datasets

```python
hard_neg_s2_df = negative_records_to_pairs(
    hard_s2,
    source2,
    "s2",
    "S2"
)

hard_neg_s3_df = negative_records_to_pairs(
    hard_s3,
    source3,
    "s3",
    "S3"
)

random_neg_s2_df = negative_records_to_pairs(
    random_s2,
    source2,
    "s2",
    "S2"
)

random_neg_s3_df = negative_records_to_pairs(
    random_s3,
    source3,
    "s3",
    "S3"
)

negative_df = pd.concat(
    [
        hard_neg_s2_df,
        hard_neg_s3_df,
        random_neg_s2_df,
        random_neg_s3_df
    ],
    ignore_index=True
)

print(negative_df.shape)
```

---

# Notebook Cell 23: Final training pairs

```python
pairs_df = pd.concat(
    [positive_df, negative_df],
    ignore_index=True
)

pairs_df = (
    pairs_df
    .drop_duplicates(
        subset=[
            "source1_entity_id",
            "target_entity_id"
        ]
    )
    .sample(frac=1, random_state=SEED)
    .reset_index(drop=True)
)

print("Total training pairs:", len(pairs_df))

print(
    pairs_df["label"]
    .value_counts()
)

print("\nBy target source:")
print(
    pairs_df
    .groupby(["target_source", "label"])
    .size()
)
```

We want a reasonably balanced dataset.

Something like:

```text
0    1.0M
1    0.5M
```

is perfectly fine.

---

# Notebook Cell 24: Crucial split by Source 1 entity

**Do not randomly split individual pairs.**

Because one S1 can have multiple positive/negative pairs.

We'll split at the entity level.

```python
from sklearn.model_selection import GroupShuffleSplit

groups = pairs_df["source1_entity_id"]

gss1 = GroupShuffleSplit(
    n_splits=1,
    test_size=TEST_SIZE,
    random_state=SEED
)

train_val_idx, test_idx = next(
    gss1.split(
        pairs_df,
        groups=groups
    )
)

train_val_df = pairs_df.iloc[train_val_idx].reset_index(drop=True)
test_df = pairs_df.iloc[test_idx].reset_index(drop=True)

gss2 = GroupShuffleSplit(
    n_splits=1,
    test_size=VALID_SIZE / (1 - TEST_SIZE),
    random_state=SEED
)

train_idx, valid_idx = next(
    gss2.split(
        train_val_df,
        groups=train_val_df["source1_entity_id"]
    )
)

train_df = train_val_df.iloc[train_idx].reset_index(drop=True)
valid_df = train_val_df.iloc[valid_idx].reset_index(drop=True)

print("Train:", train_df.shape)
print("Validation:", valid_df.shape)
print("Test:", test_df.shape)
```

Verify there is no entity leakage:

```python
train_ids = set(train_df["source1_entity_id"])
valid_ids = set(valid_df["source1_entity_id"])
test_ids = set(test_df["source1_entity_id"])

print("Train ∩ Validation:", len(train_ids & valid_ids))
print("Train ∩ Test:", len(train_ids & test_ids))
print("Validation ∩ Test:", len(valid_ids & test_ids))
```

All three should be:

```text
0
```

---

# Notebook Cell 25: Convert to Hugging Face datasets

```python
from datasets import Dataset

train_dataset = Dataset.from_pandas(
    train_df[
        ["text_a", "text_b", "label"]
    ],
    preserve_index=False
)

valid_dataset = Dataset.from_pandas(
    valid_df[
        ["text_a", "text_b", "label"]
    ],
    preserve_index=False
)

test_dataset = Dataset.from_pandas(
    test_df[
        ["text_a", "text_b", "label"]
    ],
    preserve_index=False
)

print(train_dataset)
```

---

# Notebook Cell 26: Load XLM-R tokenizer

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

print(tokenizer)
```

---

# Notebook Cell 27: Tokenization

This is our **Ditto-style pair serialization + cross-encoder classification**.

```python
def tokenize_pairs(batch):

    return tokenizer(
        batch["text_a"],
        batch["text_b"],
        truncation=True,
        max_length=MAX_LENGTH,
        padding=False
    )
```

```python
tokenized_train = train_dataset.map(
    tokenize_pairs,
    batched=True,
    remove_columns=["text_a", "text_b"]
)

tokenized_valid = valid_dataset.map(
    tokenize_pairs,
    batched=True,
    remove_columns=["text_a", "text_b"]
)

tokenized_test = test_dataset.map(
    tokenize_pairs,
    batched=True,
    remove_columns=["text_a", "text_b"]
)

tokenized_train
```

---

# Notebook Cell 28: Load the model

```python
from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=2
)

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Device:", device)
```

We will let Trainer handle moving the model to CUDA.

---

# Notebook Cell 29: Metrics

```python
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    roc_auc_score
)

def compute_metrics(eval_pred):

    logits, labels = eval_pred

    predictions = np.argmax(
        logits,
        axis=-1
    )

    probabilities = torch.softmax(
        torch.tensor(logits),
        dim=-1
    )[:, 1].numpy()

    precision, recall, f1, _ = (
        precision_recall_fscore_support(
            labels,
            predictions,
            average="binary",
            zero_division=0
        )
    )

    return {
        "accuracy": accuracy_score(
            labels,
            predictions
        ),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc_score(
            labels,
            probabilities
        )
    }
```

---

# Notebook Cell 30: Data collator

```python
from transformers import DataCollatorWithPadding

data_collator = DataCollatorWithPadding(
    tokenizer=tokenizer,
    pad_to_multiple_of=8
)
```

---

# Notebook Cell 31: Training configuration

Because Transformers APIs evolve, this cell handles both current and older argument names.

```python
import inspect
from transformers import TrainingArguments

training_kwargs = dict(
    output_dir=str(OUTPUT_DIR / "xlmr_entity_matcher"),

    learning_rate=LEARNING_RATE,
    per_device_train_batch_size=TRAIN_BATCH_SIZE,
    per_device_eval_batch_size=EVAL_BATCH_SIZE,

    gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,

    num_train_epochs=NUM_EPOCHS,

    weight_decay=WEIGHT_DECAY,
    warmup_ratio=0.1,

    logging_steps=100,

    save_strategy="steps",
    save_steps=500,

    eval_steps=500,

    load_best_model_at_end=True,
    metric_for_best_model="f1",
    greater_is_better=True,

    fp16=torch.cuda.is_available(),

    dataloader_num_workers=0,

    report_to=[],

    seed=SEED,
    data_seed=SEED,

    remove_unused_columns=True
)

signature = inspect.signature(
    TrainingArguments.__init__
)

if "eval_strategy" in signature.parameters:
    training_kwargs["eval_strategy"] = "steps"
else:
    training_kwargs["evaluation_strategy"] = "steps"

training_args = TrainingArguments(
    **training_kwargs
)

print(training_args)
```

---

# Notebook Cell 32: Trainer

```python
from transformers import Trainer, EarlyStoppingCallback

trainer_kwargs = dict(
    model=model,

    args=training_args,

    train_dataset=tokenized_train,
    eval_dataset=tokenized_valid,

    data_collator=data_collator,

    compute_metrics=compute_metrics,

    callbacks=[
        EarlyStoppingCallback(
            early_stopping_patience=2
        )
    ]
)

trainer_signature = inspect.signature(
    Trainer.__init__
)

if "processing_class" in trainer_signature.parameters:
    trainer_kwargs["processing_class"] = tokenizer
else:
    trainer_kwargs["tokenizer"] = tokenizer

trainer = Trainer(
    **trainer_kwargs
)
```

---

# Notebook Cell 33: Train

```python
print("Starting XLM-R entity matching training...")

train_result = trainer.train()

print("\nTraining complete.")
```

With 24GB VRAM, this configuration should give us a serious first experiment.

---

# Notebook Cell 34: Validation evaluation

```python
validation_metrics = trainer.evaluate(
    tokenized_valid
)

validation_metrics
```

You should get:

```text
eval_loss
eval_accuracy
eval_precision
eval_recall
eval_f1
eval_roc_auc
```

Don't worry about the first result being perfect.

The first thing we want to know is:

> Does the supervised pair model learn the matching signal at all?

---

# Notebook Cell 35: Tune the matching threshold

We should **not automatically use 0.5**.

For entity matching, threshold selection matters.

```python
from sklearn.metrics import precision_score, recall_score, f1_score

valid_predictions = trainer.predict(
    tokenized_valid
)

valid_logits = valid_predictions.predictions
valid_labels = valid_predictions.label_ids

valid_probabilities = torch.softmax(
    torch.tensor(valid_logits),
    dim=-1
)[:, 1].numpy()
```

Scan thresholds:

```python
threshold_results = []

for threshold in np.arange(
    0.10,
    0.96,
    0.01
):

    pred = (
        valid_probabilities >= threshold
    ).astype(int)

    precision = precision_score(
        valid_labels,
        pred,
        zero_division=0
    )

    recall = recall_score(
        valid_labels,
        pred,
        zero_division=0
    )

    f1 = f1_score(
        valid_labels,
        pred,
        zero_division=0
    )

    threshold_results.append({
        "threshold": threshold,
        "precision": precision,
        "recall": recall,
        "f1": f1
    })

threshold_df = pd.DataFrame(
    threshold_results
)

best_threshold_row = threshold_df.loc[
    threshold_df["f1"].idxmax()
]

best_threshold_row
```

Store it:

```python
BEST_THRESHOLD = float(
    best_threshold_row["threshold"]
)

print("Best threshold:", BEST_THRESHOLD)
```

---

# Notebook Cell 36: Evaluate on the unseen test entities

```python
test_predictions = trainer.predict(
    tokenized_test
)

test_logits = test_predictions.predictions
test_labels = test_predictions.label_ids

test_probabilities = torch.softmax(
    torch.tensor(test_logits),
    dim=-1
)[:, 1].numpy()

test_pred = (
    test_probabilities >= BEST_THRESHOLD
).astype(int)

test_precision = precision_score(
    test_labels,
    test_pred,
    zero_division=0
)

test_recall = recall_score(
    test_labels,
    test_pred,
    zero_division=0
)

test_f1 = f1_score(
    test_labels,
    test_pred,
    zero_division=0
)

test_auc = roc_auc_score(
    test_labels,
    test_probabilities
)

print("====================================")
print("TEST RESULTS")
print("====================================")
print(f"Threshold : {BEST_THRESHOLD:.3f}")
print(f"Precision : {test_precision:.4f}")
print(f"Recall    : {test_recall:.4f}")
print(f"F1        : {test_f1:.4f}")
print(f"ROC-AUC   : {test_auc:.4f}")
```

---

# Notebook Cell 37: Save the trained model

```python
MODEL_OUTPUT = OUTPUT_DIR / "xlmr_business_matcher"

trainer.save_model(
    str(MODEL_OUTPUT)
)

tokenizer.save_pretrained(
    str(MODEL_OUTPUT)
)

print("Saved model to:")
print(MODEL_OUTPUT)
```

Save threshold:

```python
import json

with open(
    OUTPUT_DIR / "matching_config.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        {
            "model_name": MODEL_NAME,
            "max_length": MAX_LENGTH,
            "threshold": BEST_THRESHOLD,
            "seed": SEED
        },
        f,
        indent=2
    )
```

---

# What we've built

At this point the model is conceptually:

```text
                    S1
                     │
                     │
             ┌───────▼───────┐
             │ XLM-R Tokenizer│
             └───────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │    XLM-R     │
              │ Cross Encoder│
              └──────┬───────┘
                     │
                     ▼
              Match probability
                     │
              ┌──────┴──────┐
              │             │
             > T           < T
              │             │
           MATCH        NO MATCH
```

And the model sees something like:

```text
COL business_name VAL Starbucks Coffee
COL business_address VAL Shop 12 Linking Road Bandra West Mumbai
COL country VAL India
COL name_normalized VAL starbucks coffee
COL address_normalized VAL shop 12 linking road bandra west mumbai
```

against:

```text
COL business_name VAL Starbucks Coffee Mumbai
COL business_address VAL 12 Linking Rd Bandra W Mumbai
COL country VAL IN
COL name_normalized VAL starbucks coffee mumbai
COL address_normalized VAL 12 linking rd bandra w mumbai
```

That is effectively the **Ditto pair-classification concept**, without depending on its old repository stack. The original Ditto formulation also serializes attributes using `COL ... VAL ...` and treats entity matching as a sequence-pair classification task. ([GitHub](https://github.com/megagonlabs/ditto/blob/master/README.md?utm_source=chatgpt.com))

## One thing we are deliberately NOT doing yet

We are **not** doing:

```text
2M × 5M
```

or

```text
2M × 5M
```

for every Source 1 against Source 2 and Source 3.

That would be computationally impractical.

Once this model is trained and validated, the production architecture becomes:

```text
                    SOURCE 1
                      2M
                       │
                       ▼
              Candidate Retrieval
                 ┌─────┴─────┐
                 │           │
               S2 Top-K    S3 Top-K
                 │           │
                 └─────┬─────┘
                       ▼
                XLM-R Matcher
                       │
                       ▼
              threshold filtering
                       │
                       ▼
             S1 → ALL matched IDs
```

For that candidate-retrieval stage, I would add **BGE-M3 or another multilingual embedding index**, because BGE-M3 is designed for multilingual retrieval and supports more than 100 languages. Its own documentation also recommends retrieval followed by reranking, which maps nicely to our embedding-retrieval → XLM-R-reranking design. ([Hugging Face](https://huggingface.co/BAAI/bge-m3/blob/refs%2Fpr%2F1/README.md?utm_source=chatgpt.com))

So the immediate milestone is:

**Run through Cell 36 and get the first Precision / Recall / F1 / ROC-AUC.** Those numbers will tell us whether our pair construction and model formulation are working before we spend resources on the 2M × 10M production retrieval layer.

---

**Sources:**

- [README.md · FacebookAI/xlm-roberta-base at main](https://huggingface.co/FacebookAI/xlm-roberta-base/blame/main/README.md?utm_source=chatgpt.com)
- [ditto/README.md at master · megagonlabs/ditto · GitHub](https://github.com/megagonlabs/ditto/blob/master/README.md?utm_source=chatgpt.com)



---
Powered by [ChatGPT Exporter](https://www.chatgptexporter.com)
