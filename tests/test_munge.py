import pytest
from httpx import AsyncClient

from src.bean_counter.main import app
from .conftest import VERSION_1_SHEET

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


def test_set_headings_version_1():
    munger = BudgetMunger(test=False)
    version_1_sheet = "01/19"
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

    with open(MOCKED_FILE, "r") as file:
        csv_reader = csv.reader(file)
        res = []
        # Iterate over each row in the CSV file
        for row in csv_reader:
            res.append(row)
    # /TO READ WS TO MOCKED FILE ----------------------

    headings = munger.set_headings(ws_name=version_1_sheet, raw=res)
    assert headings[0].cell_heading == HEADINGS[0]


def test_set_items_version_1(mocked_sheet_v1: list[list[str]]):
    munger = BudgetMunger(test=True)
    headings_with_items = munger.set_items(
        headings=munger.set_headings(ws_name=VERSION_1_SHEET, raw=mocked_sheet_v1),
        raw=mocked_sheet_v1,
    )
    _h = headings_with_items
    incoming_items = getattr(_h[0], "items")
    outgoing_items = getattr(_h[1], "items")
    assert len(incoming_items) == 5
    assert len(outgoing_items) == 16


def test_write_summary():
    munger = BudgetMunger(test=False)
    munger.write_summary(
        [
            [1, 2],
            [3, 4],
            [5, 6],
        ]
    )
    ...
