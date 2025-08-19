import pandas as pd
from jobspy import scrape_jobs, JobPost
from pandas import DataFrame

from job import Job


def run():
    # jobs_data = scrape_jobs(
    #     # glassdoor isn't working
    #     site_name=["linkedin", "indeed", "google"],
    #     search_term="python fullstack developer",
    #     google_search_term="python fullstack developer in tel aviv since yesterday",
    #     location="Tel aviv, Israel",
    #     country_indeed="israel",
    #     linkedin_fetch_description=True,
    # )

    jobs_data = pd.read_csv('a.csv')
    jobs_data.head()

    # -------------------------------------
    jobs = load_jobs_to_classes(jobs_data=jobs_data)



def load_jobs_to_classes(jobs_data: DataFrame):
    jobs: list[Job] = []
    for data in jobs_data.itertuples(index=False):
        data: JobPost
        job = Job(
            company=data.company_name,
            company_desc=data.company_description,
            employees_num=data.company_num_employees,
            company_url=data.company_url_direct,
            desc=data.description,
            is_remote=data.is_remote,
            level_desc=data.job_level,
            url=data.job_url_direct,
            location=data.location.display_location(),
            title=data.title,
            linkedin_url=data.job_url,
            linkedin_company=data.company_url
        )

        jobs.append(job)

        return jobs

if __name__ == "__main__":
    run()