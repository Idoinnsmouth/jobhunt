import os
from unittest import TestCase

from pandas import DataFrame
from pandas._testing import assert_frame_equal

from utils.backup import save_scraping_results_to_backup_folder, delete_scraping_results_from_backup_folder, \
    get_scraping_results_from_back_folder


def create_mock_dataframe() -> DataFrame:
    data = [
        {
            "company": "TestCorp",
            "company_description": "A fictional company for testing.",
            "company_num_employees": 100,
            "company_url_direct": "https://testcorp.com",
            "description": "We are looking for a backend engineer.",
            "is_remote": True,
            "job_level": "Mid",
            "job_url_direct": "https://testcorp.com/careers/job1",
            "location": "Tel Aviv, Israel",
            "title": "Backend Engineer",
            "job_url": "https://linkedin.com/jobs/view/123",
            "company_url": "https://linkedin.com/company/testcorp",
        },
        {
            "company": "Sample Inc",
            "company_description": "Another test company.",
            "company_num_employees": 50,
            "company_url_direct": "https://sampleinc.com",
            "description": "Frontend role in React.",
            "is_remote": False,
            "job_level": "Junior",
            "job_url_direct": "https://sampleinc.com/careers/job2",
            "location": "Remote",
            "title": "Frontend Developer",
            "job_url": "https://linkedin.com/jobs/view/456",
            "company_url": "https://linkedin.com/company/sampleinc",
        },
    ]
    return DataFrame(data)

class TestBackup(TestCase):
    mock_file_path = os.path.join(os.getcwd(), "mock_dataframe_data.csv")

    def assertDataframeEqual(self, a, b):
        try:
            assert_frame_equal(a, b)
        except AssertionError as e:
            raise self.failureException() from e

    def tearDown(self):
        if os.path.exists(self.mock_file_path):
            os.remove(self.mock_file_path)

    def test_save_scraping_results_to_backup_folder_create_backup(self):
        save_scraping_results_to_backup_folder(
            scraping_results=create_mock_dataframe(),
            file_path=self.mock_file_path
        )

        self.assertTrue(os.path.exists(self.mock_file_path))

        with open(self.mock_file_path, "r") as f:
            self.assertEqual(create_mock_dataframe().to_csv(index=False), f.read())

    def test_delete_scraping_results_from_backup_folder_deletes_file_when_exist(self):
        with open(self.mock_file_path, "x") as f:
            f.write("data,data,data,data")

        delete_scraping_results_from_backup_folder(file_path=self.mock_file_path)

        self.assertFalse(os.path.exists(self.mock_file_path))

    def test_delete_scraping_results_from_backup_folder_does_not_raise_error_when_file_not_found(self):
        delete_scraping_results_from_backup_folder(file_path=self.mock_file_path)


    def test_get_scraping_results_from_back_folder_returns_data_when_file_exist(self):
        mock_data = create_mock_dataframe()

        with open(self.mock_file_path, "w") as f:
            f.write(mock_data.to_csv(index=False))

        res = get_scraping_results_from_back_folder(self.mock_file_path)

        self.assertDataframeEqual(mock_data, res)


    def test_get_scraping_results_from_back_folder_returns_none_if_file_does_not_exist(self):
        res = get_scraping_results_from_back_folder(self.mock_file_path)
        self.assertIsNone(res)

