"""
Service layer for business logic in the Greapevine Collaborator Finder API.

This module contains service classes that encapsulate business logic,
separating it from views and making it reusable and testable.
"""
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework.exceptions import NotFound, ValidationError

from .models import Project, ProjectInterest, Skill, UserSkill
from .exceptions import (
    MaxSkillsExceeded,
    ProjectFullException,
    InterestAlreadyExpressed,
    InterestAlreadyHandled,
)
from .constants import MAX_SKILLS_PER_USER

User = get_user_model()


class SkillService:
    """Service class for skill-related business logic."""
    
    @staticmethod
    def add_skill_to_user(user, skill_name, level):
        """
        Add a skill to user's profile with validation.
        
        Args:
            user: User instance to add skill to
            skill_name: Programming language code (e.g., 'py', 'js')
            level: Proficiency level ('beginner', 'experienced', 'expert')
            
        Raises:
            MaxSkillsExceeded: If user already has 3 skills
            ValidationError: If skill is already added
        """
        # Check max skills
        if UserSkill.objects.filter(user=user).count() >= MAX_SKILLS_PER_USER:
            raise MaxSkillsExceeded()
        
        # Get or create skill
        skill, _ = Skill.objects.get_or_create(name=skill_name)
        
        # Create user-skill association
        try:
            UserSkill.objects.create(user=user, skill=skill, level=level)
        except IntegrityError:
            raise ValidationError({
                'skill': 'This skill has already been added to your profile'
            })
    
    @staticmethod
    def remove_skill_from_user(user, skill_name):
        """
        Remove a skill from user's profile.
        
        Args:
            user: User instance to remove skill from
            skill_name: Programming language code to remove
            
        Raises:
            NotFound: If skill doesn't exist or is not associated with user
        """
        try:
            skill = Skill.objects.get(name=skill_name)
        except Skill.DoesNotExist:
            raise NotFound('Skill not found')
        
        deleted_count, _ = UserSkill.objects.filter(user=user, skill=skill).delete()
        
        if deleted_count == 0:
            raise NotFound('This skill is not associated with your profile')


class ProjectInterestService:
    """Service class for project interest-related business logic."""
    
    @staticmethod
    def express_interest(user, project):
        """
        Express interest in a project.
        
        Args:
            user: User expressing interest
            project: Project to express interest in
            
        Returns:
            ProjectInterest: Created interest instance
            
        Raises:
            InterestAlreadyExpressed: If user already expressed interest
            ProjectFullException: If project has no available seats
        """
        # Check if already expressed
        if ProjectInterest.objects.filter(user=user, project=project).exists():
            raise InterestAlreadyExpressed()
        
        # Check if project is full
        if project.is_full():
            raise ProjectFullException()
        
        # Create interest
        return ProjectInterest.objects.create(user=user, project=project)

