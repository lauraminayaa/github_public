"""Reusable EDA helpers extracted from the notebook for reuse across projects.
This module contains lightweight wrappers so the notebook can import and use them
without duplicating code. Keep small and dependency-free where possible.
"""

import logging
import pandas as pd
import numpy as np
from scipy.stats import ks_2samp

logger = logging.getLogger(__name__)


def business_kpis(df, revenue_aliases=None, customer_aliases=None):
    revenue_aliases = revenue_aliases or ['revenue', 'amount', 'sales', 'total']
    customer_aliases = customer_aliases or ['customerid', 'customer_id', 'client_id', 'customer']
    revenue_col = next((c for c in df.columns if any(k in c.lower() for k in revenue_aliases)), None)
    customer_col = next((c for c in df.columns if any(k in c.lower() for k in customer_aliases)), None)
    kpis = {}
    if revenue_col is not None:
        kpis['total_revenue'] = float(df[revenue_col].sum(skipna=True))
    else:
        kpis['total_revenue'] = None
    if customer_col is not None:
        kpis['unique_customers'] = int(df[customer_col].nunique(dropna=True))
    else:
        kpis['unique_customers'] = None
    if kpis.get('total_revenue') and kpis.get('unique_customers'):
        kpis['avg_revenue_per_customer'] = float(kpis['total_revenue'] / max(1, kpis['unique_customers']))
    else:
        kpis['avg_revenue_per_customer'] = None
    return kpis


def detect_drift(df_new, df_ref, alpha=0.05):
    cols = df_new.select_dtypes(include='number').columns
    results = []
    for col in cols:
        if col in df_ref.columns:
            a = df_new[col].dropna()
            b = df_ref[col].dropna()
            if len(a) < 10 or len(b) < 10:
                results.append({'column': col, 'stat': None, 'p_value': None, 'drift': False})
                continue
            stat, p = ks_2samp(a, b)
            results.append({'column': col, 'stat': float(stat), 'p_value': float(p), 'drift': bool(p < alpha)})
    return pd.DataFrame(results)
