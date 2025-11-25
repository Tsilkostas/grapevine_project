"""
URL configuration for the Greapevine Collaborator Finder API.

Defines all API endpoints and their corresponding view classes.
Uses Django REST Framework's DefaultRouter for ViewSet endpoints.

API Endpoints:
    Authentication:
        - POST /api/auth/register/ - User registration
        - POST /api/auth/login/ - User login (get token)
        - POST /api/auth/reset-password/ - Password reset
    
    Skills:
        - POST /api/skills/add/ - Add skill to profile
        - POST /api/skills/remove/ - Remove skill from profile
    
    Projects (via ViewSet):
        - GET /api/projects/ - List all projects
        - POST /api/projects/ - Create project
        - GET /api/projects/{id}/ - Get project details
        - PUT/PATCH /api/projects/{id}/ - Update project
        - DELETE /api/projects/{id}/ - Delete project
        - GET /api/projects/open/ - Get projects with available seats
        - POST /api/projects/{id}/interest/ - Express interest
        - GET /api/projects/{id}/pending_interests/ - View pending interests
        - POST /api/projects/{id}/interest/{id}/accept/ - Accept interest
        - POST /api/projects/{id}/interest/{id}/decline/ - Decline interest
        - POST /api/projects/{id}/complete/ - Mark project complete
    
    Statistics:
        - GET /api/users/me/stats/ - Get user statistics
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    ResetPasswordView,
    CustomObtainAuthToken,
    SkillAddView,
    SkillRemoveView,
    ProjectViewSet,
    StatsView,
)

# DefaultRouter automatically creates standard CRUD endpoints for ViewSets
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', CustomObtainAuthToken.as_view(), name='login'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    
    # Skill management endpoints
    path('skills/add/', SkillAddView.as_view(), name='skill-add'),
    path('skills/remove/', SkillRemoveView.as_view(), name='skill-remove'),
    
    # User statistics endpoint
    path('users/me/stats/', StatsView.as_view(), name='user-stats'),
    
    # Project endpoints (from ViewSet - includes CRUD + custom actions)
    path('', include(router.urls)),
]
