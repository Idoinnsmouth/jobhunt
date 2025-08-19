import os

from pync import Notifier

def notify_and_open_report(report_name: str):
    file_path = f"{os.getcwd()}/reports/{report_name}.xlsx"
    file_path = os.path.abspath(file_path)

    Notifier.notify(
        "Generated new job reports",
        title="Job Reports",
        sound="glass",
        execute=f"open {file_path}"
    )

