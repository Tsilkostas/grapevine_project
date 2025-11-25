from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from api.models import Project, ProjectInterest, Skill, UserSkill

User = get_user_model()


class ExpressInterestTests(APITestCase):
    """Test express interest endpoint"""

    def setUp(self):
        self.owner = User.objects.create_user(username='owner', email='owner@example.com', password='pass')
        self.applicant1 = User.objects.create_user(username='applicant1', email='app1@example.com', password='pass')
        self.applicant2 = User.objects.create_user(username='applicant2', email='app2@example.com', password='pass')
        self.project = Project.objects.create(
            project_name='Test Project',
            description='Description',
            owner=self.owner,
            maximum_collaborators=2
        )
        # Add skills to applicants
        skill_py, _ = Skill.objects.get_or_create(name='py')
        skill_js, _ = Skill.objects.get_or_create(name='js')
        UserSkill.objects.create(user=self.applicant1, skill=skill_py, level='experienced')
        UserSkill.objects.create(user=self.applicant1, skill=skill_js, level='beginner')
        UserSkill.objects.create(user=self.applicant2, skill=skill_py, level='expert')

    def test_express_interest_success(self):
        """Test successfully expressing interest"""
        self.client.force_authenticate(user=self.applicant1)
        response = self.client.post(f'/api/projects/{self.project.id}/interest/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ProjectInterest.objects.filter(user=self.applicant1, project=self.project).exists())
        interest = ProjectInterest.objects.get(user=self.applicant1, project=self.project)
        self.assertEqual(interest.status, 'pending')

    def test_express_interest_unauthenticated(self):
        """Test expressing interest without authentication fails"""
        response = self.client.post(f'/api/projects/{self.project.id}/interest/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_express_interest_duplicate(self):
        """Test expressing interest twice fails"""
        self.client.force_authenticate(user=self.applicant1)
        # First interest
        response = self.client.post(f'/api/projects/{self.project.id}/interest/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Second interest should fail
        response = self.client.post(f'/api/projects/{self.project.id}/interest/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already expressed', response.data['detail'])

    def test_express_interest_when_full(self):
        """Test expressing interest when project is full"""
        # Fill all seats
        self.project.contributors.add(self.owner)
        self.project.contributors.add(self.applicant2)
        
        self.client.force_authenticate(user=self.applicant1)
        response = self.client.post(f'/api/projects/{self.project.id}/interest/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_msg = str(response.data.get('detail', ''))
        self.assertTrue('seats' in error_msg.lower() or 'available' in error_msg.lower())

    def test_express_interest_nonexistent_project(self):
        """Test expressing interest in nonexistent project"""
        self.client.force_authenticate(user=self.applicant1)
        response = self.client.post('/api/projects/99999/interest/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PendingInterestsTests(APITestCase):
    """Test pending interests endpoint"""

    def setUp(self):
        self.owner = User.objects.create_user(username='owner', email='owner@example.com', password='pass')
        self.applicant1 = User.objects.create_user(username='applicant1', email='app1@example.com', password='pass')
        self.applicant2 = User.objects.create_user(username='applicant2', email='app2@example.com', password='pass')
        self.other_user = User.objects.create_user(username='other', email='other@example.com', password='pass')
        
        self.project = Project.objects.create(
            project_name='Test Project',
            description='Description',
            owner=self.owner,
            maximum_collaborators=3
        )
        
        # Create interests
        skill_py, _ = Skill.objects.get_or_create(name='py')
        skill_js, _ = Skill.objects.get_or_create(name='js')
        UserSkill.objects.create(user=self.applicant1, skill=skill_py, level='experienced')
        UserSkill.objects.create(user=self.applicant2, skill=skill_js, level='beginner')
        
        self.interest1 = ProjectInterest.objects.create(user=self.applicant1, project=self.project, status='pending')
        self.interest2 = ProjectInterest.objects.create(user=self.applicant2, project=self.project, status='pending')
        self.interest3 = ProjectInterest.objects.create(user=self.other_user, project=self.project, status='accepted')

    def test_get_pending_interests_as_owner(self):
        """Test owner can view pending interests"""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(f'/api/projects/{self.project.id}/pending_interests/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only pending interests
        
        # Verify privacy - only username, email, and skills visible
        for interest in response.data:
            user_data = interest['user']
            self.assertIn('username', user_data)
            self.assertIn('email', user_data)
            self.assertIn('skills', user_data)
            # Should NOT include sensitive fields
            self.assertNotIn('first_name', user_data)
            self.assertNotIn('last_name', user_data)
            self.assertNotIn('age', user_data)
            self.assertNotIn('country', user_data)
            self.assertNotIn('residence', user_data)

    def test_get_pending_interests_unauthenticated(self):
        """Test getting pending interests without authentication fails"""
        response = self.client.get(f'/api/projects/{self.project.id}/pending_interests/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_pending_interests_not_owner(self):
        """Test non-owner cannot view pending interests"""
        self.client.force_authenticate(user=self.applicant1)
        response = self.client.get(f'/api/projects/{self.project.id}/pending_interests/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pending_interests_privacy_constraint(self):
        """Test that only username, email, and skills are visible"""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(f'/api/projects/{self.project.id}/pending_interests/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check first interest
        interest_data = response.data[0]
        user_data = interest_data['user']
        
        # Required fields
        self.assertIn('username', user_data)
        self.assertIn('email', user_data)
        self.assertIn('skills', user_data)
        
        # Skills should have correct structure
        if user_data['skills']:
            skill = user_data['skills'][0]
            self.assertIn('skill', skill)
            self.assertIn('level', skill)


class AcceptInterestTests(APITestCase):
    """Test accept interest endpoint"""

    def setUp(self):
        self.owner = User.objects.create_user(username='owner', email='owner@example.com', password='pass')
        self.applicant = User.objects.create_user(username='applicant', email='app@example.com', password='pass')
        self.project = Project.objects.create(
            project_name='Test Project',
            description='Description',
            owner=self.owner,
            maximum_collaborators=2
        )
        self.interest = ProjectInterest.objects.create(user=self.applicant, project=self.project, status='pending')

    def test_accept_interest_success(self):
        """Test successfully accepting an interest"""
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f'/api/projects/{self.project.id}/interest/{self.interest.id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.interest.refresh_from_db()
        self.assertEqual(self.interest.status, 'accepted')
        self.assertIn(self.applicant, self.project.contributors.all())

    def test_accept_interest_unauthenticated(self):
        """Test accepting interest without authentication fails"""
        response = self.client.post(f'/api/projects/{self.project.id}/interest/{self.interest.id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_accept_interest_not_owner(self):
        """Test non-owner cannot accept interest"""
        self.client.force_authenticate(user=self.applicant)
        response = self.client.post(f'/api/projects/{self.project.id}/interest/{self.interest.id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accept_interest_when_full(self):
        """Test accepting interest when project is full"""
        # Fill all seats
        other_user = User.objects.create_user(username='other', email='other@example.com', password='pass')
        self.project.contributors.add(self.owner, other_user)
        
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f'/api/projects/{self.project.id}/interest/{self.interest.id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_msg = str(response.data.get('detail', ''))
        self.assertTrue('seats' in error_msg.lower() or 'available' in error_msg.lower())

    def test_accept_already_handled_interest(self):
        """Test accepting an already handled interest"""
        self.interest.status = 'accepted'
        self.interest.save()
        
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f'/api/projects/{self.project.id}/interest/{self.interest.id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_msg = str(response.data.get('detail', ''))
        self.assertTrue('handled' in error_msg.lower() or 'already' in error_msg.lower())

    def test_accept_nonexistent_interest(self):
        """Test accepting nonexistent interest"""
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f'/api/projects/{self.project.id}/interest/99999/accept/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DeclineInterestTests(APITestCase):
    """Test decline interest endpoint"""

    def setUp(self):
        self.owner = User.objects.create_user(username='owner', email='owner@example.com', password='pass')
        self.applicant = User.objects.create_user(username='applicant', email='app@example.com', password='pass')
        self.project = Project.objects.create(
            project_name='Test Project',
            description='Description',
            owner=self.owner,
            maximum_collaborators=2
        )
        self.interest = ProjectInterest.objects.create(user=self.applicant, project=self.project, status='pending')

    def test_decline_interest_success(self):
        """Test successfully declining an interest"""
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f'/api/projects/{self.project.id}/interest/{self.interest.id}/decline/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.interest.refresh_from_db()
        self.assertEqual(self.interest.status, 'declined')
        # User should NOT be added as contributor
        self.assertNotIn(self.applicant, self.project.contributors.all())

    def test_decline_interest_unauthenticated(self):
        """Test declining interest without authentication fails"""
        response = self.client.post(f'/api/projects/{self.project.id}/interest/{self.interest.id}/decline/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_decline_interest_not_owner(self):
        """Test non-owner cannot decline interest"""
        self.client.force_authenticate(user=self.applicant)
        response = self.client.post(f'/api/projects/{self.project.id}/interest/{self.interest.id}/decline/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_decline_already_handled_interest(self):
        """Test declining an already handled interest"""
        self.interest.status = 'declined'
        self.interest.save()
        
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f'/api/projects/{self.project.id}/interest/{self.interest.id}/decline/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_msg = str(response.data.get('detail', ''))
        self.assertTrue('handled' in error_msg.lower() or 'already' in error_msg.lower())

    def test_decline_nonexistent_interest(self):
        """Test declining nonexistent interest"""
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f'/api/projects/{self.project.id}/interest/99999/decline/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

