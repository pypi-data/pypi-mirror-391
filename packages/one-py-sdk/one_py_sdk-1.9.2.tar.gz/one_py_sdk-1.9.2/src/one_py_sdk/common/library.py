import requests
import json
from logging import Logger
from one_py_sdk.enterprise.authentication import AuthenticationApi
from one_py_sdk.shared.helpers.protobufhelper import DeserializeResponse


class LibraryApi:
    def __init__(self, env, auth: AuthenticationApi, session: requests.Session = None):
        self.AppUrl = "/common/library/v1/"
        self.Environment = env
        self.Authentication = auth
        if not session:
            self.Session = requests.Session()
            self.Session.headers = {"Content-Type": "application/x-protobuf", "Accept": "application/x-protobuf"}            
        else:
            self.Session = session

    def GetUnits(self):
        url = self.Environment+self.AppUrl+"unit"      
        response = DeserializeResponse(self.Session.get(url))
        if response.errors:
            return response
        return response.content.units.items

    def getParameter(self, parameterId):
        pass

    def GetParameters(self):
        url = self.Environment+self.AppUrl+"parameter"       
        r = self.Session.get(url)
        response = DeserializeResponse(r)
        if response.errors:
            return response
        return response.content.parameters.items

    def GetQuantityTypes(self):
        url = self.Environment+self.AppUrl+"quantityType"        
        response = DeserializeResponse(self.Session.get(url))
        if response.errors:
            return response
        return response.content.quantityTypes.items

    def Geti18nKeys(self,  modules: str, language: str = "en",):
        url = self.Environment+self.AppUrl+"i18n"
        if (language and modules):
            url = url+"?modulecsv="+modules+"&lang="+language
        elif (modules):
            url = url+"?modulecsv="+modules
        else:
            return print("Modules is a required parameter")
        headers = {'Authorization': self.Authentication.Token.access_token,
                   "Accept": "application/json"}
        response = requests.get(url, headers=headers)
        jResponse = json.loads(response.content)
        return jResponse.get("FM")
