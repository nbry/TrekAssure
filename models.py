""" SQLAlchemy models for TrekAssure """

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """ Connect this database to provided Flask app """
    db.app = app
    db.init_app(app)


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, default=None)
    address = db.Column(db.Text, default=None)

    @classmethod
    def register(cls, username, pwd, email, address):
        """ Register user w/hashed password and return use """

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8, email=email, address=address)

    @classmethod
    def authenticate(cls, username, pwd):
        """ Validate that user exists and password is correct 

        Return user if valid; else return False
        """

        user = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return user
        else:
            return False
