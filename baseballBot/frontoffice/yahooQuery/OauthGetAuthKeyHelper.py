import os
import json
from yahoo_oauth.utils import get_data, services, CALLBACK_URI

class OauthGetAuthKeyHelper(object):

    def __init__(self, token_file_dir, oauth_version = 'oauth2'):
        self.auth_dir = os.path.dirname(os.path.dirname(__file__))
        self.token_file_dir = "token" + str(token_file_dir)
        self.oauth_version = oauth_version

        auth_dir = os.path.dirname(os.path.dirname(__file__))
        with open(os.path.join(auth_dir, "private.json")) as yahoo_app_credentials:
            auth_info = json.load(yahoo_app_credentials)

        self.consumer_key = auth_info["consumer_key"]
        self.consumer_secret = auth_info["consumer_secret"]

    def need_verifier_code(self):
        pathToTokenDir = os.path.join(self.auth_dir + "/tokens/" + self.token_file_dir) 

        pathToToken = os.path.join(self.auth_dir + "/tokens/" + self.token_file_dir, "token.json") 

        # check if directory for user token directory exists
        if not os.path.isdir(pathToTokenDir) or not os.path.isfile(pathToToken) :
            return True

        #if token dir does exist and some other validity check
        data = get_data(pathToToken)
        if "access_token" not in data and "refresh_token" not in data:
            return True

        return False

    def get_auth_url(self):
        # auth_dir = os.path.dirname(os.path.dirname(__file__))
        # with open(os.path.join(auth_dir, "private.json")) as yahoo_app_credentials:
        #     auth_info = json.load(yahoo_app_credentials)
        # consumer_key = auth_info["consumer_key"]
        # consumer_secret = auth_info["consumer_secret"]
        service_params = {
                'client_id': self.consumer_key,
                'client_secret': self.consumer_secret,
                'name' : 'yahoo',
                'access_token_url' : services[self.oauth_version]['ACCESS_TOKEN_URL'],
                'authorize_url' : services[self.oauth_version]['AUTHORIZE_TOKEN_URL'],
                'base_url': None
            }

        # Defining oauth service
        oauthService = services[self.oauth_version]['SERVICE'](**service_params)
        return oauthService.get_authorize_url(client_secret=self.consumer_secret, redirect_uri=CALLBACK_URI, response_type='code')
  

