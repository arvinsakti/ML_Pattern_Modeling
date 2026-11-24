# Multiple Linear Regression via Cramer's Rule — Excel Implementation

This repository contains the Microsoft Excel workbook and datasets used in the article:

> A. C. Frobenius and F. X. W. Y. Untoro, "*[article title]*," *[journal name]*, [year]. DOI: [to be added]

The workbook fits a multiple linear regression model with two predictors,

$$Y = b_0 + b_1 X_1 + b_2 X_2$$

using the least-squares normal equations solved with Cramer's rule (determinants). It then predicts Y for new values of X1 and X2. The synthetic data in the article were generated with the rule **Y = X1 + X2**, and the workbook recovers this rule (b0 = 0, b1 = 1, b2 = 1).

## Repository contents

| File | Description |
|---|---|
| `mlr_cramer_rule.xlsx` | Excel workbook loaded with the main training dataset (observations 1–5) |
| `mlr_cramer_rule_second_training_set.xlsx` | Same workbook loaded with the second training dataset (10 observations) and the new input (2000, 24) |

Both workbooks use only built-in worksheet functions (no macros) and have three sheets:

- `DATASET +`: training data input and prediction input/output
- `PROSES +`: sums, matrices A–A3, determinants, and coefficients
- `EVALUATION`: training fit, ANOVA, coefficient t-tests, and prediction errors on the five test datasets (Table XVII of the article)
| `README.md` | This file |

## Requirements

- Microsoft Excel 2010 or later. LibreOffice Calc should also work, since only standard functions are used.
- No macros, add-ins, or internet connection are needed.

## How to use

1. **Enter the training data.** Open the `DATASET +` sheet and enter the training observations (X1, X2, Y) in columns D–F, starting at row 7.
2. **Check the computation.** Open the `PROSES +` sheet. It automatically computes:
   - the products X1·Y, X2·Y, X1·X2, X1², and X2² for each row;
   - the sums N, ΣX1, ΣX2, ΣY, ΣX1Y, ΣX2Y, ΣX1X2, ΣX1², and ΣX2²;
   - matrices A, A1, A2, and A3, and their determinants (using `MDETERM`);
   - the coefficients b0 = det(A1)/det(A), b1 = det(A2)/det(A), and b2 = det(A3)/det(A).
3. **Predict.** Return to the `DATASET +` sheet and enter new values of X1 and X2 in the input cells. The predicted value of Y appears automatically.
4. **Evaluate (optional).** Open the `EVALUATION` sheet to see the ANOVA table, the coefficient t-tests, and the prediction errors (MSE, MAE, RMSE, R²) for the training data and for each test dataset.

The training table holds up to 29 observations. If more rows are entered, a warning appears in the `PROSES +` sheet.

## Method

The least-squares coefficients satisfy the normal equations:

```
| N     ΣX1     ΣX2   | | b0 |   | ΣY   |
| ΣX1   ΣX1²    ΣX1X2 | | b1 | = | ΣX1Y |
| ΣX2   ΣX1X2   ΣX2²  | | b2 |   | ΣX2Y |
          A               b         h
```

Matrix Ak (k = 1, 2, 3) is A with column k replaced by h, and the coefficients are bk−1 = det(Ak) / det(A).

### Pseudocode

```
Input : training set {(X1_n, X2_n, Y_n)}, n = 1..N;  test input (X1*, X2*)
Output: b0, b1, b2 and prediction Ŷ*

1. For each row n: compute X1·Y, X2·Y, X1·X2, X1², X2²
2. N ← COUNT(rows); compute ΣX1, ΣX2, ΣY, ΣX1Y, ΣX2Y, ΣX1X2, ΣX1², ΣX2²
3. Build A and h; build A1, A2, A3
4. D ← MDETERM(A); D1 ← MDETERM(A1); D2 ← MDETERM(A2); D3 ← MDETERM(A3)
5. if |D| < 1e-9 then output "Dataset is unpredictable"; stop
6. b0 ← D1/D;  b1 ← D2/D;  b2 ← D3/D
7. Ŷ* ← b0 + b1·X1* + b2·X2*
8. return b0, b1, b2, Ŷ*
```

