from dataclasses import dataclass


@dataclass
class Job:
    company: str
    company_desc: str | None
    employees_num: str | None
    company_url: str | None  # taken from direct or linkedin for backup
    desc: str
    is_remote: bool
    level_desc: str | None
    url: str  # taken direct or from linkedin for backup
    location: str
    title: str

    def __init__(self, company: str, company_desc: str | None, employees_num: str | None, company_url: str | None,
                 desc: str, is_remote: bool, level_desc: str | None, url: str, location: str, title: str,
                 linkedin_url: str, linkedin_company: str):
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


    # todo - add rating system for job