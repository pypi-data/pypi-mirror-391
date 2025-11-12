import requests
import json
from one_py_sdk.enterprise.authentication import AuthenticationApi
from one_py_sdk.shared.helpers.protobufhelper import DeserializeResponse
from one_interfaces import user_pb2 as User


class CoreApi:
    def __init__(self, env, auth: AuthenticationApi, session: requests.Session =None):
        self.AppUrl = "/enterprise/core/v1/"
        self.Environment = env
        self.Authentication = auth
        if not session:
            self.Session = requests.Session()
            self.Session.headers = {"Content-Type": "application/x-protobuf", "Accept": "application/x-protobuf"}            
        else:
            self.Session = session

    def GetUser(self, userId, expand=None):
        user = User.User()
        if (expand != None):
            url = self.Environment+self.AppUrl+"User/"+userId+"expand="+expand
        else:
            url = self.Environment+self.AppUrl+"User/"+userId
        
        response = DeserializeResponse(self.Session.get(url))
        if response.errors:
            return response
        return response.content.users.items[0]


class UserHelper:
    def GetUserFromUserInfo(userInfo):
        jResponse = json.loads(userInfo.content)
