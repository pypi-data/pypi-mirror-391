from datetime import datetime, timedelta
import unittest
import csv
import sys
from one_py_sdk.clientsdk import ClientSdk
from one_py_sdk.shared.constants import Environment as env
from one_py_sdk.shared.models.datapoint import DataPoint
from testConstants import *
from one_py_sdk.shared.constants import *
client = ClientSdk(env.get('stage'))
startDate = datetime.now()-timedelta(days=7)
endDate = datetime.now()
twinTypeId = ""
twinSubTypeId = ""


class TestAuthenticationApi(unittest.TestCase):
    def test_getToken(self):
        tokenResponse = client.Authentication.GetToken(userName, password)
        self.assertIsNotNone(tokenResponse)
        self.assertTrue("Bearer" in tokenResponse)
        client.Authentication.LoginResourceOwner(userName, password)


class TestSpreadsheetAPI(unittest.TestCase):
    def test_GetWorksheetColumnIds(self):
        idResponse = client.Spreadsheet.GetWorksheetColumnIds(readPlantId, 4)
        self.assertIsNotNone(idResponse)

    def test_GetRowsForTimeRange(self):
        rowsForTimeRangeResponse = client.Spreadsheet.GetRowsForTimeRange(
            readPlantId, 4, startDate, endDate)
        self.assertIsNotNone(rowsForTimeRangeResponse)
        countOfNotes =0
        for k in rowsForTimeRangeResponse:
            self.assertIsNotNone(
                rowsForTimeRangeResponse[k].cells[0].cellDatas[0].value.value)
            if rowsForTimeRangeResponse[k].cells[0].notes is not None:
                countOfNotes+=1
        self.assertGreaterEqual(countOfNotes, 1)

    def test_GetWorksheetDefinition(self):
        wsDefResponse = client.Spreadsheet.GetWorksheetDefinition(
            readPlantId, 4)
        self.assertIsNotNone(wsDefResponse)
        self.assertGreaterEqual(len(wsDefResponse[0].columns), 10)

    def test_ImportDictionary(self):
        dates1d = [startDate + timedelta(days=1*i) for i in range(7)]
        colIds = client.Spreadsheet.GetWorksheetColumnIds(plantId, 4)
        data1d = [DataPoint(
            "1", colId, f"noted {colId}", client.Authentication.User.id) for colId in colIds]
        dailyDict = {}
        for date in dates1d:
            dailyDict[date] = data1d
        importResponse = client.Spreadsheet.ImportDictionary(
            writePlantId, dailyDict, 4)
        self.assertIsNotNone(importResponse)


class TestExporter(unittest.TestCase):
    def test_ExportLimitColumns(self):
        allLimits = "LimitColumnInfoAllLimitsTest.csv"
        # Only exports columns with regulatory limits unless the final parameter is set to true (it defaults to false) then it will export all columns with limits
        client.Exporter.ExportLimitColumns(allLimits, plantId, 4, "", True)

        with open(allLimits) as file:
            csvreader = csv.reader(file)
            next(csvreader)  # Read the header row
            count = 0
            for row in csvreader:
                count += 1
        self.assertGreaterEqual(count, 2)

    def test_ExportRegulatoryLimits(self):
        regLimits = "LimitColumnInfoRegulatoryLimitsTest.csv"
        # Only exports columns with regulatory limits unless the final parameter is set to true (it defaults to false) then it will export all columns with limits
        client.Exporter.ExportLimitColumns(regLimits, plantId, 4, "")
        with open(regLimits) as file:
            csvreader = csv.reader(file)
            next(csvreader)  # Read the header row
            count = 0
            for row in csvreader:
                count += 1
        self.assertGreaterEqual(count, 1)

    def test_ExportWorksheet(self):
        allWs = "AllWsExport.csv"
        client.Exporter.ExportWorksheet(allWs, plantId, startDate, endDate)
        with open(allWs, 'r') as file:
            csvreader = csv.reader(file)
            next(csvreader)  # Read the header row
            count = 0
            for row in csvreader:
                count += 1
        self.assertGreaterEqual(count, 70)

    def test_ExportColumnDetails(self):
        columnInfoDaily = "ColumnInfoDaily.csv"
        client.Exporter.ExportColumnDetails(columnInfoDaily, plantId, 4)
        with open(columnInfoDaily, 'r') as file:
            csvreader = csv.reader(file)
            next(csvreader)  # Read the header row
            count = 0
            for row in csvreader:
                count += 1
        self.assertGreaterEqual(count, 3)

    def test_ExportLimits(self):
        # Exports limit columns for all worksheet types
        limits = "Limits.csv"
        client.Exporter.ExportLimits(limits, plantId)
        with open(limits, 'r') as file:
            csvreader = csv.reader(file)
            header = next(csvreader)  # Read the header row
            count = 0
            for row in csvreader:
                count += 1
        self.assertGreaterEqual(count, 3)
        dailyLimits = "LimitsDaily.csv"
        client.Exporter.ExportLimits(dailyLimits, plantId, 4)
        count = 0
        with open(dailyLimits, 'r') as file:
            csvreader = csv.reader(file)
            header = next(csvreader)  # Read the header row
            count = 0
            for row in csvreader:
                count += 1
        self.assertGreaterEqual(count, 3)


