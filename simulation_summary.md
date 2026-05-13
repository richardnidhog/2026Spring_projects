# Hospital Bed Monte Carlo Simulation — Results Summary

**Generated**: 2026-05-13 14:39:07

**Configuration**:

- Population: 2,710,000
- Total beds: 33,000
- Simulation days: 60
- Monte Carlo runs per scenario: 1000
- Multiprocessing: enabled
- Total runtime: 49.4 seconds

---

## H1: Bed Doubling under COVID-only Surge (Delta variant)

Compares baseline beds vs doubled beds, no lockdown.

| Scenario | Beds | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |
|---|---:|---:|---:|---:|---:|---:|
| Before | 33,000 | 82.2% | 57.6 | [57.6, 57.7] | 2.62% | [2.19%, 3.04%] |
| After | 66,000 | 6.3% | 58.7 | [58.5, 58.8] | 35.12% | [34.07%, 36.17%] |

---

## H2: Bed Doubling under COVID + Influenza (Delta variant, doubled beds)

Both scenarios at 66,000 beds, no lockdown.

| Scenario | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |
|---|---:|---:|---:|---:|---:|
| COVID-only | 6.6% | 58.7 | [58.6, 58.8] | 33.61% | [32.56%, 34.65%] |
| COVID + Flu | 7.3% | 58.8 | [58.6, 58.9] | 30.55% | [29.53%, 31.57%] |

---

## H3: Lockdown Impact (3 categories × 3 lockdown levels)

### Influenza-only baseline (no COVID)

| Lockdown | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |
|---:|---:|---:|---:|---:|---:|
| 0% | 0.0% | — | — | 92.18% | [92.08%, 92.28%] |
| 25% | 0.0% | — | — | 98.27% | [98.25%, 98.29%] |
| 50% | 0.0% | — | — | 99.43% | [99.43%, 99.43%] |

### COVID-only by variant

#### Original

| Lockdown | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |
|---:|---:|---:|---:|---:|---:|
| 0% | 0.0% | — | — | 99.89% | [99.89%, 99.89%] |
| 25% | 0.0% | — | — | 99.97% | [99.97%, 99.97%] |
| 50% | 0.0% | — | — | 99.99% | [99.99%, 99.99%] |

#### Delta

| Lockdown | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |
|---:|---:|---:|---:|---:|---:|
| 0% | 82.9% | 57.6 | [57.5, 57.7] | 2.38% | [1.97%, 2.79%] |
| 25% | 0.0% | — | — | 83.64% | [83.39%, 83.89%] |
| 50% | 0.0% | — | — | 98.63% | [98.62%, 98.65%] |

#### Omicron

| Lockdown | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |
|---:|---:|---:|---:|---:|---:|
| 0% | 100.0% | 30.2 | [30.2, 30.2] | 0.00% | — |
| 25% | 100.0% | 35.3 | [35.2, 35.3] | 0.00% | — |
| 50% | 100.0% | 45.3 | [45.2, 45.3] | 0.00% | — |

### COVID + Influenza by variant

#### Original

| Lockdown | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |
|---:|---:|---:|---:|---:|---:|
| 0% | 0.0% | — | — | 92.07% | [91.97%, 92.17%] |
| 25% | 0.0% | — | — | 98.24% | [98.22%, 98.25%] |
| 50% | 0.0% | — | — | 99.43% | [99.42%, 99.43%] |

#### Delta

| Lockdown | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |
|---:|---:|---:|---:|---:|---:|
| 0% | 89.9% | 57.3 | [57.2, 57.4] | 1.23% | [0.94%, 1.52%] |
| 25% | 0.0% | — | — | 81.61% | [81.37%, 81.86%] |
| 50% | 0.0% | — | — | 98.07% | [98.06%, 98.09%] |

#### Omicron

| Lockdown | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |
|---:|---:|---:|---:|---:|---:|
| 0% | 100.0% | 30.2 | [30.1, 30.2] | 0.00% | — |
| 25% | 100.0% | 35.3 | [35.2, 35.3] | 0.00% | — |
| 50% | 100.0% | 45.2 | [45.2, 45.3] | 0.00% | — |

### Per-scenario diagnostics

**Omicron-only at lockdown = 0 %** (worst-case COVID surge)

- Overflow probability: 100.0%
- Mean overflow day: 30.2  (95 % CI [30.2, 30.3])
- Mean vacancy: 0.00%  (95 % CI —)

**Flu-only — infection dynamics across lockdown levels**

| Lockdown | Attack Rate | Attack Rate 5-95 band | Peak Active I | Peak Day |
|---:|---:|---:|---:|---:|
| 0% | 1.2581% | [0.9288%, 1.6956%] | 7,519 | 57.9 |
| 25% | 0.2930% | [0.2348%, 0.3623%] | 849 | 13.0 |
| 50% | 0.1022% | [0.0912%, 0.1148%] | 796 | 0.0 |

---

## Output files

All plot files are in `test_images/`.  Generated this run:

- **H1**: `H1_before-{beds-vs-days,overflow-hist,vacancy-hist}.png`, `H1_after-*.png`
- **H2**: `H2_covid_only_delta-*.png`, `H2_dual_pathogen_delta-*.png`
- **H3 summaries**: `H3_lockdown_flu_only.png`, `H3_lockdown_covid_only.png`, `H3_lockdown_dual.png`
- **H3 Omicron diagnostics**: `H3_omicron_only-{beds-vs-days,overflow-hist,vacancy-hist}.png`
- **H3 Flu diagnostics**: `H3_flu_only-active-infections.png`, `H3_flu_only-infection-proportion.png`, `H3_flu_only-lockdown-comparison.png`
