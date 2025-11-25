from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from api.models import Project, ProjectInterest

User = get_user_model()


class StatsTests(APITestCase):
    """Test user statistics endpoint"""

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='u1@example.com', password='pass')
        self.user2 = User.objects.create_user(username='user2', email='u2@example.com', password='pass')
        self.user3 = User.objects.create_user(username='user3', email='u3@example.com', password='pass')
        
        # User1 creates 2 projects
        self.project1 = Project.objects.create(
            project_name='Project 1',
            description='First project',
            owner=self.user1,
            maximum_collaborators=2
        )
        self.project2 = Project.objects.create(
            project_name='Project 2',
            description='Second project',
            owner=self.user1,
            maximum_collaborators=1
        )
        
        # User2 creates 1 project
        self.project3 = Project.objects.create(
            project_name='Project 3',
            description='Third project',
            owner=self.user2,
            maximum_collaborators=2
        )
        
        # User1 contributes to project3 (accepted interest)
        self.project3.contributors.add(self.user1)
        ProjectInterest.objects.create(user=self.user1, project=self.project3, status='accepted')
        
        # User2 contributes to project1
        self.project1.contributors.add(self.user2)
        ProjectInterest.objects.create(user=self.user2, project=self.project1, status='accepted')
        
        # User3 expresses interest but not accepted
        ProjectInterest.objects.create(user=self.user3, project=self.project1, status='pending')

    def test_get_stats_success(self):
        """Test successfully getting user statistics"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/users/me/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('projects_created', response.data)
        self.assertIn('projects_contributed', response.data)
        self.assertEqual(response.data['projects_created'], 2)
        self.assertEqual(response.data['projects_contributed'], 1)  # Only project3 where user1 is contributor

    def test_get_stats_unauthenticated(self):
        """Test getting stats without authentication fails"""
        response = self.client.get('/api/users/me/stats/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_stats_user_with_no_projects(self):
        """Test stats for user with no created or contributed projects"""
        new_user = User.objects.create_user(username='newuser', email='new@example.com', password='pass')
        self.client.force_authenticate(user=new_user)
        response = self.client.get('/api/users/me/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['projects_created'], 0)
        self.assertEqual(response.data['projects_contributed'], 0)

    def test_stats_counts_only_actual_contributions(self):
        """Test that stats count actual contributions, not just interests"""
        self.client.force_authenticate(user=self.user3)
        response = self.client.get('/api/users/me/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # User3 expressed interest but wasn't accepted, so contributed should be 0
        self.assertEqual(response.data['projects_contributed'], 0)

    def test_stats_multiple_contributions(self):
        """Test stats for user who contributed to multiple projects"""
        # Add user1 as contributor to another project
        self.project2.contributors.add(self.user1)
        ProjectInterest.objects.create(user=self.user1, project=self.project2, status='accepted')
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/users/me/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['projects_created'], 2)
        self.assertEqual(response.data['projects_contributed'], 2)  # project2 and project3

    def test_stats_completed_projects_count(self):
        """Test that completed projects are still counted"""
        self.project1.completed = True
        self.project1.save()
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/users/me/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Completed projects should still count
        self.assertEqual(response.data['projects_created'], 2)