class TestCoreApi(unittest.TestCase):
    def test_GetUser(self):
        client.Authentication.GetUserInfo()
        user = client.Core.GetUser(client.Authentication.User.id)
        self.assertEqual(user.userName, userName)


class TestTwinApi(unittest.TestCase):
    def test_GetTwinData(self):
        twinDataResponse = client.DigitalTwin.GetTwinData(plantId)
        self.assertIsNotNone(twinDataResponse)

    def test_Get(self):
        plantTwin = client.DigitalTwin.Get(plantId)
        self.assertIsNotNone(plantTwin)
        self.assertEqual(plantTwin[0].twinReferenceId.value, plantId)

    def test_GetDigitalTwinTypes(self):
        twinTypes = client.DigitalTwin.GetDigitalTwinTypes()
        self.assertIsNotNone(twinTypes)
        twinTypeId = twinTypes[0].id

    def test_GetDigitalTwinSubtypes(self):
        twinSubtypesResponse = client.DigitalTwin.GetDigitalTwinSubtypes()
        self.assertIsNotNone(twinSubtypesResponse)
        twinSubTypeId = twinSubtypesResponse[0].id

    def test_GetDescendantsByType(self):
        twinDescendantsByTypeResponse = client.DigitalTwin.GetDescendantsByType(
            plantId, twinTypeId)
        self.assertIsNotNone(twinDescendantsByTypeResponse)

    def test_GetDescendantsBySubType(self):
        twinDescendantsBySubtypeResponse = client.DigitalTwin.GetDescendantsBySubType(
            plantId, twinSubTypeId)
        self.assertIsNotNone(twinDescendantsBySubtypeResponse)

    def test_GetDescendants(self):
        allDescendants = client.DigitalTwin.GetDescendants(plantId)
        self.assertIsNotNone(allDescendants)


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestAuthenticationApi('test_getToken'))
    test_suite.addTests([TestSpreadsheetAPI('test_ImportDictionary'), TestSpreadsheetAPI('test_GetRowsForTimeRange'),
                         TestSpreadsheetAPI('test_GetWorksheetDefinition'), TestSpreadsheetAPI('test_GetWorksheetColumnIds')])
    test_suite.addTests([TestExporter("test_ExportLimitColumns"), TestExporter("test_ExportRegulatoryLimits"),
                         TestExporter("test_ExportWorksheet"), TestExporter(
                             "test_ExportColumnDetails"),
                         TestExporter("test_ExportLimits")])
    test_suite.addTest(TestCoreApi("test_GetUser"))
    test_suite.addTests([TestTwinApi("test_GetTwinData"), TestTwinApi("test_Get"),
                         TestTwinApi("test_GetDigitalTwinTypes"), TestTwinApi(
                             "test_GetDigitalTwinSubtypes"),
                         TestTwinApi("test_GetDescendantsByType"), TestTwinApi(
                             "test_GetDescendantsBySubType"),
                         TestTwinApi("test_GetDescendants")])

    return test_suite


if __name__ == '__main__':
    userName = sys.argv[1]
    password = sys.argv[2]
    runner = unittest.TextTestRunner()
    runner.run(suite())
