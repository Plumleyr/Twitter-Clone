"""User views tests."""

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

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewsTestCase(TestCase):
    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "test1@test.com", "password", None)
        uid1 = 1111
        u1.id = uid1

        u2 = User.signup("test2", "test2@test.com", "password", None)
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_list_users(self):
        resp = self.client.get('/users')

        self.assertEqual(resp.status_code, 200)
        self.assertIn("@test1", str(resp.data))
        self.assertIn("@test2", str(resp.data))

    def test_users_show(self):
        resp = self.client.get(f'/users/{self.u1.id}')

        self.assertEqual(resp.status_code, 200)
        self.assertIn("@test1", str(resp.data))

    def test_users_followers(self):
        follow = Follows(user_being_followed_id = self.u1.id, user_following_id = self.u2.id)
        db.session.add(follow)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.u1.id
            
        resp = self.client.get(f"/users/{self.u1.id}/followers")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("@test2", str(resp.data))

    def test_users_following(self):
        follow = Follows(user_being_followed_id = self.u1.id, user_following_id = self.u2.id)
        db.session.add(follow)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.u2.id
            
        resp = self.client.get(f"/users/{self.u2.id}/following")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("@test1", str(resp.data))

    def test_add_like(self):
        m = Message(id=1111, text="Hi", user_id=self.u1.id)
        db.session.add(m)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.u2.id

        resp = self.client.post("/users/add_like/1111", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        likes = Likes.query.filter(Likes.message_id==1111).all()
        self.assertEqual(len(likes), 1)

    def test_remove_like(self):
        m = Message(id=1111, text="Hi", user_id=self.u1.id)
        db.session.add(m)
        db.session.commit()

        l = Likes(user_id = self.u2.id, message_id = 1111)
        db.session.add(l)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.u2.id

        resp = self.client.post("/users/add_like/1111", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        likes = Likes.query.filter(Likes.message_id==1111).all()
        self.assertEqual(len(likes), 0)

    def test_show_likes(self):
        m = Message(id=1111, text="Hi", user_id=self.u1.id)
        db.session.add(m)
        db.session.commit()

        l = Likes(user_id = self.u2.id, message_id = 1111)
        db.session.add(l)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.u2.id

        resp = self.client.get(f'/users/{self.u2.id}/likes')
        self.assertEqual(resp.status_code, 200)

        self.assertIn("Hi", str(resp.data))