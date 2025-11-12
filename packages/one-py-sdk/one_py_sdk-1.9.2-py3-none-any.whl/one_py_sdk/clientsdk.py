from imp import cache_from_source
from requests import Session
from datetime import time
import json
import requests_cache
from one_py_sdk.enterprise.core import CoreApi
from one_py_sdk.historian.data import HistorianApi
from one_py_sdk.operations.spreadsheet import SpreadsheetApi
from one_py_sdk.common.library import LibraryApi
from one_py_sdk.enterprise.twin import DigitalTwinApi
from one_py_sdk.enterprise.report import ReportApi
from one_py_sdk.common.configuration import ConfigurationApi
from one_py_sdk.shared.constants import *
from one_py_sdk.enterprise.authentication import AuthenticationApi
from one_py_sdk.shared.helpers.csvhelper import Exporter


class ClientSdk:
    def __init__(self, env="https://api-us.aquaticinformatics.net/", cacheTimeout: int = None):
        self.Environment = env
        self.Initialize(cacheTimeout)
    

    def Initialize(self, cacheTimeout: int):
        self.Session = Session()         
        self.Session.headers = {"Content-Type": "application/x-protobuf", "Accept": "application/x-protobuf"}            
        self.Authentication = AuthenticationApi(self.Environment, self.Session)
        self.DigitalTwin = DigitalTwinApi(
            self.Environment, self.Authentication, self.Session)
        self.Spreadsheet = SpreadsheetApi(
            self.Environment, self.Authentication, self.Session)
        self.Library = LibraryApi(self.Environment, self.Authentication, self.Session)
        self.Core = CoreApi(self.Environment, self.Authentication, self.Session)
        self.Historian = HistorianApi(self.Environment, self.Authentication, self.Session)
        self.Exporter = Exporter(self.Environment, self.Authentication, self.Session)
        self.Configuration = ConfigurationApi(
            self.Environment, self.Authentication, self.Session)
        self.Report = ReportApi(self.Environment, self.Authentication, self.Session)
        
        if cacheTimeout != None:
            requests_cache.install_cache(
                "client-cache", backend="memory", expire_after=cacheTimeout)

    def LoadCurrentUser(self):
        if not self.Authentication.IsAuthenticated:
            return print("Not authenticated. Authenticate and try again")
        if(self.Authentication.User.id != None):
            self.Authentication.GetUserInfo()
            self.Authentication.User.CopyFrom(
                self.Core.GetUser(self.Authentication.User.id))
