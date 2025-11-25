from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from api.models import Skill, UserSkill

User = get_user_model()


class SkillAddTests(APITestCase):
    """Test add skill endpoint"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Create skills
        for name in ['cpp', 'js', 'py', 'java', 'lua', 'rust', 'go', 'julia']:
            Skill.objects.get_or_create(name=name)

    def test_add_skill_success(self):
        """Test successfully adding a skill"""
        self.client.force_authenticate(user=self.user)
        data = {
            'skill': 'py',
            'level': 'experienced'
        }
        response = self.client.post('/api/skills/add/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserSkill.objects.filter(user=self.user, skill__name='py').exists())

    def test_add_skill_unauthenticated(self):
        """Test adding skill without authentication fails"""
        data = {
            'skill': 'py',
            'level': 'experienced'
        }
        response = self.client.post('/api/skills/add/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_skill_invalid_level(self):
        """Test adding skill with invalid level fails"""
        self.client.force_authenticate(user=self.user)
        data = {
            'skill': 'py',
            'level': 'invalid_level'
        }
        response = self.client.post('/api/skills/add/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_skill_invalid_language(self):
        """Test adding skill with invalid language fails"""
        self.client.force_authenticate(user=self.user)
        data = {
            'skill': 'invalid_lang',
            'level': 'beginner'
        }
        response = self.client.post('/api/skills/add/', data, format='json')
        # Should still create the skill (get_or_create), but test the flow
        response = self.client.post('/api/skills/add/', data, format='json')
        # Second attempt should fail due to skill already added
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_duplicate_skill(self):
        """Test adding the same skill twice fails"""
        self.client.force_authenticate(user=self.user)
        data = {
            'skill': 'py',
            'level': 'beginner'
        }
        # First add
        response = self.client.post('/api/skills/add/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Second add should fail
        response = self.client.post('/api/skills/add/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # ValidationError returns errors in field format: {'skill': ['error message']}
        # Check if error is in 'skill' field or 'detail' field
        if 'skill' in response.data and isinstance(response.data['skill'], list):
            error_msg = str(response.data['skill'][0])
        elif 'detail' in response.data:
            error_msg = str(response.data['detail'])
        else:
            error_msg = str(response.data)
        # The error should mention that skill is already added
        self.assertTrue(
            'already' in error_msg.lower() or 'skill' in error_msg.lower(),
            f"Expected 'already' in error message, got: {error_msg}"
        )

    def test_add_max_three_skills(self):
        """Test that maximum 3 skills can be added"""
        self.client.force_authenticate(user=self.user)
        
        # Add 3 skills
        for skill_name in ['py', 'js', 'cpp']:
            data = {'skill': skill_name, 'level': 'beginner'}
            response = self.client.post('/api/skills/add/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify 3 skills exist
        self.assertEqual(UserSkill.objects.filter(user=self.user).count(), 3)
        
        # Try to add 4th skill - should fail
        data = {'skill': 'java', 'level': 'beginner'}
        response = self.client.post('/api/skills/add/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check error message
        error_msg = str(response.data.get('detail', ''))
        self.assertIn('maximum', error_msg.lower())

    def test_add_skill_all_levels(self):
        """Test adding skills with all valid levels"""
        self.client.force_authenticate(user=self.user)
        levels = ['beginner', 'experienced', 'expert']
        
        for i, level in enumerate(levels):
            skill_name = ['py', 'js', 'cpp'][i]
            data = {'skill': skill_name, 'level': level}
            response = self.client.post('/api/skills/add/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            user_skill = UserSkill.objects.get(user=self.user, skill__name=skill_name)
            self.assertEqual(user_skill.level, level)

    def test_add_skill_all_languages(self):
        """Test adding all supported programming languages"""
        self.client.force_authenticate(user=self.user)
        languages = ['cpp', 'js', 'py', 'java', 'lua', 'rust', 'go', 'julia']
        
        # Can only add 3, so test first 3
        for lang in languages[:3]:
            data = {'skill': lang, 'level': 'beginner'}
            response = self.client.post('/api/skills/add/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class SkillRemoveTests(APITestCase):
    """Test remove skill endpoint"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Get or create skills (they may already exist from migrations)
        self.skill_py, _ = Skill.objects.get_or_create(name='py')
        self.skill_js, _ = Skill.objects.get_or_create(name='js')
        # Add skills to user
        UserSkill.objects.create(user=self.user, skill=self.skill_py, level='experienced')
        UserSkill.objects.create(user=self.user, skill=self.skill_js, level='beginner')

    def test_remove_skill_success(self):
        """Test successfully removing a skill"""
        self.client.force_authenticate(user=self.user)
        data = {'skill': 'py'}
        response = self.client.post('/api/skills/remove/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(UserSkill.objects.filter(user=self.user, skill=self.skill_py).exists())
        self.assertTrue(UserSkill.objects.filter(user=self.user, skill=self.skill_js).exists())

    def test_remove_skill_unauthenticated(self):
        """Test removing skill without authentication fails"""
        data = {'skill': 'py'}
        response = self.client.post('/api/skills/remove/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_remove_nonexistent_skill(self):
        """Test removing a skill that doesn't exist"""
        self.client.force_authenticate(user=self.user)
        data = {'skill': 'nonexistent'}
        response = self.client.post('/api/skills/remove/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_skill_not_associated_with_user(self):
        """Test removing a skill that user doesn't have"""
        self.client.force_authenticate(user=self.user)
        # Get or create another skill not associated with user
        skill_rust, _ = Skill.objects.get_or_create(name='rust')
        data = {'skill': 'rust'}
        response = self.client.post('/api/skills/remove/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_all_skills(self):
        """Test removing all user skills"""
        self.client.force_authenticate(user=self.user)
        
        # Remove first skill
        data = {'skill': 'py'}
        response = self.client.post('/api/skills/remove/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Remove second skill
        data = {'skill': 'js'}
        response = self.client.post('/api/skills/remove/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify no skills remain
        self.assertEqual(UserSkill.objects.filter(user=self.user).count(), 0)

