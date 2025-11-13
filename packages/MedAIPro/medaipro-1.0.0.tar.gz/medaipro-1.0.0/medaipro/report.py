from fpdf import FPDF

def generate_report(results, output="report.pdf"):
    """生成醫療報告 PDF"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="MedAIPro 醫療分析報告", ln=True, align="C")
    pdf.ln(10)
    for k, v in results.items():
        pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)
    pdf.output(output)
    return f"報告已生成：{output}"
