import json
import os
from typing import Literal, Optional
from uuid import uuid4
from fastapi import Depends, FastAPI, HTTPException
from starlette.status import HTTP_201_CREATED
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
# from mangum import Mangum


# class Book(BaseModel):
#     name: str
#     genre: Literal["fiction", "non-fiction"]
#     price: float
#     book_id: Optional[str] = uuid4().hex

app = FastAPI()
# handler = Mangum(app)


@app.get("/")
async def root():
    return {"message": "Welcome to bean-counter!"}

def create_inflows_gsheet_if_not_exists():
    """Create the inflows gsheet if it doesn't exist"""
    api_cx = False
    if api_cx:
        return True
    raise HTTPException(status_code=403, 
                        detail="Invalid auth to GSheet")

@app.post(
        "/process/inflow",
        status_code=HTTP_201_CREATED,
        dependencies=[Depends(create_inflows_gsheet_if_not_exists)],
)
async def process_inflow():
    """Endpoint to connect to GSheet to write to master csv with all inf lows"""

    return {"status": "success"}

