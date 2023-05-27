from datetime import date
import json
import os
from typing import Literal, Optional
from uuid import uuid4
from fastapi import Depends, FastAPI, HTTPException
from starlette.status import HTTP_201_CREATED
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from fastapi.testclient import TestClient

import gspread

# from mangum import Mangum

def google_sheets_auth(from_dict = False):
    if from_dict:
        credentials = {
            ...
        }
        return gspread.service_account_from_dict(credentials) # type: ignore
    return gspread.service_account(filename='./config/service_account.json')

class BudgetMunger:
    def __init__(self) -> None:
        self.gc = google_sheets_auth()
        self.spreadsheet_name = 'Family Budget'
        self.summary_sheet = 'bean-counter-summary'
        self.sh = self.gc.open(self.spreadsheet_name)


    def process_incoming(self):
        """Process the incoming data from monthly worksheets"""
        ...

        # collect all sheet names with title in format: '01/19'
        # sheets = [ws.title for ws in self.sh.worksheets() if ws.title[0].isdigit()]
        
        # self.ws = self.sh.worksheet(self.summary_sheet)
        # self.ws.update_cell(1, 2, 'Bingo!')

munger = BudgetMunger()

class Heading(BaseModel):
    sheet_name: str             # '01/19'
    type: str                   # 'Outgoing'
    cell_heading: str           # 'Outgoings'
    heading_column: int         # 0
    heading_row: int            # 0
    values_range: str           # 'A5:A7'

class SummaryRow(BaseModel):
    _id: str
    direction: str
    name: str
    category: str
    dt: date
    val: float

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
    "/process/incoming",
    status_code=HTTP_201_CREATED,
    dependencies=[Depends(create_summary_gsheet_if_not_exists)],
)
async def process_incoming():
    """Endpoint to connect to GSheet to write to master csv with all inf lows"""
    munger.process_incoming()
    return {"status": "success"}
