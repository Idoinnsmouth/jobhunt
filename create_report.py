from dataclasses import asdict
from datetime import datetime

import pandas as pd
from openpyxl.reader.excel import load_workbook
from openpyxl.styles import Alignment

from job import Job

COLUMNS = {
    "company": "Company",
    "title": "Job Title",
    "desc": "Job Description",
    "location": "Location",
    "level_desc": "Job 'Level'",
    "url": "Job Apply Link",
    "company_desc": "Company Description",
    "company_url": "Company Site",
    "employees_num": "Number of Employees",
    "is_remote": "Remote",
}

def create_report(jobs: list[Job]) -> str:
    df = pd.DataFrame([asdict(job) for job in jobs])[list(COLUMNS.keys())]

    df.rename(columns=COLUMNS, inplace=True)
    df.sort_values(by=["Company"], inplace=True)

    time = datetime.now()
    name = f"job_report_{time.day}-{time.month}-{time.year}"
    df.to_excel(f"reports/{name}.xlsx", index=False)
    _post_creation_changes(name)

    return name


def _post_creation_changes(report_name: str):
    wb = load_workbook(f"reports/{report_name}.xlsx")
    ws = wb.active


    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True)

            if cell.column_letter == "C":
                ws.column_dimensions["C"].width = 40
            else:
                ws.column_dimensions[cell.column_letter].bestFit = True

    wb.save(f"reports/{report_name}.xlsx")