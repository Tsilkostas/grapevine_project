from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from api.models import Project, Skill, ProjectInterest

User = get_user_model()


class InterestFlowTests(APITestCase):
    def setUp(self):
        # create users
        self.owner = User.objects.create_user(username='owner', password='pw')
        self.alice = User.objects.create_user(username='alice', password='pw', email='alice@example.com')
        # create project
        self.project = Project.objects.create(project_name='Test', owner=self.owner, maximum_collaborators=1)

    def test_express_interest_and_accept(self):
        # alice authenticate using DRF client
        self.client.force_authenticate(user=self.alice)
        resp = self.client.post(f'/api/projects/{self.project.pk}/interest/')
        self.assertEqual(resp.status_code, 201)
        interest = ProjectInterest.objects.get(user=self.alice, project=self.project)
        self.assertEqual(interest.status, 'pending')

        # owner accepts
        self.client.force_authenticate(user=self.owner)
        resp = self.client.post(f'/api/projects/{self.project.pk}/interest/{interest.pk}/accept/')
        self.assertEqual(resp.status_code, 200)
        interest.refresh_from_db()
        self.assertEqual(interest.status, 'accepted')
        self.assertIn(self.alice, self.project.contributors.all())

    def test_owner_cannot_accept_when_no_seats(self):
        # Express interest first (before project is full)
        self.client.force_authenticate(user=self.alice)
        resp = self.client.post(f'/api/projects/{self.project.pk}/interest/')
        self.assertEqual(resp.status_code, 201)
        interest = ProjectInterest.objects.get(user=self.alice, project=self.project)
        
        # Now fill the seat
        self.project.contributors.add(self.owner)
        
        # Owner tries to accept but should fail because no seats available
        self.client.force_authenticate(user=self.owner)
        resp = self.client.post(f'/api/projects/{self.project.pk}/interest/{interest.pk}/accept/')
        self.assertEqual(resp.status_code, 400)
