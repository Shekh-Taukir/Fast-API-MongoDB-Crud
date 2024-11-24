from datetime import date
from pydantic import BaseModel


class Notes(BaseModel):
    note_title: str
    note_desc: str
    writer_fname: str
    writer_lname: str
