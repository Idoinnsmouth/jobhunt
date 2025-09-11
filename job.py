import logging
from dataclasses import dataclass

from job_analysis import score_job_description


@dataclass
class Job:
    company: str
    company_desc: str | None
    employees_num: str | None
    company_url: str | None
    desc: str
    is_remote: bool
    level_desc: str | None
    url: str
    location: str
    title: str
    rating: int

    def __init__(self, company: str, company_desc: str | None, employees_num: str | None,
                 company_url: str | None, desc: str, is_remote: bool,
                 level_desc: str | None, url: str, location: str, title: str,
                 linkedin_url: str, linkedin_company: str):
        # todo - handle nans that we have instead of None
        self.company = company
        self.company_desc = company_desc
        self.employees_num = employees_num
        self.company_url = company_url or linkedin_company
        self.desc = desc
        self.is_remote = is_remote
        self.level_desc = level_desc
        self.url = url or linkedin_url
        self.location = location
        self.title = title

        try:
            # todo - move this to main.py instead of doing this while loading the dataclass (in case of specific error)
            if type(self.desc) is not float:
                _rating = score_job_description(self.desc).score
        except Exception as e:
            _rating = 0
            logging.exception(e)
            pass

        self.rating = _rating