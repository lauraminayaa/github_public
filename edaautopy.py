# Automated EDA (Exploratory Data Analysis) Report
# This notebook generates a fast, business-friendly EDA report for any cleaned dataset.

# Import required libraries
# %pip install ydata-profiling pandas
import pandas as pd
from ydata_profiling import ProfileReport
import sys
print(sys.executable)

# Automated Data Drift Detection (Business-Adaptive)
from scipy.stats import ks_2samp
import pandas as pd
def detect_drift(df_new, df_ref, alpha=0.05, numeric_only=True, verbose=True):
    """Compare numeric distributions between df_new and df_ref using KS test.
    Returns a DataFrame with stat, p-value, drift flag, and a plain-language interpretation column when verbose=True.
    """
    cols = df_new.select_dtypes(include='number').columns if numeric_only else df_new.columns
    results = []
    for col in cols:
        if col in df_ref.columns:
            a = df_new[col].dropna()
            b = df_ref[col].dropna()
            if len(a) < 10 or len(b) < 10:
                results.append({'column':col,'stat':None,'p_value':None,'drift':False,'note':'too few samples','interpretation':'insufficient data for reliable test'})
                continue
            stat, p = ks_2samp(a, b)
            drift = p < alpha
            # interpretation heuristics
            if pd.isna(stat) or pd.isna(p):
                interp = 'test failed or returned NaN'
            elif drift:
                severity = 'large' if stat > 0.5 else 'moderate' if stat > 0.2 else 'small'
                interp = (f'Distribution changed (p={p:.4f}, stat={stat:.4f}) — {severity} shift detected. '
                          'Possible causes: operational change, seasonality, data-collection issue, or emerging market trend. '
                          'Business impact: predictive models relying on this feature may degrade; monitoring and investigation recommended.')
            else:
                interp = (f'No statistically significant distribution change (p={p:.4f}). '
                          'Minor fluctuations may be present but not statistically supported at the chosen alpha.')
            results.append({'column':col,'stat':stat,'p_value':p,'drift':drift,'note':'','interpretation':interp})
    res_df = pd.DataFrame(results).sort_values(by='p_value') if results else pd.DataFrame(columns=['column','stat','p_value','drift','interpretation'])
    if verbose:
        print('Data Drift Detection (KS Test):')
        try:
            display(res_df.style.format({'stat':'{:.4f}','p_value':'{:.4f}'}))
        except Exception:
            print(res_df)
        # summary guidance
        n_drift = int(res_df['drift'].sum()) if 'drift' in res_df.columns else 0
        total_tested = len(res_df)
        print(f'\nSummary: {n_drift} of {total_tested} tested numeric columns show statistically significant drift (alpha={alpha}).')
        if n_drift == 0:
            print('Interpretation: No major distribution-level changes detected between the two samples. Business continuity likely unaffected at feature-distribution level.')
        else:
            print('Interpretation: Some features shifted. Business implications may include: model performance degradation, changed customer behavior, or data collection issues.')
            print('Recommended actions:')
            print('- Verify ETL and data collection for recent changes or bugs.')
            print('- Check for known business events or seasonality that could explain shifts.')
            print('- If models use drifting features, run performance checks and consider retraining or adding drift-aware monitoring.')
    return res_df

# Usage: drift_df = detect_drift(df_new, df_reference)

# Explainable AI: SHAP Feature Impact (Business-Adaptive)
# Note: requires 'shap' installed. If not installed, run: %pip install shap
import shap
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import matplotlib.pyplot as plt
def explain_features(df, target=None, model=None, max_display=10, show_plot=True):
    """Train a simple tree model and show SHAP summary plot. Returns (model, explainer, shap_values).
    - Auto-detects target if not provided (last numeric column).
    - If a custom model is provided, uses that instead of RandomForest.
    """
