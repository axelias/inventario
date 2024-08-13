from controllers.auth_controller import AuthController

class Logout(AuthController):
    def show(self):
        self.auth.logout()