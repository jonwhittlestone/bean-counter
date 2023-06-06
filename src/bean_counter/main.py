from datetime import date
import json
import os
from enum import Enum
from typing import Literal, Optional
from uuid import uuid4
from fastapi import Depends, FastAPI, HTTPException
from starlette.status import HTTP_201_CREATED
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

import gspread
from gspread import Cell

# from mangum import Mangum

HEADINGS = [
    "Incomings",
    "Outgoings",
    # "Savings",
    # "Investments",
    # "Net Worth"
]

SUB_HEADINGS = [
    "Total Incomings",
    "Total Outgoings",
    "Balance",
    "Weekly",
    "Weekly Each",
]

CATEGORIES = ["House", "Repayments", "Monthly Extras"]


class Item(BaseModel):
    title: str
    value: float


class Heading(BaseModel):
    sheet_name: str  # 'Family Budget'
    ws_name: str  # '01/19'
    type: str | None  # 'Outgoing'

    cell_heading: str  # 'Outgoings'
    heading_column: int  # 0
    heading_row: int  # 0
    # item_range: str  # 'A5:A7'
    items: list[Item] | None


class SheetVersionEnum(str, Enum):
    VERSION_1 = "v1"


class Sheet(BaseModel):
    sheet_name: str  # '01/19'
    sheet_version: SheetVersionEnum
    raw: list[list[str]]
    # headings: list[Heading]


class SummaryRow(BaseModel):
    """Output row destined for output-summary-row sheet"""

    _id: str
    direction: str
    name: str
    category: str
    dt: date
    val: float


def google_sheets_auth(from_dict=False):
    if from_dict:
        credentials = {...}
        return gspread.service_account_from_dict(credentials)  # type: ignore
    return gspread.service_account(filename="./config/service_account.json")


class BudgetMunger:
    def __init__(self, test: bool = False) -> None:
        self.gc = google_sheets_auth()
        self.spreadsheet_name = "Family Budget"
        self.test = test
        self.summary_sheet = "bean-counter-summary"
        self.sh = self.gc.open(self.spreadsheet_name)

    def fetch_sheet(self, ws_name):
        ws = self.sh.worksheet(ws_name)
        return ws.get_all_values()

    def write_summary(self, data):
        ws = self.sh.worksheet(self.summary_sheet)
        ws.update("A1:B8", data)

    def set_headings(self, ws_name: str, raw: list[list[str]]):  # -> list[Heading]:
        headings = []
        for h in HEADINGS:
            for row in raw:
                if h in row:
                    headings.append(
                        Heading(
                            sheet_name=self.spreadsheet_name,
                            ws_name=ws_name,
                            cell_heading=h,
                            heading_column=row.index(h),
                            heading_row=raw.index(row),
                        )
                    )  # type: ignore
            ...
        return headings

    def is_item_worthy(self, val: str) -> bool:
        """Is item worthy of capturing as an Item?"""
        if val == "":
            return False
        if val in SUB_HEADINGS:
            return False
        if val in CATEGORIES:
            return False
        return True

    def set_items(self, headings: list[Heading], raw: list[list[str]]):
        for h in headings:
            ...
            for row in raw:
                if h.cell_heading in row[h.heading_column]:
                    # Now we can loop through the rows below the heading until we reach another heading
                    for i in range(h.heading_row + 1, len(raw)):
                        if self.is_item_worthy(raw[i][0]):
                            if str(raw[i][0]) in HEADINGS:
                                break
                            if h.items is None:
                                h.items = []
                            h.items.append(
                                Item(
                                    title=raw[i][h.heading_column],
                                    value=0
                                    if raw[i][h.heading_column + 1] == ""
                                    else float(raw[i][h.heading_column + 1]),
                                )
                            )
                    break
        return headings

    def get_sheet(self, ws_name: str) -> Sheet:
        """Scan a sheet for headings and return a list of Heading objects"""

        ws_name = "01/19"
        raw = self.fetch_sheet(ws_name=ws_name)
        headings = self.set_headings(ws_name=ws_name, raw=raw)
        self.set_items(headings=headings, raw=raw)

        return Sheet(
            sheet_name=self.spreadsheet_name,
            sheet_version=SheetVersionEnum.VERSION_1,
            raw=raw,
        )


munger = BudgetMunger()


app = FastAPI()
# handler = Mangum(app)


@app.get("/")
async def root():
    return {"message": "Welcome to bean-counter!"}


def create_summary_gsheet_if_not_exists():
    """Create the inflows gsheet if it doesn't exist"""
    try:
        gc = google_sheets_auth()
        sh = gc.open(munger.spreadsheet_name)
        if munger.summary_sheet not in [ws.title for ws in sh.worksheets()]:
            sh.add_worksheet(index=0, title=munger.summary_sheet, rows=100, cols=20)
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid auth to GSheet")


@app.post(
    "/run",
    status_code=HTTP_201_CREATED,
    dependencies=[Depends(create_summary_gsheet_if_not_exists)],
)
async def run():
    """Endpoint to connect to GSheet to write to master csv with all inf lows"""
    return {"status": "success"}
