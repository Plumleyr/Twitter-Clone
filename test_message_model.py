"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class MessageModelTestCase(TestCase):

    def setUp(self):

        db.drop_all()
        db.create_all()

        self.uid1 = 1111
        u1 = User.signup("test1", "test1@test.com", "password", None)
        u1.id = self.uid1
        db.session.commit()

        self.u1 = User.query.get(self.uid1)

        self.client = app.test_client()

    def tearDown(self):

        db.session.rollback()

    def test_message_model(self):

        m = Message(text = "Hi", user_id = self.u1.id)

        db.session.add(m)
        db.session.commit()

        self.assertEqual(len(self.u1.messages), 1)
        self.assertEqual(self.u1.messages[0].text, "Hi")

    def test_message_likes(self):

        m = Message(text = "Hi", user_id = self.u1.id)

        db.session.add(m)
        db.session.commit()

        u2 = User.signup("test2", "test2@test.com", "password", None)
        uid2 = 2222
        u2.id = uid2
        db.session.add(u2)
        db.session.commit()

        u2.likes.append(m)
        db.session.commit()
        
        u2likes = Likes.query.filter(Likes.user_id == uid2).all()

        self.assertEqual(len(u2likes),1)
        self.assertEqual(u2likes[0].message_id, m.id)