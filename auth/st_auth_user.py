import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


class UserAuthenticator(object):
    def __init__(self):
        self.name = None
        self.authentication_status = None
        self.username = None
        self.authenticator = None
        self.authenticate_user()

    def authenticate_user(self):
        with open('config/auth_config.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)

        self.authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
            config['preauthorized']
        )
        self.name, self.authentication_status, self.username = self.authenticator.login(clear_on_submit= True)

    def logout(self):
        self.authenticator.logout('Logout', 'unrendered')