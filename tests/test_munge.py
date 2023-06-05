import pytest
from httpx import AsyncClient

from src.bean_counter.main import app

from fastapi.testclient import TestClient
from src.bean_counter.main import BudgetMunger, Sheet, Heading, HEADINGS

client = TestClient(app)


def test_process_incoming():
    response = client.post("/process/incoming")
    assert response.status_code == 201


def test_parse_sheet_model():
    munger = BudgetMunger(test=True)
    res = munger.get_sheet(ws_name="01/19")
    assert type(res) == Sheet


def _test_scan_for_headings():
    munger = BudgetMunger(test=False)
    res = munger.scan_for_headings(ws_name="01/19")
    assert res == "A4:B11"

def test_get_headings_items_version_1():
    munger = BudgetMunger(test=False)
    version_1_sheet = '01/19'
    MOCKED_FILE = "./tests/version_1.csv"

    import csv
    # TO SAVE WS TO MOCKED FILE ----------------------
    # res = munger.fetch_sheet(ws_name=version_1_sheet)
    # with open(MOCKED_FILE, "w+") as my_csv:
    #     csv_writer = csv.writer(my_csv,delimiter=',')
    #     csv_writer.writerows(res)
    # /TO SAVE WS TO MOCKED FILE ----------------------
    ...

    # TO READ WS TO MOCKED FILE ----------------------

    with open(MOCKED_FILE, 'r') as file:
        csv_reader = csv.reader(file)
        res = []
        # Iterate over each row in the CSV file
        for row in csv_reader:
            res.append(row)
    # /TO READ WS TO MOCKED FILE ----------------------

    headings = munger.set_headings(ws_name=version_1_sheet, raw=res)
    assert headings[0].cell_heading == HEADINGS[0]

def test_write_summary():

    munger = BudgetMunger(test=False)
    munger.write_summary([
        [1, 2], 
        [3, 4],
        [5, 6],
    ])
    ...
