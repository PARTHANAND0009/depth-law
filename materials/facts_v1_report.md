# P2 facts v1: selection report

- **Rules:** `materials/SAMPLING_RULES_v1.md`; seed 20261121.
- **Facts:** 300, from 20 relations; sha256 0f596cd7385a318b9f2d8bea84d5d8cf483ee62c9333fa3bec0ecd60d9f1bfe3.

| relation | pool | eligible | fail frac | tercile sizes | eligible relation | selected | influential (0a) | reason excluded |
|---|---|---|---|---|---|---|---|---|
| capital | 200 | 145 | 0.28 | [49, 48, 48] | False | False | False | 0.28 of pool fail distinct/contentful first token |
| citizenship | 200 | 197 | 0.01 | [66, 65, 66] | True | True | False |  |
| company_ceo | 200 | 110 | 0.45 | [37, 36, 37] | False | False | True | 0.45 of pool fail distinct/contentful first token |
| constellation | 200 | 143 | 0.28 | [48, 47, 48] | False | False | False | 0.28 of pool fail distinct/contentful first token |
| continent | 200 | 200 | 0.00 | [67, 66, 67] | True | True | False |  |
| country | 200 | 199 | 0.01 | [67, 66, 66] | True | True | False |  |
| country_of_origin | 200 | 200 | 0.00 | [67, 66, 67] | True | True | False |  |
| developer | 200 | 183 | 0.09 | [61, 61, 61] | True | False | True |  |
| employer | 200 | 199 | 0.01 | [67, 66, 66] | True | True | False |  |
| field_of_work | 200 | 200 | 0.00 | [67, 66, 67] | True | True | False |  |
| formation_location | 200 | 198 | 0.01 | [66, 66, 66] | True | True | False |  |
| headquarters | 200 | 198 | 0.01 | [66, 66, 66] | True | True | False |  |
| instrument | 200 | 200 | 0.00 | [67, 66, 67] | True | True | False |  |
| manufacturer | 200 | 184 | 0.08 | [62, 61, 61] | True | True | True |  |
| music_genre | 200 | 200 | 0.00 | [67, 66, 67] | True | True | False |  |
| native_language | 200 | 200 | 0.00 | [67, 66, 67] | True | True | False |  |
| occupation | 200 | 200 | 0.00 | [67, 66, 67] | True | True | False |  |
| official_language | 200 | 200 | 0.00 | [67, 66, 67] | True | True | False |  |
| original_language | 200 | 200 | 0.00 | [67, 66, 67] | True | True | False |  |
| original_network | 200 | 197 | 0.01 | [66, 65, 66] | True | True | False |  |
| place_of_birth | 200 | 180 | 0.10 | [60, 60, 60] | True | False | False |  |
| place_of_death | 200 | 199 | 0.01 | [67, 66, 66] | True | True | False |  |
| religion | 200 | 181 | 0.10 | [61, 60, 60] | True | False | False |  |
| sport | 200 | 198 | 0.01 | [66, 66, 66] | True | True | False |  |
| sport_position | 200 | 200 | 0.00 | [67, 66, 67] | True | True | False |  |
| work_location | 200 | 193 | 0.04 | [65, 64, 64] | True | True | False |  |
