from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


class RegistrationTests(APITestCase):
    """Test user registration endpoint"""

    def test_register_user_success(self):
        """Test successful user registration with all required fields"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'age': 25,
            'country': 'USA',
            'residence': 'New York'
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['first_name'], 'Test')
        self.assertEqual(response.data['last_name'], 'User')
        self.assertEqual(response.data['age'], 25)
        self.assertEqual(response.data['country'], 'USA')
        self.assertEqual(response.data['residence'], 'New York')

    def test_register_user_minimal_fields(self):
        """Test registration with only required fields"""
        data = {
            'username': 'minimal',
            'email': 'minimal@example.com',
            'password': 'pass123'
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

    def test_register_duplicate_username(self):
        """Test registration with duplicate username fails"""
        User.objects.create_user(username='existing', email='existing@example.com', password='pass')
        data = {
            'username': 'existing',
            'email': 'new@example.com',
            'password': 'pass123'
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        """Test registration with duplicate email (Django allows duplicate emails by default)"""
        User.objects.create_user(username='user1', email='same@example.com', password='pass')
        data = {
            'username': 'user2',
            'email': 'same@example.com',
            'password': 'pass123'
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        # Django's AbstractUser doesn't enforce unique emails by default
        # So duplicate emails are allowed
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_missing_required_fields(self):
        """Test registration without required fields fails"""
        data = {'username': 'test'}
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    """Test user login endpoint"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_login_success(self):
        """Test successful login returns token"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_wrong_password(self):
        """Test login with wrong password fails"""
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        """Test login with nonexistent user fails"""
        data = {
            'username': 'nonexistent',
            'password': 'pass123'
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PasswordResetTests(APITestCase):
    """Test password reset endpoint"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpass123'
        )

    def test_reset_password_success(self):
        """Test successful password reset"""
        data = {
            'email': 'test@example.com',
            'new_password': 'newpass123'
        }
        response = self.client.post('/api/auth/reset-password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))

    def test_reset_password_nonexistent_email(self):
        """Test password reset with nonexistent email"""
        data = {
            'email': 'nonexistent@example.com',
            'new_password': 'newpass123'
        }
        response = self.client.post('/api/auth/reset-password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_reset_password_multiple_users_same_email(self):
        """Test password reset when multiple users share email"""
        # Create another user with same email
        User.objects.create_user(
            username='user2',
            email='test@example.com',
            password='pass2'
        )
        data = {
            'email': 'test@example.com',
            'new_password': 'newpass123'
        }
        response = self.client.post('/api/auth/reset-password/', data, format='json')
        # Should reset password for first matched user
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check for success message or warning about multiple users
        response_text = str(response.data)
        self.assertTrue(
            'successful' in response_text.lower() or 'multiple' in response_text.lower()
        )

    def test_reset_password_missing_fields(self):
        """Test password reset without required fields"""
        data = {'email': 'test@example.com'}
        response = self.client.post('/api/auth/reset-password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

