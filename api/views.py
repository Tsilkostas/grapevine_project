"""
API Views for the Greapevine Collaborator Finder API.

This module contains all the view classes that handle HTTP requests:
- Authentication views (registration, login, password reset)
- Skill management views (add/remove skills)
- Project management views (CRUD operations, interest handling)
- Statistics view (user statistics)

All views use Django REST Framework for request/response handling and include
proper error handling, authentication, and authorization.
"""
from rest_framework import generics, status, viewsets
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import NotFound, PermissionDenied, PermissionDenied
from django.shortcuts import get_object_or_404

from django.contrib.auth import get_user_model
from .models import Project, ProjectInterest
from .permissions import IsProjectOwner
from .services import SkillService, ProjectInterestService
from .constants import MESSAGES
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    UserSkillSerializer,
    ProjectSerializer,
    ProjectInterestSerializer,
    ResetPasswordSerializer,
    SkillRemoveSerializer,
    StatsSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    Register a new user account and receive an authentication token.
    
    Username must be unique. Returns user profile data with authentication token.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]  # Public endpoint - anyone can register

    def create(self, request, *args, **kwargs):
        """Create a new user account and return authentication token."""
        # Validate and deserialize input data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user (password is hashed in serializer)
        user = serializer.save()
        
        # Get or create authentication token for the new user
        # Token is used for subsequent authenticated requests
        token, _ = Token.objects.get_or_create(user=user)
        
        # Serialize user data and add token
        data = UserSerializer(user).data
        data['token'] = token.key
        
        return Response(data, status=status.HTTP_201_CREATED)


class ResetPasswordView(APIView):
    """
    Reset user password using email address.
    
    If multiple users share the same email, the first match will be reset.
    """
    permission_classes = [AllowAny]  # Public endpoint
    serializer_class = ResetPasswordSerializer

    @extend_schema(request=ResetPasswordSerializer, responses={200: None})
    def post(self, request):
        """Reset user password by email address."""
        # Validate input data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        new_password = serializer.validated_data['new_password']
        
        # Get first user with this email (handles both single and multiple)
        user = User.objects.filter(email=email).order_by('id').first()
        
        if not user:
            raise NotFound('User with this email not found')
        
        user.set_password(new_password)
        user.save()
        
        return Response({'detail': MESSAGES['password_reset']}, status=status.HTTP_200_OK)


class CustomObtainAuthToken(ObtainAuthToken):
    """
    Authenticate user credentials and receive an authentication token.
    
    Returns only the token string for use in subsequent API requests.
    """
    def post(self, request, *args, **kwargs):
        """Authenticate user and return token."""
        # Use parent class to handle authentication
        resp = super().post(request, *args, **kwargs)
        
        # Extract token and return simplified response
        token = Token.objects.get(key=resp.data['token'])
        return Response({'token': token.key})


