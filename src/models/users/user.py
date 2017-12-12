import uuid
from src.common.database import Database
from src.common.utils import Utils
import src.models.users.errors as UserErrors
from src.models.alerts.alert import Alert


class User(object):
    def __init__(self, email, password, _id=None):
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else id

    def __repr__(self):
        return "<User {}>".format(self.email)

    @staticmethod
    def is_login_valid(email,password):
        """
        This method verifies that an email-password combo sent by the site forms is valid or not.
        Checks that the email exists and the password associated to it is correct
        :param email: The user's email
        :param password: A sha512 hashed password
        :return: True if valid, False otherwise
        """

        user_data = Database.find_one('users',{'email':email})
        if user_data is None:
            # Tell the user that the email does not exist
            raise UserErrors.UserNotExistsError("Your username does not exist.")
        if not Utils.check_hashed_password(password,user_data['password']):
            # Tell the user that the password is wrong
            raise UserErrors.IncorrectPasswordError("Your password is not correct.")
        return True

    @staticmethod
    def register_user(email,password):
        """
        This method registers a user using an email and a password. The password already comes
        hashed as sha-512.
        :param email: user's email (might be valid)
        :param password: sha-512 hashed password
        :return: true if registed otherwise, false otherwise
        """
        user_data = Database.find_one('users',{'email':email})
        if user_data is not None:
            raise UserErrors.UserAlreadyRegisteredError("The User already exists")
        if not Utils.email_is_valid(email):
            raise UserErrors.InvalidEmailError("The Email does not have the right format")
        User(email,Utils.hash_password(password)).save_to_db()
        return True

    def save_to_db(self):
        Database.insert('users',self.json())

    def json(self):
        return {
            "_id":self._id,
            "email":self.email,
            "password":self.password
        }

    @classmethod
    def find_by_email(cls,email):
        user=Database.find_one('users',{'email':email})
        User=cls(**user)
        return User

    def get_alerts(self):
        return Alert.find_by_user_email(self.email)