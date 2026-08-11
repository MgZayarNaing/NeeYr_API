from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class APIRouteTests(APITestCase):

    def setUp(self):
        # Create a mock user for authenticated endpoints
        self.user = User.objects.create_user(
            username="testuser", 
            email="test@example.com", 
            password="Password123!"
        )

    def test_login(self):
        """Test authentication endpoint"""
        url = reverse('user-login')  # Uses the route name from your URLconf
        data = {'username': 'testuser', 'password': 'Password123!'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_categories_unauthenticated(self):
        """Test retrieving category list"""
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED])