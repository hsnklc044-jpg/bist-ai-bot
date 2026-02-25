from openpyxl import Workbook

def generate_weekly_report():
    wb = Workbook()
    ws = wb.active
    ws.title = "Test"

    ws.append(["Test"])
    ws.append(["Railway Çalışıyor"])

    filename = "/tmp/test.xlsx"
    wb.save(filename)

    return filename
