from django.test import TestCase


from django.test import TestCase
from django.urls import reverse


class ChatTest(TestCase):
    def test_login(self):
        response = self.client.post(reverse('account_login'), {
            'email': 'admin@admin.com',
            'password': 'admin',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/home.html')

        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('account_login'))

        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
