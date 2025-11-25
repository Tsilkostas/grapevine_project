from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from api.models import Project

User = get_user_model()


class ProjectCreateTests(APITestCase):
    """Test project creation endpoint"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='collaborator',
            email='collab@example.com',
            password='testpass123'
        )

    def test_create_project_success(self):
        """Test successfully creating a project"""
        self.client.force_authenticate(user=self.user)
        data = {
            'project_name': 'Test Project',
            'description': 'A test project description',
            'maximum_collaborators': 3
        }
        response = self.client.post('/api/projects/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['project_name'], 'Test Project')
        self.assertEqual(response.data['description'], 'A test project description')
        self.assertEqual(response.data['maximum_collaborators'], 3)
        self.assertEqual(response.data['owner']['username'], 'owner')
        self.assertFalse(response.data['completed'])

    def test_create_project_with_collaborators(self):
        """Test creating project with initial collaborators"""
        self.client.force_authenticate(user=self.user)
        data = {
            'project_name': 'Team Project',
            'description': 'Project with collaborators',
            'maximum_collaborators': 2,
            'collaborators': ['collaborator']
        }
        response = self.client.post('/api/projects/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project = Project.objects.get(id=response.data['id'])
        self.assertIn(self.other_user, project.contributors.all())

    def test_create_project_unauthenticated(self):
        """Test creating project without authentication fails"""
        data = {
            'project_name': 'Test Project',
            'description': 'Description',
            'maximum_collaborators': 1
        }
        response = self.client.post('/api/projects/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_project_missing_required_fields(self):
        """Test creating project without required fields fails"""
        self.client.force_authenticate(user=self.user)
        data = {'description': 'Only description'}
        response = self.client.post('/api/projects/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_project_invalid_collaborator(self):
        """Test creating project with nonexistent collaborator"""
        self.client.force_authenticate(user=self.user)
        data = {
            'project_name': 'Test Project',
            'description': 'Description',
            'maximum_collaborators': 2,
            'collaborators': ['nonexistent_user']
        }
        # Should still create project but skip invalid collaborator
        response = self.client.post('/api/projects/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project = Project.objects.get(id=response.data['id'])
        self.assertEqual(project.contributors.count(), 0)


class ProjectListTests(APITestCase):
    """Test project listing endpoints"""

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='u1@example.com', password='pass')
        self.user2 = User.objects.create_user(username='user2', email='u2@example.com', password='pass')
        
        # Create projects
        self.project1 = Project.objects.create(
            project_name='Project 1',
            description='First project',
            owner=self.user1,
            maximum_collaborators=2
        )
        self.project2 = Project.objects.create(
            project_name='Project 2',
            description='Second project',
            owner=self.user2,
            maximum_collaborators=1
        )
        self.project3 = Project.objects.create(
            project_name='Project 3',
            description='Third project',
            owner=self.user1,
            maximum_collaborators=3,
            completed=True
        )

    def test_list_projects_unauthenticated(self):
        """Test listing projects without authentication (should work)"""
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_list_projects_authenticated(self):
        """Test listing projects with authentication"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_retrieve_project_unauthenticated(self):
        """Test retrieving single project without authentication (should work)"""
        response = self.client.get(f'/api/projects/{self.project1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['project_name'], 'Project 1')

    def test_retrieve_project_authenticated(self):
        """Test retrieving single project with authentication"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/projects/{self.project1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['project_name'], 'Project 1')
        self.assertEqual(response.data['owner']['username'], 'user1')

    def test_retrieve_nonexistent_project(self):
        """Test retrieving nonexistent project"""
        response = self.client.get('/api/projects/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OpenProjectsTests(APITestCase):
    """Test open projects endpoint"""

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='u1@example.com', password='pass')
        self.user2 = User.objects.create_user(username='user2', email='u2@example.com', password='pass')
        self.user3 = User.objects.create_user(username='user3', email='u3@example.com', password='pass')
        
        # Project with open seats
        self.open_project = Project.objects.create(
            project_name='Open Project',
            description='Has open seats',
            owner=self.user1,
            maximum_collaborators=3
        )
        
        # Project with full seats
        self.full_project = Project.objects.create(
            project_name='Full Project',
            description='No open seats',
            owner=self.user1,
            maximum_collaborators=2
        )
        self.full_project.contributors.add(self.user2, self.user3)
        
        # Project with one open seat
        self.partial_project = Project.objects.create(
            project_name='Partial Project',
            description='One open seat',
            owner=self.user1,
            maximum_collaborators=2
        )
        self.partial_project.contributors.add(self.user2)

    def test_get_open_projects_unauthenticated(self):
        """Test getting open projects without authentication (should work)"""
        response = self.client.get('/api/projects/open/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project_names = [p['project_name'] for p in response.data]
        self.assertIn('Open Project', project_names)
        self.assertIn('Partial Project', project_names)
        self.assertNotIn('Full Project', project_names)

    def test_get_open_projects_authenticated(self):
        """Test getting open projects with authentication"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/projects/open/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return projects with available seats
        for project in response.data:
            project_obj = Project.objects.get(id=project['id'])
            self.assertLess(project_obj.contributors.count(), project_obj.maximum_collaborators)


class ProjectCompleteTests(APITestCase):
    """Test project completion endpoint"""

    def setUp(self):
        self.owner = User.objects.create_user(username='owner', email='owner@example.com', password='pass')
        self.other_user = User.objects.create_user(username='other', email='other@example.com', password='pass')
        self.project = Project.objects.create(
            project_name='Test Project',
            description='Description',
            owner=self.owner,
            maximum_collaborators=2
        )

    def test_complete_project_success(self):
        """Test successfully completing a project"""
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f'/api/projects/{self.project.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertTrue(self.project.completed)

    def test_complete_project_unauthenticated(self):
        """Test completing project without authentication fails"""
        response = self.client.post(f'/api/projects/{self.project.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_complete_project_not_owner(self):
        """Test completing project as non-owner fails"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(f'/api/projects/{self.project.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_complete_already_completed_project(self):
        """Test completing an already completed project"""
        self.project.completed = True
        self.project.save()
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f'/api/projects/{self.project.id}/complete/')
        # Should still return success (idempotent)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProjectDeleteTests(APITestCase):
    """Test project deletion endpoint"""

    def setUp(self):
        self.owner = User.objects.create_user(username='owner', email='owner@example.com', password='pass')
        self.other_user = User.objects.create_user(username='other', email='other@example.com', password='pass')
        self.project = Project.objects.create(
            project_name='Test Project',
            description='Description',
            owner=self.owner,
            maximum_collaborators=2
        )

    def test_delete_project_success(self):
        """Test successfully deleting a project"""
        self.client.force_authenticate(user=self.owner)
        project_id = self.project.id
        response = self.client.delete(f'/api/projects/{project_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(id=project_id).exists())

    def test_delete_project_unauthenticated(self):
        """Test deleting project without authentication fails"""
        response = self.client.delete(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_project_not_owner(self):
        """Test deleting project as non-owner fails"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_delete_nonexistent_project(self):
        """Test deleting nonexistent project"""
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete('/api/projects/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)




