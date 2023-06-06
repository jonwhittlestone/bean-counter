import pytest
import csv

from src.bean_counter.main import BudgetMunger

MOCKED_FILE = "./tests/version_1.csv"
VERSION_1_SHEET = "01/19"


@pytest.fixture
def mocked_sheet_v1() -> list[list[str]]:
    with open(MOCKED_FILE, "w+") as file:
        csv_reader = csv.reader(file)
        res = []
        # Iterate over each row in the CSV file
        for row in csv_reader:
            res.append(row)
        if res == []:
            munger = BudgetMunger(test=False)
            res = munger.fetch_sheet(ws_name=VERSION_1_SHEET)
            with open(MOCKED_FILE, "w+") as my_csv:
                csv_writer = csv.writer(my_csv, delimiter=",")
                csv_writer.writerows(res)
                return res

        return res
