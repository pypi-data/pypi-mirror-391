import pandas as pd
from scipy import stats

def t_test(group1, group2):
    """雙樣本 t 檢定"""
    t, p = stats.ttest_ind(group1, group2)
    return {"t值": round(t, 3), "p值": round(p, 5), "顯著": p < 0.05}

def chi_square(observed, expected):
    """卡方檢定"""
    chi2, p = stats.chisquare(observed, expected)
    return {"chi2": round(chi2, 3), "p值": round(p, 5)}
