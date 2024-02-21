"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User(
        email="test@test.com",
        username="testuser",
        password="hashedpass"
        )

        db.session.add(u)
        db.session.commit()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test2@test.com",
            username="testuser2",
            password="hashedpass2"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_signup_get(self):

        resp = self.client.get('/signup')
        html = resp.get_data(as_text = True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('name="csrf_token"', html)
        self.assertIn('name="username"', html)
        self.assertIn('name="password"', html)

    def test_user_signup_post(self):
        # Make a GET request to get the CSRF token
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)

        # Extract the CSRF token from the response data
        csrf_token = response.form['csrf_token']

        # Prepare form data including the CSRF token
        form_data = {
            'csrf_token': csrf_token,
            'email': 'test2@test.com',
            'username': 'testuser2',
            'password': 'actualpassword'
        }

        # Post the form data to the signup route
        response = self.client.post('/signup', data=form_data, follow_redirects=True)

        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check if the user was created in the database
        user = User.query.filter_by(username='testuser2').first()
        self.assertIsNotNone(user)
        # self.assertEqual(user.email, 'test2@test.com' )

    # def test_user_signup_post_bad(self):
    #     d = {'email' : 'test@test.com', 'username' : 'testuser', 'password' : 'hashedpass2'}
    #     resp = self.client.post('/signup', data = d, follow_redirects = True)
    #     html = resp.get_data(as_text=True)

    #     self.assertEqual(resp.status_code, 200)
    #     self.assertIn('Username already taken', html )

    def test_user_login_get(self):

        resp = self.client.get('/login')
        html = resp.get_data(as_text = True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('name="csrf_token"', html)
        self.assertIn('name="username"', html)
        self.assertIn('name="password"', html)