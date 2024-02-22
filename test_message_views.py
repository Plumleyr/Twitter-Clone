"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        uid = 1111
        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser.id = uid

        db.session.commit()

        uid2 = 2222
        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        self.testuser2.id = uid2

        db.session.commit()

        testuser = User.query.get(uid)
        testuser2 = User.query.get(uid2)

        self.testuser = testuser
        self.testuser2 = testuser2

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_messages_show(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            m = Message(text = "Hi", user_id = self.testuser.id)
            m.id = 1010
            db.session.add(m)
            db.session.commit()
            
            resp = c.get("/messages/1010")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Hi", str(resp.data))

    def test_invalid_message(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/messages/29356")

            self.assertEqual(resp.status_code,404)

    def test_delete_message(self):
        

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            m = Message(text = "Hi", user_id = self.testuser.id)
            m.id = 1010
            db.session.add(m)
            db.session.commit()

            resp = c.post("/messages/1010/delete")

            u_messages = Message.query.filter(Message.user_id == self.testuser.id).all()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(len(u_messages), 0)

    def test_delete_message_bad(self):
        

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            m = Message(text = "Hi", user_id = self.testuser2.id)
            m.id = 1010
            db.session.add(m)
            db.session.commit()

            resp = c.post("/messages/1010/delete")

            u2_messages = Message.query.filter(Message.user_id == self.testuser2.id).all()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(len(u2_messages), 1)