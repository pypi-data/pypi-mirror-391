import requests
import json
from logging import Logger
from one_py_sdk.shared.helpers.protobufhelper import DeserializeResponse


class ConfigurationApi:
    def __init__(self, env, auth, session: requests.Session=None):
        self.AppUrl = "/common/configuration/v2/"
        self.Environment = env
        self.Authentication = auth
        if not session:
            self.Session = requests.Session()
            self.Session.headers = {"Content-Type": "application/x-protobuf", "Accept": "application/x-protobuf"}            
        else:
            self.Session = session

    def GetSpreadsheetViews(self, authTwinId, configurationTypeId='bedc5ff2-bc8e-4916-9560-ccc28701d792'):
        url = f'{self.Environment}{self.AppUrl}?authTwinRefId={authTwinId}&configurationTypeId={configurationTypeId}'        
        response = DeserializeResponse(self.Session.get(url))
        if response.errors:
            return response
        return response.content.configurations.items
