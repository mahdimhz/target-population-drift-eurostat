# Feature engineering summary

The extended panel keeps 608 observed country-year rows from the Phase 1 panel. 5 new Eurostat feature datasets were merged.

The feature view contains 18 columns: 5 original controls, 5 new variables, and 8 transformed, lag, or change variables.

Main missingness introduced by new features:
- `gini_income` has 199 missing rows after the left merge.
- `physicians_per_100k` has 177 missing rows after the left merge.
- `oop_health_expenditure_share_pc` has 164 missing rows after the left merge.
- `hospital_beds_per_100k` has 86 missing rows after the left merge.
- `long_term_unemployment_rate_pc` has 54 missing rows after the left merge.

Lag variables are missing for the first observed year within each country. No values were carried forward.
