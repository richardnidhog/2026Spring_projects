# Hospital Bed Monte Carlo Simulation — Results Summary

**Generated**: 2026-05-06 08:01:52

**Configuration**:

- Population: 2,710,000
- Total beds: 33,000
- Simulation days: 60
- Monte Carlo runs per scenario: 500
- Multiprocessing: enabled
- Total runtime: 42.6 seconds

---

## H1: Bed Doubling under COVID-only Surge (Delta variant)

Compares baseline beds vs doubled beds, no lockdown.

| Scenario | Beds | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |
|---|---:|---:|---:|---:|---:|---:|
| Before | 33,000 | 83.8% | 57.6 | [57.5, 57.7] | 2.13% | [1.61%, 2.65%] |
| After | 66,000 | 4.2% | 58.8 | [58.5, 59.0] | 34.48% | [33.02%, 35.94%] |

---

## H2: Bed Doubling under COVID + Influenza (Delta variant, doubled beds)

Both scenarios at 66,000 beds, no lockdown.

| Scenario | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |
|---|---:|---:|---:|---:|---:|
| COVID-only | 6.8% | 58.6 | [58.4, 58.8] | 35.29% | [33.79%, 36.79%] |
| COVID + Flu | 9.4% | 58.9 | [58.7, 59.0] | 30.50% | [29.02%, 31.99%] |

---

## H3: Lockdown Impact (3 categories × 3 lockdown levels)

### Influenza-only baseline (no COVID)

| Lockdown | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |
|---:|---:|---:|---:|---:|---:|
| 0% | 0.0% | — | — | 92.22% | [92.09%, 92.35%] |
| 25% | 0.0% | — | — | 98.26% | [98.24%, 98.29%] |
| 50% | 0.0% | — | — | 99.43% | [99.43%, 99.44%] |

### COVID-only by variant

#### Original

| Lockdown | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |
|---:|---:|---:|---:|---:|---:|
| 0% | 0.0% | — | — | 99.89% | [99.88%, 99.89%] |
| 25% | 0.0% | — | — | 99.97% | [99.97%, 99.97%] |
| 50% | 0.0% | — | — | 99.99% | [99.99%, 99.99%] |

#### Delta

| Lockdown | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |
|---:|---:|---:|---:|---:|---:|
| 0% | 82.8% | 57.5 | [57.4, 57.6] | 2.03% | [1.54%, 2.51%] |
| 25% | 0.0% | — | — | 83.50% | [83.16%, 83.85%] |
| 50% | 0.0% | — | — | 98.66% | [98.64%, 98.68%] |

#### Omicron

| Lockdown | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |
|---:|---:|---:|---:|---:|---:|
| 0% | 100.0% | 30.2 | [30.2, 30.3] | 0.00% | — |
| 25% | 100.0% | 35.4 | [35.3, 35.4] | 0.00% | — |
| 50% | 100.0% | 45.2 | [45.1, 45.3] | 0.00% | — |

### COVID + Influenza by variant

#### Original

| Lockdown | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |
|---:|---:|---:|---:|---:|---:|
| 0% | 0.0% | — | — | 92.06% | [91.93%, 92.19%] |
| 25% | 0.0% | — | — | 98.24% | [98.22%, 98.26%] |
| 50% | 0.0% | — | — | 99.42% | [99.42%, 99.43%] |

#### Delta

| Lockdown | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |
|---:|---:|---:|---:|---:|---:|
| 0% | 90.0% | 57.4 | [57.3, 57.5] | 1.45% | [0.99%, 1.90%] |
| 25% | 0.0% | — | — | 82.02% | [81.66%, 82.38%] |
| 50% | 0.0% | — | — | 98.08% | [98.06%, 98.11%] |

#### Omicron

| Lockdown | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |
|---:|---:|---:|---:|---:|---:|
| 0% | 100.0% | 30.1 | [30.1, 30.2] | 0.00% | — |
| 25% | 100.0% | 35.3 | [35.2, 35.4] | 0.00% | — |
| 50% | 100.0% | 45.3 | [45.2, 45.3] | 0.00% | — |

### Per-scenario diagnostics

**Omicron-only at lockdown = 0 %** (worst-case COVID surge)

- Overflow probability: 100.0%
- Mean overflow day: 30.3  (95 % CI [30.2, 30.4])
- Mean vacancy: 0.00%  (95 % CI —)

**Flu-only — infection dynamics across lockdown levels**

| Lockdown | Attack Rate | Attack Rate 5-95 band | Peak Active I | Peak Day |
|---:|---:|---:|---:|---:|
| 0% | 1.2470% | [0.8783%, 1.6623%] | 7,447 | 58.0 |
| 25% | 0.2903% | [0.2361%, 0.3547%] | 842 | 11.6 |
| 50% | 0.1014% | [0.0909%, 0.1141%] | 794 | 0.0 |

---

## Output files

All plot files are in `test_images/`.  Generated this run:

- **H1**: `H1_before-{beds-vs-days,overflow-hist,vacancy-hist}.png`, `H1_after-*.png`
- **H2**: `H2_covid_only_delta-*.png`, `H2_dual_pathogen_delta-*.png`
- **H3 summaries**: `H3_lockdown_flu_only.png`, `H3_lockdown_covid_only.png`, `H3_lockdown_dual.png`
- **H3 Omicron diagnostics**: `H3_omicron_only-{beds-vs-days,overflow-hist,vacancy-hist}.png`
- **H3 Flu diagnostics**: `H3_flu_only-active-infections.png`, `H3_flu_only-infection-proportion.png`, `H3_flu_only-lockdown-comparison.png`
