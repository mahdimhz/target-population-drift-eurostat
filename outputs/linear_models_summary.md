# Linear and regularized models summary

The best test-set result among OLS, Ridge, and Lasso is from Lasso, with MAE 1.428, RMSE 1.887, and R-squared 0.385. The comparison uses the Phase 5a time-aware split and the same selected feature set for all three models.

Among the regularized models, Lasso has the lower test RMSE. It improves on OLS by 0.517 RMSE points and 0.509 MAE points.

The coefficients describe predictive associations in aggregate Eurostat country-year data. They should be read as model summaries for prediction, not as causal claims.