class SkillAddView(APIView):
    """
    Add a programming language skill to your profile.
    
    Maximum 3 skills per user. Duplicate skills are not allowed.
    Supported languages: cpp, js, py, java, lua, rust, go, julia
    Skill levels: beginner, experienced, expert
    """
    permission_classes = [IsAuthenticated]  # User must be logged in
    serializer_class = UserSkillSerializer

    @extend_schema(request=UserSkillSerializer, responses={201: None})
    def post(self, request):
        """Add a skill to the authenticated user's profile."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        skill_name = serializer.validated_data['skill']
        level = serializer.validated_data['level']
        
        SkillService.add_skill_to_user(request.user, skill_name, level)
        
        return Response({'detail': MESSAGES['skill_added']}, status=status.HTTP_201_CREATED)


class SkillRemoveView(APIView):
    """Remove a skill from your profile."""
    permission_classes = [IsAuthenticated]  # User must be logged in
    serializer_class = SkillRemoveSerializer

    @extend_schema(request=SkillRemoveSerializer, responses={200: None})
    def post(self, request):
        """Remove a skill from the authenticated user's profile."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        skill_name = serializer.validated_data['skill']
        SkillService.remove_skill_from_user(request.user, skill_name)
        
        return Response({'detail': MESSAGES['skill_removed']}, status=status.HTTP_200_OK)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    Project CRUD operations and interest management.
    
    Public endpoints: list, retrieve, open
    Owner-only endpoints: update, delete, complete, pending_interests, accept_interest, decline_interest
    """
    queryset = Project.objects.all().order_by('-created_at')  # Newest first
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]  # Default: require authentication
    
    def get_queryset(self):
        """Optimize queryset with select_related and prefetch_related."""
        queryset = super().get_queryset()
        if self.action in ['list', 'retrieve', 'open']:
            return queryset.select_related('owner').prefetch_related('contributors')
        return queryset

    def perform_create(self, serializer):
        """Create a new project with authenticated user as owner. Add collaborators if provided."""
        # Get optional collaborators list from request data
        # This is not part of the model, so it's handled separately
        collaborators = self.request.data.get('collaborators', [])
        
        # Save project with authenticated user as owner
        project = serializer.save(owner=self.request.user)
        
        if collaborators:
            # Performance optimization: Get all valid users in a single query
            # instead of querying one by one in a loop
            # Invalid usernames are automatically filtered out
            valid_users = User.objects.filter(username__in=collaborators)
            project.contributors.add(*valid_users)

    def get_permissions(self):
        """Dynamic permissions based on action."""
        if self.action in ['list', 'retrieve', 'open']:
            return [AllowAny()]
        # For update/partial_update/destroy, use IsProjectOwner permission
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsProjectOwner()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def open(self, request):
        """
        Get all projects with available seats for contributors.
        
        Returns projects where contributor count < maximum_collaborators and project is not completed.
        Public access.
        """
        open_projects = Project.objects.with_available_seats().select_related('owner').prefetch_related('contributors')
        serializer = self.get_serializer(open_projects, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def interest(self, request, pk=None):
        """
        Express interest in contributing to a project.
        
        Requires available seats. Project owner must accept before becoming a contributor.
        Cannot express interest twice in the same project.
        """
        project = get_object_or_404(Project, pk=pk)
        ProjectInterestService.express_interest(request.user, project)
        
        return Response({'detail': MESSAGES['interest_registered']}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    @extend_schema(responses={200: ProjectInterestSerializer(many=True)})
    def pending_interests(self, request, pk=None):
        """
        View pending interests for a project (owner only).
        
        Returns username, email, and skills only (privacy compliant).
        Sensitive fields (first_name, last_name, age, country, residence) are not included.
        """
        project = get_object_or_404(Project, pk=pk)
        
        # Check permission explicitly
        if not project.is_owner(request.user):
            raise PermissionDenied('Only the project owner can view pending interests')
        
        qs = project.interests.filter(status='pending').select_related('user').prefetch_related('user__user_skills__skill')
        serializer = ProjectInterestSerializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(parameters=[OpenApiParameter('interest_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)])
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='interest/(?P<interest_id>[^/.]+)/accept')
    def accept_interest(self, request, pk=None, interest_id=None):
        """
        Accept a pending interest and add user as contributor (owner only).
        
        Project must have available seats. Interest must be in 'pending' status.
        """
        project = get_object_or_404(Project, pk=pk)
        interest = get_object_or_404(ProjectInterest, pk=interest_id, project=project)
        
        # Check permission explicitly
        if not project.is_owner(request.user):
            raise PermissionDenied('Only the project owner can accept interests')
        
        interest.accept()
        
        return Response({'detail': MESSAGES['interest_accepted']}, status=status.HTTP_200_OK)

    @extend_schema(parameters=[OpenApiParameter('interest_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)])
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='interest/(?P<interest_id>[^/.]+)/decline')
    def decline_interest(self, request, pk=None, interest_id=None):
        """
        Decline a pending interest (owner only).
        
        User is not added as contributor. Interest must be in 'pending' status.
        """
        project = get_object_or_404(Project, pk=pk)
        interest = get_object_or_404(ProjectInterest, pk=interest_id, project=project)
        
        # Check permission explicitly
        if not project.is_owner(request.user):
            raise PermissionDenied('Only the project owner can decline interests')
        
        interest.decline()
        
        return Response({'detail': MESSAGES['interest_declined']}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        """
        Mark a project as completed (owner only).
        
        Completed projects are excluded from the open projects list. Idempotent operation.
        """
        project = get_object_or_404(Project, pk=pk)
        
        # Check permission explicitly
        if not project.is_owner(request.user):
            raise PermissionDenied('Only the project owner can mark the project as completed')
        
        project.completed = True
        project.save()
        
        return Response({'detail': MESSAGES['project_completed']}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a project permanently (owner only).
        
        Warning: This action is irreversible. All project data and related records will be deleted.
        """
        project = self.get_object()
        
        # Check permission explicitly
        if not project.is_owner(request.user):
            raise PermissionDenied('Only the project owner can delete the project')
        
        return super().destroy(request, *args, **kwargs)


class StatsView(APIView):
    """
    Get your project statistics.
    
    Returns number of projects created and contributed to.
    Only counts actual contributions (not pending interests).
    """
    permission_classes = [IsAuthenticated]  # User must be logged in
    serializer_class = StatsSerializer

    @extend_schema(
        operation_id='user_stats',
        summary='Get user statistics',
        description='Returns the number of projects created and contributed to by the authenticated user. Only counts actual contributions (not pending interests).',
        responses={200: StatsSerializer},
        tags=['Users']
    )
    def get(self, request):
        """Get statistics for the authenticated user."""
        user = request.user
        
        data = {
            'projects_created': user.owned_projects.count(),
            'projects_contributed': user.contributed_projects.count(),
        }
        
        return Response(data)

