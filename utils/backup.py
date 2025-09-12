import os
from typing import Union

from pandas import DataFrame, read_csv

SCRAPING_BACKUP_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backup_results",
                                         "scraping_backup.csv")


def save_scraping_results_to_backup_folder(scraping_results: DataFrame, file_path: str = None):
    path = file_path or SCRAPING_BACKUP_FILE_PATH
    with open(path, "w") as f:
        f.write(scraping_results.to_csv(index=False))


def delete_scraping_results_from_backup_folder(file_path: str = None):
    path = file_path or SCRAPING_BACKUP_FILE_PATH

    if os.path.exists(path):
        os.remove(path)

def get_scraping_results_from_back_folder(file_path: str = None) -> Union[DataFrame, None]:
    path = file_path or SCRAPING_BACKUP_FILE_PATH

    if os.path.exists(path):
        return read_csv(path)
    else:
        return None