## Numerical precision

Excel stores and computes all numbers in 64-bit double-precision floating point (IEEE 754, about 15 significant digits). Integers and intermediate sums are therefore exact up to 2⁵³ ≈ 9 × 10¹⁵. Small round-off errors on the order of 10⁻¹⁵ can appear in the coefficients (for example, b0 = 1.98 × 10⁻¹⁵ or b1 = 0.9999999999999992). The values reported in the article are rounded for display.

## Singular matrix (det(A) = 0)

The coefficients cannot be estimated uniquely when det(A) = 0. This happens when:

- there are fewer than three observations (N < 3);
- one predictor has the same value in every observation; or
- X1 and X2 are perfectly collinear (for example, X2 = 2·X1 for all observations).

In these cases (|det(A)| < 10⁻⁹), the workbook displays **"Dataset is unpredictable"** instead of a prediction, and the coefficients, ANOVA, and t-tests are reported as undefined.

## Datasets used in the article

All data are synthetic and were generated with **Y = X1 + X2**.

**Training dataset (observations 1–5)**

| No | X1 | X2 | Y |
|---|---|---|---|
| 1 | 1 | 1 | 2 |
| 2 | 0 | 3 | 3 |
| 3 | 0 | 7 | 7 |
| 4 | 4 | 0 | 4 |
| 5 | 3 | 5 | 8 |

**Test datasets.** The model fitted on the training dataset is applied unchanged to each test set.

| Test set | Observations | (X1, X2) pairs |
|---|---|---|
| Test 1 | 6–10 | (1, 1), (3, 1), (2, 3), (6, 3), (4, 5) |
| Test 2 | 11–15 | (5, −6), (8, −4), (3, −9), (6, −8), (9, −7) |
| Test 3 | 16–20 | (5, 6), (7, 4), (3, 9), (6, 8), (9, 2) |
| Test 4 | 21–25 | (−5, −6), (−7, −4), (−3, −9), (−6, −8), (−9, −2) |
| Test 5 | 26–30 | (55, 66), (77, 44), (33, 99), (66, 88), (99, 99) |

**Second training dataset (additional experiment, 10 observations).** The coefficients are re-estimated from these observations only.

| No | X1 | X2 | Y |
|---|---|---|---|
| 1 | 11 | 222 | 233 |
| 2 | 0 | 963 | 963 |
| 3 | 0 | 72 | 72 |
| 4 | 465 | 0 | 465 |
| 5 | −375 | 5 | −370 |
| 6 | −305 | −125 | −430 |
| 7 | 453 | −153 | 300 |
| 8 | 1000 | 250 | 1250 |
| 9 | 1232 | 0 | 1232 |
| 10 | 4 | 567 | 571 |

New input: (X1, X2) = (2000, 24). Reference value: Y = 2024.

## Limitations

- The workbook handles exactly two predictors (X1 and X2).
- The data in the article are synthetic and noise-free, so exact recovery of the coefficients (MSE = 0, R² = 1) is expected. Performance on noisy or real-world data is not demonstrated here.
- With an exact fit, the residual variance is zero, so the conventional t- and F-statistics are undefined.

## Citation

If you use this workbook, please cite the article above and this repository:

```
A. C. Frobenius and F. X. W. Y. Untoro, "Multiple linear regression via Cramer's rule — Excel implementation," GitHub/Zenodo, [year]. DOI: [Zenodo DOI]
```

## License

[e.g., CC BY 4.0 — choose a license before publishing]

## Contact

- Arvin Claudy Frobenius — arvinclaudy@amikom.ac.id
- F. X. Wisnu Yudo Untoro — wisnuyudo@uwks.ac.id
