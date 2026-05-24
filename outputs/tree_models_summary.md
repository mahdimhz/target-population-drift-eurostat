# Tree models summary

The best tree-based test result is from Gradient Boosting, with MAE 1.130, RMSE 1.526, and R-squared 0.598.

The best tree model, Gradient Boosting, has lower test RMSE than the best linear model, Lasso. The RMSE difference is 0.361 points, and the MAE difference is 0.298 points.

The highest predictive-importance features in the selected tree model are: `physicians_per_100k`, `gini_income`, `poverty_or_social_exclusion_pc`, `long_term_unemployment_rate_pc`, `hospital_beds_per_100k`.

These importance values describe prediction patterns in the fitted model. They are not causal evidence and should not be read as policy evaluation.
