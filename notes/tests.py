from django.test import TestCase
from django.contrib.auth import get_user_model


class UserManagersTests(TestCase):

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email='justa@user.com', password='rrr')
        self.assertEqual(user.email, 'justa@user.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        try:
            self.assertIsNone(user.username)
        except AttributeError:
            ...
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email='')
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='rrr')

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(email='giga@user.com', password='rrrr')
        self.assertEqual(admin_user.email, 'giga@user.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        try:
            self.assertIsNone(admin_user.username)
        except AttributeError:
            ...
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='giga@user.com', password='rrrr', is_superuser=False)
