import pytest
from httpx import AsyncClient

from src.bean_counter.main import SheetVersionEnum, app
from .conftest import VERSION_1_SHEET, VERSION_2_SHEET

from fastapi.testclient import TestClient
from src.bean_counter.main import BudgetMunger, Sheet, Heading, HEADINGS

client = TestClient(app)


def test_run():
    response = client.get("/run?limit=2")
    assert response.status_code == 201


def test_parse_sheet_model():
    munger = BudgetMunger(test=True)
    res = munger.get_sheet(ws_name="01/19")
    assert type(res) == Sheet


def test_set_headings_version_1(mocked_sheet_v1: list[list[str]]):
    munger = BudgetMunger(test=True)

    headings = munger.set_headings(ws_name=VERSION_1_SHEET, raw=mocked_sheet_v1)
    assert headings[0].cell_heading == HEADINGS[0]


def test_set_headings_version_2(mocked_sheet_v2: list[list[str]]):
    munger = BudgetMunger(test=True)

    headings = munger.set_headings(ws_name=VERSION_2_SHEET, raw=mocked_sheet_v2)
    assert headings[0].cell_heading == "💷 Incomings"
    assert headings[1].cell_heading == "💸 Outgoings"


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


def test_set_items_version_2(mocked_sheet_v2: list[list[str]]):
    munger = BudgetMunger(test=True)
    headings_with_items = munger.set_items(
        headings=munger.set_headings(ws_name=VERSION_1_SHEET, raw=mocked_sheet_v2),
        raw=mocked_sheet_v2,
    )
    _h = headings_with_items
    incoming_items = getattr(_h[0], "items")
    outgoing_items = getattr(_h[1], "items")
    assert len(incoming_items) == 5
    assert len(outgoing_items) == 26


def test_find_sheet_version(
    mocked_sheet_v1: list[list[str]], mocked_sheet_v2: list[list[str]]
):
    ...
    version1 = Sheet.find_version(raw=mocked_sheet_v1)
    assert version1 == SheetVersionEnum.VERSION_1

    version2 = Sheet.find_version(raw=mocked_sheet_v2)
    assert version2 == SheetVersionEnum.VERSION_2


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
