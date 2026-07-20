# Feature Summary Statistics

Total messages: 42,363 | Registers: 11

## Key Metrics by Register

| Register | N | Mean Words | Mean Zipf | Contract Rate | Caps Rate | Profanity Rate | Q Density |
|----------|---|-----------|-----------|--------------|-----------|---------------|----------|
| ACADEMIC | 1,361 | 68.7 | 4.33 | 0.44 | 17.75 | 0.60 | 0.181 |
| ARGUMENTATIVE | 6 | 307.2 | 4.70 | 1.77 | 47.73 | 0.34 | 0.079 |
| CASUAL | 7,106 | 7.4 | 4.55 | 0.74 | 10.62 | 1.38 | 0.086 |
| CREATIVE_DIRECTION | 657 | 155.4 | 4.44 | 0.42 | 13.76 | 0.24 | 0.117 |
| FRUSTRATED | 127 | 151.4 | 4.23 | 0.59 | 31.41 | 36.33 | 0.383 |
| INVESTIGATE | 1,633 | 86.3 | 4.36 | 0.38 | 20.54 | 0.38 | 0.154 |
| MECHANICAL | 1,680 | 112.3 | 4.40 | 0.44 | 15.15 | 0.52 | 0.143 |
| PERSONAL | 610 | 147.6 | 4.42 | 0.58 | 22.70 | 0.29 | 0.147 |
| PROFESSIONAL | 6,403 | 154.7 | 4.46 | 0.43 | 13.23 | 0.41 | 0.142 |
| TECH | 15,480 | 157.9 | 4.08 | 0.29 | 22.90 | 0.42 | 0.141 |
| UNTAGGED | 7,300 | 51.9 | 4.52 | 0.44 | 10.76 | 0.20 | 0.166 |

## Vocabulary Rarity Distribution by Register (Kite Shape)

| Register | 1.0-2.0 | 2.0-3.0 | 3.0-4.0 | 4.0-5.0 | 5.0-6.0 | 6.0-10.0 |
|----------|---|---|---|---|---|---|
| ACADEMIC | 19 | 48 | 222 | 809 | 153 | 2 |
| ARGUMENTATIVE | 0 | 0 | 0 | 6 | 0 | 0 |
| CASUAL | 68 | 216 | 640 | 2013 | 1546 | 80 |
| CREATIVE_DIRECTION | 6 | 17 | 80 | 416 | 82 | 2 |
| FRUSTRATED | 4 | 10 | 19 | 74 | 16 | 0 |
| INVESTIGATE | 8 | 52 | 239 | 998 | 166 | 1 |
| MECHANICAL | 12 | 36 | 236 | 1069 | 203 | 4 |
| PERSONAL | 4 | 8 | 87 | 429 | 62 | 0 |
| PROFESSIONAL | 36 | 120 | 767 | 4389 | 736 | 12 |
| TECH | 310 | 1033 | 3980 | 8004 | 1027 | 9 |
| UNTAGGED | 12 | 90 | 815 | 5390 | 986 | 2 |

## Sentence Length Distribution by Register

| Register | 1-5 | 5-10 | 10-15 | 15-20 | 20-30 | 30-999 |
|----------|---|---|---|---|---|---|
| ACADEMIC | 185 | 314 | 356 | 233 | 156 | 117 |
| ARGUMENTATIVE | 0 | 0 | 3 | 1 | 1 | 1 |
| CASUAL | 4200 | 2388 | 314 | 121 | 60 | 23 |
| CREATIVE_DIRECTION | 96 | 162 | 172 | 109 | 80 | 38 |
| FRUSTRATED | 15 | 41 | 38 | 15 | 15 | 3 |
| INVESTIGATE | 275 | 349 | 411 | 275 | 199 | 124 |
| MECHANICAL | 245 | 436 | 428 | 244 | 173 | 154 |
| PERSONAL | 43 | 136 | 179 | 118 | 111 | 23 |
| PROFESSIONAL | 673 | 1453 | 1775 | 1181 | 904 | 417 |
| TECH | 1772 | 2888 | 3483 | 2431 | 2037 | 2863 |
| UNTAGGED | 182 | 1779 | 2413 | 1527 | 980 | 418 |

## Bimodality Detection (Sentence Length)

- **TECH**: BC=0.6169, bimodal=True (n=15480)
- **CREATIVE_DIRECTION**: BC=0.6451, bimodal=True (n=657)

## Cross-Register Feature Rankings (by mean)

- **mean_zipf**: highest=ARGUMENTATIVE (4.704), lowest=TECH (4.081)
- **contraction_rate**: highest=ARGUMENTATIVE (1.770), lowest=TECH (0.294)
- **profanity_rate**: highest=FRUSTRATED (36.334), lowest=UNTAGGED (0.199)
- **caps_emphasis_rate**: highest=ARGUMENTATIVE (47.732), lowest=CASUAL (10.617)
- **question_density**: highest=FRUSTRATED (0.383), lowest=ARGUMENTATIVE (0.079)
- **mean_sentence_len**: highest=TECH (25.147), lowest=CASUAL (4.573)
- **type_token_ratio**: highest=CASUAL (0.986), lowest=ARGUMENTATIVE (0.676)
- **pct_rare**: highest=TECH (7.267), lowest=ARGUMENTATIVE (4.883)
