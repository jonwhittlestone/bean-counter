import io
import re
from datetime import date, datetime
from enum import Enum
from typing import Literal, Optional
from uuid import uuid4

import gspread
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ValidationError
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from mangum import Mangum

SHEET_URL = "https://docs.google.com/spreadsheets/d/190QeHTRisFY3KwGO3M7wIgrJtvgKg7Dn5Q2a6VC3FWc/edit#gid=1078864678"
HEADINGS = [
    "Incomings",
    "Outgoings",
    "💷 Incomings",
    "💸 Outgoings",
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
    "Total earnings carried over",
]

CATEGORIES = [
    "House",
    "Repayments",
    "Monthly Extras",
    "Car",
    "Offspring",
    "Monthly Extras in Joint account",
]


class RunFilterParams(BaseModel):
    limit: Optional[int]
    test: Optional[int]


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
    items: list[Item] | None


class SheetVersionEnum(str, Enum):
    VERSION_1 = "v1"
    VERSION_2 = "v2"


class Sheet(BaseModel):
    sheet_name: str  # '01/19'
    sheet_version: SheetVersionEnum
    headings: list[Heading]

    @classmethod
    def find_version(cls, raw: list[list[str]]) -> SheetVersionEnum:
        if raw[0] == ["", "", "%", "Actual", "", ""]:
            return SheetVersionEnum.VERSION_1
        else:
            return SheetVersionEnum.VERSION_2


class SummaryRow(BaseModel):
    """Output row destined for output-summary-row sheet"""

    _id: str
    direction: str
    name: str
    category: str
    date: str
    val: float


def google_sheets_auth(from_dict=False):
    if from_dict:
        credentials = {...}
        return gspread.service_account_from_dict(credentials)  # type: ignore
    return gspread.service_account(filename="./config/service_account.json")


def is_title_date(string):
    """Checks if string is mm/yy"""
    pattern = r"^\d{2}/\d{2}$"
    match = re.match(pattern, string)
    if match:
        return True


def de_emojify(input_string):
    regrex_pattern = re.compile(
        pattern="["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+",
        flags=re.UNICODE,
    )
    return regrex_pattern.sub(r"", input_string)


class BudgetMunger:
    def __init__(self, test: bool = False) -> None:
        self.gc = google_sheets_auth()
        self.spreadsheet_name = "Family Budget"
        self.test = test
        self.summary_sheet = "bean-counter-summary"
        self.sh = self.gc.open(self.spreadsheet_name)

    def slurp_contents_of_all_sheets(self, filters: RunFilterParams):
        """Slurp contents of all sheets"""
        sheets = []
        m = 1
        for ws in self.sh.worksheets():
            if is_title_date(ws.title):
                if filters.limit and m > filters.limit:
                    break
                sheets.append(self.get_sheet(ws_name=ws.title))
                m += 1
        return sheets

    def build_flat_summary(self, sheets: list[Sheet]):
        """Traverse sheets and build a flat summary of all items"""
        summary_rows = []
        for s in sheets:
            for h in s.headings:
                for i in h.items:
                    date_obj = datetime.strptime(h.ws_name, "%m/%y")
                    try:
                        summary_rows.append(
                            SummaryRow(
                                _id=str(uuid4()),
                                direction=h.cell_heading,
                                name=i.title,
                                category="",
                                date=date_obj.date().isoformat(),
                                val=i.value,
                            )
                        )
                    except ValidationError as e:
                        ...
        return summary_rows

    def run(self, filters: RunFilterParams):
        try:
            sheets = self.slurp_contents_of_all_sheets(filters=filters)
            summary_rows = self.build_flat_summary(sheets)
            if filters.test:
                return summary_rows
            else:
                self.write_summary(summary_rows)
        except Exception as e:
            raise Exception(e)

    def fetch_sheet(self, ws_name):
        ws = self.sh.worksheet(ws_name)
        return ws.get_all_values()

    def write_row(self, row: SummaryRow):
        d = row.dict()
        ret = d.values()
        return list(ret)

    def write_header(self, data):
        return list(data[0].dict().keys())

    def write_summary(self, data):
        ws = self.sh.worksheet(self.summary_sheet)
        ws.clear()
        rows = [self.write_row(r) for r in data if r.val > 0]
        rows.insert(0, self.write_header(data))
        ws.update("A1:ZZ5", rows)

    def set_headings(self, ws_name: str, raw: list[list[str]]):  # -> list[Heading]:
        headings = []
        for h in HEADINGS:
            for row in raw:
                if h in row:
                    headings.append(
                        Heading(
                            sheet_name=self.spreadsheet_name,
                            ws_name=ws_name,
                            cell_heading=de_emojify(h).strip(),
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
                            try:
                                val = float(raw[i][h.heading_column + 1])
                            except ValueError:
                                val = 0
                            h.items.append(
                                Item(title=raw[i][h.heading_column], value=val)
                            )
                    break
        return headings

    def get_sheet(self, ws_name: str) -> Sheet:
        """Scan a sheet for headings and return a list of Heading objects"""

        raw = self.fetch_sheet(ws_name=ws_name)
        headings = self.set_headings(ws_name=ws_name, raw=raw)
        self.set_items(headings=headings, raw=raw)

        return Sheet(
            sheet_name=self.spreadsheet_name,
            sheet_version=Sheet.find_version(raw=raw),
            headings=headings,
        )


munger = BudgetMunger()


app = FastAPI()
handler = Mangum(app)


@app.get("/")
async def root(request: Request):
    return {"welcome": f"{request.base_url}run"}


def create_summary_gsheet_if_not_exists():
    """Create the inflows gsheet if it doesn't exist"""
    try:
        gc = google_sheets_auth()
        sh = gc.open(munger.spreadsheet_name)
        if munger.summary_sheet not in [ws.title for ws in sh.worksheets()]:
            sh.add_worksheet(index=0, title=munger.summary_sheet, rows=100, cols=20)
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid auth to GSheet")


@app.get(
    "/run",
    status_code=HTTP_201_CREATED,
    dependencies=[Depends(create_summary_gsheet_if_not_exists)],
)
async def run(limit: int = Query(None), test: bool = Query(False)):
    """Endpoint to connect to GSheet to write to master csv with all items"""

    filters = RunFilterParams(limit=limit, test=test)

    try:
        munger.run(filters)
        return {
            "datetime": datetime.now().isoformat(),
            "status": "success",
            "sheet-url": SHEET_URL,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/summary",
    status_code=HTTP_200_OK,
    dependencies=[Depends(create_summary_gsheet_if_not_exists)],
)
async def summary():
    """Endpoint to connect to GSheet to download summary sheet"""

    from gspread_dataframe import get_as_dataframe, set_with_dataframe

    ws = munger.sh.worksheet(munger.summary_sheet)
    df = get_as_dataframe(ws)
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=summary.csv"
    return response
