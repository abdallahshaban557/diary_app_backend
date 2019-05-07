from datetime

class diary_entry:
    id = ""
    title = ""
    body = ""
    entryDate = datetime.datetime.now()
    updateTS = datetime.datetime.now()

    def __init__(self, id, title, body, entryDate, updateTS): 
        self.id = id
        self.title = title
        self.body = body
        self.entryDate = entryDate
        self.updateTS = updateTS