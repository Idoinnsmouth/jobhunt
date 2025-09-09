import os

import pandas as pd
import keyring
from jobspy import scrape_jobs, JobResponse
from pandas import DataFrame

from create_report import create_report
from job import Job
from os_stuff import notify_and_open_report


def run():
    jobs_data = scrape_jobs(
        site_name=["linkedin"],
        search_term="python fullstack developer",
        google_search_term="python fullstack developer in tel aviv since yesterday",
        location="Tel aviv, Israel",
        country_indeed="Israel",
        linkedin_fetch_description=True,
        hours_old=24,
        results_wanted=50,
        proxies=get_proxys()
    )

    # example set of data
    # script_dir = os.path.dirname(os.path.abspath(__file__))
    # file_path = os.path.join(script_dir, 'a.csv')
    # jobs_data = pd.read_csv(file_path)
    # jobs_data.head()

    # -------------------------------------
    jobs = load_jobs_to_classes(jobs_data=jobs_data)
    report_name = create_report(jobs=jobs)

    notify_and_open_report(report_name)


def load_jobs_to_classes(jobs_data: DataFrame):
    jobs: list[Job] = []
    for data in jobs_data.itertuples(index=False):
        job = Job(
            company=data.company,
            company_desc=data.company_description,
            employees_num=data.company_num_employees,
            company_url=data.company_url_direct,
            desc=data.description,
            is_remote=data.is_remote,
            level_desc=data.job_level,
            url=data.job_url_direct,
            location=data.location,
            title=data.title,
            linkedin_url=data.job_url,
            linkedin_company=data.company_url
        )

        jobs.append(job)

    return jobs

def get_proxys() -> list[str]:
    PORT = "1080"
    with open("env/proxies.txt", "r") as f:
        ips = f.read().split(",")

    username = keyring.get_password("nordvpn1", "username")
    password = keyring.get_password("nordvpn1", "password")

    return [f"socks5h://{username}:{password}@{ip}:{PORT}" for ip in ips]


if __name__ == "__main__":
    run()