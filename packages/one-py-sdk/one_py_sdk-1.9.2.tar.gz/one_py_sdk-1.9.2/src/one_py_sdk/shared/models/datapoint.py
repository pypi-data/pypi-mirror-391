import datetime
from uuid import uuid4

class DataPoint:
    def __init__(self, stringValue: str, columnId, note: str ="", auditUserId:uuid4 ="", auditTimeStamp: datetime ="", isLocked: bool =False):
        self.stringValue = stringValue
        self.columnId = columnId
        self.note = note
        self.auditUserId = auditUserId
        self.auditTimeStamp = auditTimeStamp
        self.isLocked =isLocked
    def __repr__(self) -> str:
        return f"String value: {self.stringValue}, Column Id: {self.columnId},\
    Note: {self.note}, Audit UserId: {self.auditUserId}, Audit time: {self.auditTimeStamp}, IsLocked: {self.isLocked}"
        
