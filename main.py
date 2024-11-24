from fastapi import FastAPI
from pymongo import MongoClient
from models import Notes
from datetime import date

app = FastAPI()

conn = MongoClient("mongodb+srv://dba:dba@cluster0.otf2y.mongodb.net/")
db = conn.new_note


def of_get_printable_data(raw_note):
    dict_note = []

    for note in raw_note:
        dict_note.append(
            {
                "title": note.get("note_title"),
                "description": note.get("note_desc"),
                "author_firstname": note.get("writer_fname"),
                "author_lastname": note.get("writer_lname"),
                "note_entered": note.get("note_entered"),
            }
        )

    return dict_note


@app.get("/")
async def root():
    return {"message": "Good start"}


# API that retrieves all the notes, and sorting is descending as per inserted.
@app.get("/get_all_notes/")
async def of_getAllNotes():

    # checks for the result count, and if its 0, then show msg that no data is present.
    if db.new_note.count_documents({}) == 0:
        return {"Message": "No entries present in DB."}

    # making the sorting so that new rows came at top, -1 indicates order in descending
    notes = db.new_note.find().sort("_id", -1)

    # get the printable data that will be a result set to return
    dict_note = of_get_printable_data(notes)

    return {"result": dict_note, "Total Rows": len(dict_note), "Success": True}


# API that add a note and save it
@app.post("/add_note")
async def of_add_note(note: Notes):
    dict_note = dict(note)
    add_note = {
        "note_title": dict_note.get("note_title"),
        "note_desc": dict_note.get("note_desc"),
        "writer_fname": dict_note.get("writer_fname"),
        "writer_lname": dict_note.get("writer_lname"),
        "note_entered": date.today().isoformat(),
    }
    result = db.new_note.insert_one(add_note)
    return {"Success": "True"}


# API that deletes all the notes
@app.delete("/delete_all_notes")
async def of_delete_notes():
    result = db.new_note.delete_many({})
    return {
        "Success": "True",
        "Message": f"Deleted {result.deleted_count} entries from db.",
    }


# API that returns the data as per title search
@app.get("/get_books_based_on_title")
async def of_get_books_based_on_title(search_title: str):

    # its just like select * from new_note where note_title like '%<search_title>%', and apply the sort so that last entries came at top
    result_note = db.new_note.find(
        {"note_title": {"$regex": f".*{search_title}.*", "$options": "i"}}
    ).sort("_id", -1)

    dict_note = of_get_printable_data(result_note)

    return {"result": dict_note, "Success": True, "Total Rows": len(dict_note)}


# API that updates the specific note
@app.put("/update_note")
async def of_update_note(note_id: str, updated_note: Notes):
    result_note = db.new_note.find({"_id": note_id})
    if len(str(result_note._id)) == 0:
        return {"Message": "Such note entry doesn't exists"}

    result = db.new_note.update_one(
        {"_id": note_id},
        {
            "$set": {
                "note_title": updated_note.note_title,
                "note_desc": updated_note.note_desc,
                "writer_fname": updated_note.writer_fname,
                "writer_lname": updated_note.writer_lname,
            }
        },
    )
    if result.modified_count == 0:
        return {"Success": False, "Message": "No changes made"}

    return {"Success": True, "Message": "Changes have been applied"}
