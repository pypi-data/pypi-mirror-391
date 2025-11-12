from collections import OrderedDict
from datetime import datetime
import uuid
from requests import Session
from one_py_sdk.enterprise.authentication import AuthenticationApi
from one_py_sdk.shared.helpers.protobufhelper import DeserializeResponse
from one_py_sdk.shared.helpers.datetimehelper import *
from one_py_sdk.shared.helpers.helpers import IsValidGuid
from one_py_sdk.shared.models.datapoint import DataPoint
from one_interfaces import row_pb2 as row
from one_interfaces import cell_pb2 as cell
from one_interfaces import celldata_pb2 as celldata
from one_interfaces import auditevent_pb2 as audit
from one_interfaces import note_pb2 as note


class SpreadsheetApi:
    def __init__(self, env: str, auth: AuthenticationApi, session: Session = None):
        self.Environment = env
        self.Auth = auth
        self.AppUrl = "/operations/spreadsheet/v1/"
        if not session:
            self.Session = Session()
            self.Session.headers = {
                "Content-Type": "application/x-protobuf", "Accept": "application/x-protobuf"}
        else:
            self.Session = session

    def ImportDictionary(self, plantId, valueDict, wsType):
        rows = self.__rowBuilder(valueDict, wsType, plantId)
        return self.SaveRows(plantId, wsType, rows)

    def SaveRows(self, plantId, wsType, rows):
        url = f"{self.Environment}{self.AppUrl}{plantId}/worksheet/{str(wsType)}/rows"
        response = DeserializeResponse(self.Session.post(
            url, data=rows.SerializeToString()))
        return response

    def __rowBuilder(self, valueDict, wsType, plantId):
        r = row.Rows()
        spreadsheetDef = self.GetSpreadsheetDefinition(plantId)
        sortedValueDict = OrderedDict(valueDict.items())
        map = self.MapColumnGuidToIntId(plantId, wsType)
        rowNumbers = []
        for key in valueDict.keys():
            rowNumber = GetRowNumber(key, wsType)
            utcTime = AssumePlantTimeConvertToUtc(key, spreadsheetDef[0].enumTimeZone)            
            for dataPoint in sortedValueDict[key]:
                cd = celldata.CellData()
                c = cell.Cell()
                if IsValidGuid(dataPoint.columnId):
                    c.columnNumber = map[dataPoint.columnId]
                else:
                    c.columnNumber = dataPoint.columnId
                try:
                    if dataPoint.note != "":
                        n = note.Note()
                        n.text = dataPoint.note
                        if dataPoint.auditUserId != "":
                            n.userId = dataPoint.auditUserId
                        else:
                            n.userId = self.Auth.User.id
                        if dataPoint.auditTimeStamp != "":
                            n.timeStamp.jsonDateTime.value = ToJsonTicksDateTime(
                                AssumePlantTimeConvertToUtc(dataPoint.auditTimeStamp, spreadsheetDef[0].enumTimeZone)).jsonDateTime.value
                        else:
                            n.timeStamp.jsonDateTime.value = ToJsonTicksDateTime(
                                utcTime).jsonDateTime.value
                        c.notes.append(n)
                except:
                    pass
                s = audit.AuditEvent()
                s.id = str(uuid.uuid4())
                if dataPoint.auditUserId != "":
                    s.userId = dataPoint.auditUserId
                    cd.dataSourceBinding.bindingId = dataPoint.auditUserId
                else:
                    s.userId = self.Auth.User.id
                    cd.dataSourceBinding.bindingId = self.Auth.User.id
                if dataPoint.auditTimeStamp != "":
                    s.timeStamp.jsonDateTime.value = ToJsonTicksDateTime(
                        AssumePlantTimeConvertToUtc(dataPoint.auditTimeStamp, spreadsheetDef[0].enumTimeZone)).jsonDateTime.value
                else:
                    s.timeStamp.jsonDateTime.value = ToJsonTicksDateTime(
                        utcTime).jsonDateTime.value
                s.details = "Python SDK import"
                s.enumDataSource = 5
                s.enumDomainSource = 2
                cd.isLocked = dataPoint.isLocked
                cd.auditEvents.append(s)
                cd.stringValue.value = dataPoint.stringValue
                cd.dataSourceBinding.dataSource = 5
                cd.dataSourceBinding.enumSamplingStatistic = 0
                if rowNumber not in rowNumbers:
                    rowNumbers.append(rowNumber)
                    r2 = row.Row()
                    r2.rowNumber = rowNumber
                    c.cellDatas.append(cd)
                    r2.cells.append(c)
                    r.items[r2.rowNumber].CopyFrom(r2)
                else:
                    itemAdded = False
                    r2 = r.items[rowNumber]
                    for item in r2.cells:
                        if item.columnNumber == c.columnNumber:
                            item.cellDatas.insert(0, cd)
                            itemAdded = True
                    if not itemAdded:
                        c.cellDatas.append(cd)
                        r2.cells.append(c)
        return r

    def GetWorksheetColumnIds(self, plantId, wsType):
        url = self.Environment + self.AppUrl + plantId + \
            "/worksheet/"+str(wsType)+"/definition"
        response = DeserializeResponse(self.Session.get(url))
        if response.errors:
            return response
        columnIds = [
            col.columnId for col in response.content.worksheetDefinitions.items[0].columns if col.isActive == True]
        return columnIds

    def MapColumnGuidToIntId(self, plantId, wsType):
        url = self.Environment + self.AppUrl + plantId + \
            "/worksheet/"+str(wsType)+"/definition"
        response = DeserializeResponse(self.Session.get(url))
        if response.errors:
            return response
        guidToIntMap = {}
        for col in response.content.worksheetDefinitions.items[0].columns:
            guidToIntMap[col.columnId] = col.columnNumber
        return guidToIntMap

    def GetWorksheetColumnNumbers(self, plantId, wsType):
        url = self.Environment + self.AppUrl + plantId + \
            "/worksheet/"+str(wsType)+"/definition"
        response = DeserializeResponse(self.Session.get(url))
        if response.errors:
            return response
        columnNumbers = [
            col.columnNumber for col in response.content.worksheetDefinitions.items[0].columns if col.isActive == True]
        return columnNumbers

    def GetWorksheetDefinition(self, plantId, wsType):
        url = self.Environment + self.AppUrl + plantId + \
            "/worksheet/"+str(wsType)+"/definition"
        response = DeserializeResponse(self.Session.get(url))
        if response.errors:
            return response
        return response.content.worksheetDefinitions.items

    def GetSpreadsheetDefinition(self, plantId):
        url = f'{self.Environment}{self.AppUrl}{plantId}/definition'
        response = DeserializeResponse(self.Session.get(url))
        if response.errors:
            return response
        return response.content.spreadsheetDefinitions.items

    def GetColumnByDay(self, plantId, wsType, columnId, date: datetime):
        url = self.Environment + self.AppUrl + plantId + \
            f'/worksheet/{str(wsType)}/column/{columnId}/byday/{date.year}/{date.month}/{date.day}'
        response = DeserializeResponse(self.Session.get(url))
        if response.errors:
            return response
        return response.content.measurements.items

    def GetColumnByMonth(self, plantId: str, wsType: int, columnId: int, date: datetime):
        url = self.Environment + self.AppUrl + plantId + \
            f'/worksheet/{str(wsType)}/column/{columnId}/bymonth/{date.year}/{date.month}'
        response = DeserializeResponse(self.Session.get(url))
        if response.errors:
            return response
        return response.content.measurements.items

    def GetColumnByYear(self, plantId, wsType, columnId, date: datetime):
        url = self.Environment + self.AppUrl + plantId + \
            f'/worksheet/{str(wsType)}/column/{columnId}/byyear/{date.year}'
        response = DeserializeResponse(self.Session.get(url))
        if response.errors:
            return response
        return response.content.measurements.items

    def GetRows(self, plantId, wsType, startRow=None, endRow=None, columns=None, viewId=None):
        if columns and viewId:
            return print("Using both columns and viewId parameters together is not supported.")
        requestId = uuid.uuid4()
        url = f'{self.Environment}{self.AppUrl}{plantId}/worksheet/{str(wsType)}/rows?requestId={requestId}'
        if startRow:
            url = url+f'&startRow={startRow}'
        if endRow:
            url = url+f'&endRow={endRow}'
        if columns:
            url = url+f'&columns={columns}'
        if viewId:
            url = url+f'&viewId={viewId}'

        response = DeserializeResponse(self.Session.get(url))
        if response.errors:
            return response
        return response.content.rows.items

    def __getRows(self, plantId, wsType, startRow=None, endRow=None, columns=None, viewId=None):
        if columns and viewId:
            return print("Using both columns and viewId parameters together is not supported.")
        requestId = uuid.uuid4()
        url = f'{self.Environment}{self.AppUrl}{plantId}/worksheet/{str(wsType)}/rows?requestId={requestId}'
        if startRow:
            url = url+f'&startRow={startRow}'
        if endRow:
            url = url+f'&endRow={endRow}'
        if columns:
            url = url+f'&columns={columns}'
        if viewId:
            url = url+f'&viewId={viewId}'

        response = DeserializeResponse(self.Session.get(url))
        if response.errors:
            return response
        return response.content.rows

    def GetRowsByDay(self, plantId, wsType, date: datetime, columns=None, viewId=None):
        if columns and viewId:
            return print("Using both columns and viewId parameters together is not supported.")
        url = self.Environment + self.AppUrl + \
            f'{plantId}/worksheet/{str(wsType)}/rows/byday/{date.year}/{date.month}/{date.day}'
        response = DeserializeResponse(self.Session.get(url))
        if response.errors:
            return response
        return response.content.rows.items

    def GetRowsByMonth(self, plantId, wsType, date: datetime, columns=None, viewId=None):
        if columns and viewId:
            return print("Using both columns and viewId parameters together is not supported.")
        url = self.Environment + self.AppUrl + \
            f'{plantId}/worksheet/{str(wsType)}/rows/bymonth/{date.year}/{date.month}'
        response = DeserializeResponse(self.Session.get(url))
        if response.errors:
            return response
        return response.content.rows.items

    def GetRowsForTimeRange(self, plantId, wsType, startDate: datetime, endDate: datetime):
        startRow = GetRowNumber(startDate, wsType)
        endRow = GetRowNumber(endDate, wsType)
        rows = row.Rows()
        while endRow - startRow > 5000:
            newEndRow = startRow+5000
            rows.MergeFrom(self.__getRows(
                plantId, wsType, startRow, newEndRow))
            startRow = newEndRow+1
        rows.MergeFrom(self.__getRows(plantId, wsType, startRow, endRow))
        return rows.items
