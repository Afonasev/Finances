import unittest

import peewee
import webtest

import finances
from finances import models


class TestControllers(unittest.TestCase):
    test_email = 'user@mail.com'
    test_password = 'abc456'

    def setUp(self):
        models.database.initialize(peewee.SqliteDatabase(':memory:'))

        from manage import init_db
        init_db()

        self.app = webtest.TestApp(finances.app)

    def test_not_found_page(self):
        self.assertRaises(webtest.app.AppError, self.app.get, '/smt_page')

    def test_register(self):
        url = '/register'

        self.assertEqual(self.app.get(url).status, '200 OK')

        self.assertIn(
            'Create a new Finances user', self.app.get(url).text
        )

        self._empty_email_pass_test(url)

        # Test: invalid email
        answer_page = self.app.post(url, {
            'email': 'invalid_email',
            'password': self.test_password,
        }).text
        self.assertIn('Email is not correct', answer_page)

        # Test: length of password must be greater than 5 letters
        answer_page = self.app.post(url, {
            'email': self.test_email,
            'password': 'A1234',
        }).text
        self.assertIn('password must be greater', answer_page)

        # Test: the password should contain numbers
        answer_page = self.app.post(url, {
            'email': self.test_email,
            'password': 'abcdef',
        }).text
        self.assertIn('The password should contain numbers', answer_page)

        # Test: the password should contain letters
        answer_page = self.app.post(url, {
            'email': self.test_email,
            'password': '123456',
        }).text
        self.assertIn('The password should contain letters', answer_page)

        # Test: register new user successful
        self.app.post(url, {
            'email': self.test_email,
            'password': self.test_password,
        })
        self.assertTrue(models.User._check(email=self.test_email))

        # Test: try register duplicate user
        answer_page = self.app.post(url, {
            'email': self.test_email,
            'password': self.test_password,
        }).text
        self.assertIn('User with same email already exists', answer_page)

    def test_login(self):
        url = '/login'

        # Test: get page
        self.assertEqual(self.app.get(url).status, '200 OK')
        self.assertIn(
            'Login with your Finances account', self.app.get(url).text
        )

        self._empty_email_pass_test(url)

        # Test: wrong email
        answer_page = self.app.post(url, {
            'email': 'wrong_email',
            'password': self.test_password,
        }).text
        self.assertIn('Wrong email or password', answer_page)

        # Test: wrong password
        answer_page = self.app.post(url, {
            'email': self.test_email,
            'password': 'wrong_password',
        }).text
        self.assertIn('Wrong email or password', answer_page)

        # Test: wrong email and password
        answer_page = self.app.post(url, {
            'email': 'wrong_email',
            'password': 'wrong_password',
        }).text
        self.assertIn('Wrong email or password', answer_page)

        # Test: User not exist
        answer_page = self.app.post(url, {
            'email': self.test_email,
            'password': self.test_password,
        }).text
        self.assertIn('Wrong email or password', answer_page)

        models.User.reg(
            email=self.test_email,
            password=self.test_password,
        )

        # Test: login successful
        self.app.post(url, {
            'email': self.test_email,
            'password': self.test_password,
        })

        self.assertTrue(self.app.cookies.get('user_id'))

    def test_logout(self):
        models.User.reg(
            email=self.test_email,
            password=self.test_password,
        )

        # Test: login not yet done
        self.assertFalse(self.app.cookies.get('user_id'))

        self.app.post('/login', {
            'email': self.test_email,
            'password': self.test_password,
        })
        # Test: login successful
        self.assertTrue(self.app.cookies.get('user_id'))

        # Test: logout successful
        self.app.get('/logout')
        self.assertFalse(self.app.cookies.get('user_id'))

    def _empty_email_pass_test(self, url):
        # Test: email is empty
        answer_page = self.app.post(url, {
            'email': '',
            'password': self.test_password,
        }).text
        self.assertIn('Email is empty', answer_page)

        # Test: password is empty
        answer_page = self.app.post(url, {
            'email': self.test_email,
            'password': '',
        }).text
        self.assertIn('Password is empty', answer_page)
