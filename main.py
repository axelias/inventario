# auth/st_auth_user.py

class UserAuthenticator:
    def __init__(self):
        self.username = "inv247"
        self.password = "inv247"
        self.authentication_status = None
        self.authenticate()

    def authenticate(self):
        input_username = st.text_input('Username')
        input_password = st.text_input('Password', type='password')

        if st.button('Login'):
            if input_username == self.username and input_password == self.password:
                self.authentication_status = True
            else:
                self.authentication_status = False
