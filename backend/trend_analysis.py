from scipy.stats import linregress
import pymannkendall as mk

def analyze_trend(data: list[dict]) -> str:
    """
    Takes trend data and returns a summary using linear regression and Mann-Kendall test.
    """
    if not data:
        return "No data to analyze."

    years = [d['year'] for d in data]
    freq = [d['frequency'] for d in data]

    lin = linregress(years, freq)
    mk_result = mk.original_test(freq)

    return (
        f"Linear Trend: slope = {lin.slope:.2f}, p = {lin.pvalue:.3f}, R² = {lin.rvalue ** 2:.2f}. "
        f"Mann-Kendall: trend = {mk_result.trend}, p = {mk_result.p:.3f}."
    )
