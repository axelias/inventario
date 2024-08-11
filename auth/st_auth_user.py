import streamlit_authenticator as stauth

class UserAuthenticator(object):
    def __init__(self):
        self.name = None
        self.authentication_status = None
        self.username = None
        self.authenticator = None
        self.authenticate_user()

    def authenticate_user(self):
        # Define static credentials
        credentials = {
            "usernames": {
                "admin": {
                    "name": "inv247",
                    "password": "inv247"
                }
            }
        }
        
        # Define static cookie configuration
        cookie_config = {
            "name": "auth_cookie",
            "key": "some_random_secret_key",
            "expiry_days": 30  # Adjust as needed
        }

        self.authenticator = stauth.Authenticate(
            credentials,
            cookie_config['name'],
            cookie_config['key'],
            cookie_config['expiry_days']
        )
        
        self.name, self.authentication_status, self.username = self.authenticator.login(clear_on_submit=True)

    def logout(self):
        self.authenticator.logout('Logout', 'unrendered')

# Usage example
auth = UserAuthenticator()
if auth.authentication_status:
    st.write(f"Welcome {auth.name}!")
elif auth.authentication_status is False:
    st.error("Username/password is incorrect")
elif auth.authentication_status is None:
    st.warning("Please enter your username and password")
