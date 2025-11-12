from datetime import datetime
import requests
import json
from one_py_sdk.enterprise.authentication import AuthenticationApi
from one_py_sdk.shared.helpers.protobufhelper import DeserializeResponse


class HistorianApi:
    def __init__(self, env, auth: AuthenticationApi, session: requests.Session=None):
        self.Environment = env
        self.Authentication = auth
        self.AppUrl = "/historian/data/v1/"
        if not session:
            self.Session = requests.Session()
            self.Session.headers = {"Content-Type": "application/x-protobuf", "Accept": "application/x-protobuf"}            
        else:
            self.Session = session

    def GetHistorianData(self, twinRefId, date: datetime):
        date = f'{str(date.date())}T{str(date.time())}Z'
        url = f'{self.Environment}{self.AppUrl}{twinRefId}/{date}'
        response = DeserializeResponse(self.Session.get(url))
        if response.errors:
            return response
        return response.content.historianDatas.items

    def GetHistorianDataRange(self, twinRefId, startTime: datetime, endTime: datetime):
        startString = f'{str(startTime.date())}T{str(startTime.time())}'
        endString = f'{str(endTime.date())}T{str(endTime.time())}'
        url = f'{self.Environment}{self.AppUrl}{twinRefId}?startTime={startString}&endTime={endString}'
        response = DeserializeResponse(self.Session.get(url))
        if response.errors:
            return response
        return response.content.historianDatas.items
