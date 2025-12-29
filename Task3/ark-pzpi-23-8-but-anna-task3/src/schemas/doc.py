from pydantic import BaseModel
from datetime import date, datetime, time
from typing import List, Optional


class WasteTransferActDTO(BaseModel):
    city: str
    act_date: date

    sender_name: str
    sender_edrpou: str
    sender_address: str
    sender_phone: str

    receiver_name: str
    receiver_edrpou: str
    receiver_address: str
    receiver_phone: str

    transfer_datetime: datetime
    waste_description: str
