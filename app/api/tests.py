from django.test import TestCase, Client
from django.urls import reverse


class Tests(TestCase):

    def test_registration(self):
        # No body
        response = Client().post(reverse('registration'), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['result'], None)

        # Empty password
        body = {'password': ''}
        response = Client().post(reverse('registration'), body, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['result'], None)
        self.assertEqual(response.json()['error'], 'Password can not be empty')
