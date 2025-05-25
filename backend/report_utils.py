# report_utils.py
import pandas as pd
from fpdf import FPDF
from scipy.stats import linregress
import pymannkendall as mk

def generate_csv(trends, path="trend_insights.csv"):
    df = pd.DataFrame(trends)
    df.to_csv(path, index=False)
    return path

def generate_pdf(trends, hazard_type, summary, path="trend_insights_summary.pdf"):
    df = pd.DataFrame(trends)
    years = df["year"]
    frequencies = df["frequency"]

    linreg = linregress(years, frequencies)
    mk_result = mk.original_test(frequencies)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"{hazard_type.title()} Trend Summary", ln=True, align="C")
    pdf.ln(10)

    pdf.multi_cell(0, 10, summary)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Linear Regression: slope = {linreg.slope:.2f}, p = {linreg.pvalue:.3f}, R² = {linreg.rvalue**2:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Mann-Kendall: trend = {mk_result.trend}, p = {mk_result.p:.3f}", ln=True)

    pdf.ln(10)
    pdf.cell(200, 10, txt="Year-wise Data", ln=True)
    for t in trends:
        pdf.cell(200, 10, txt=f"Year: {t['year']}, Frequency: {t['frequency']}", ln=True)

    pdf.output(path)
    return path
