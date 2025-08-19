import os

from pync import Notifier

def notify_mac(title: str, message: str, file_name: str):
    file_path = f"{os.getcwd()}/reports/{file_name}.xlsx"
    file_path = os.path.abspath(file_path)

    Notifier.notify(
        message,
        title=title,
        sound="glass",
        execute=f"say 'Master Noy, you job report is ready' | open {file_path}"
    )


if __name__ == "__main__":
    notify_mac("Job Alert", "New job added to your spreadsheet!", "job_report_19-8-2025")
