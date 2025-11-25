"""
Serializers for the Greapevine Collaborator Finder API.

Serializers handle conversion between Python objects and JSON, including:
- Input validation
- Data transformation
- Nested object serialization
- Privacy constraints (limiting visible fields)

All serializers use Django REST Framework's ModelSerializer or Serializer
base classes for consistent behavior and validation.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Skill, UserSkill, Project, ProjectInterest

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User profile data. Password is never included in responses."""
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'age', 'country', 'residence')


class RegisterSerializer(serializers.ModelSerializer):
    """
    User registration with password hashing.
    
    Required: username (unique), email, password
    Optional: first_name, last_name, age, country, residence
    Password is write-only and automatically hashed.
    """
    # Password is write-only: accepted in input but never returned in output
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'age', 'country', 'residence')

    def create(self, validated_data):
        """Create a new user with hashed password."""
        # Extract password before creating user (password is not a model field)
        password = validated_data.pop('password')
        
        # Create user with all other fields
        user = User(**validated_data)
        
        # Hash password using Django's password hashing system
        # This uses PBKDF2 with SHA256 by default
        user.set_password(password)
        
        # Save user to database
        user.save()
        
        return user


class SkillSerializer(serializers.ModelSerializer):
    """Programming language skill."""
    class Meta:
        model = Skill
        fields = ('id', 'name')


class UserSkillSerializer(serializers.ModelSerializer):
    """
    Add a skill to user's profile.
    
    Skill: programming language code (e.g., 'py', 'js', 'cpp')
    Level: beginner, experienced, or expert
    """
    # Accept skill as string (language code) instead of requiring Skill object
    skill = serializers.CharField()
    
    # Validate level against allowed choices
    level = serializers.ChoiceField(choices=UserSkill.LEVEL_CHOICES)

    class Meta:
        model = UserSkill
        fields = ('skill', 'level')
    
    def validate_skill(self, value):
        """Validate that skill is one of the supported languages."""
        from .models import Skill
        supported_languages = [lang[0] for lang in Skill.LANG_CHOICES]
        if value not in supported_languages:
            raise serializers.ValidationError(
                f'Invalid skill. Supported languages: {", ".join(supported_languages)}'
            )
        return value


class ProjectSerializer(serializers.ModelSerializer):
    """
    Project with owner set automatically from authenticated user.
    
    Collaborators can be specified as a list of usernames during creation.
    Invalid usernames are silently skipped.
    """
    # Owner is read-only - set automatically from authenticated user
    owner = UserSerializer(read_only=True)
    
    # Collaborators accepted as list of usernames (strings)
    # write_only: Accepted in input but not returned in output
    # required=False: Optional field
    collaborators = serializers.ListField(
        child=serializers.CharField(), 
        write_only=True, 
        required=False
    )

    class Meta:
        model = Project
        fields = ('id', 'project_name', 'description', 'owner', 'maximum_collaborators', 'created_at', 'completed', 'collaborators')

    def create(self, validated_data):
        """Create a project instance."""
        # Remove collaborators from validated_data
        # They're not a model field, so they can't be passed to Model.objects.create()
        # Collaborators are handled in the view's perform_create() method
        validated_data.pop('collaborators', None)

        # Create the project
        # Owner may be provided via serializer.save(owner=...) in the view
        project = Project.objects.create(**validated_data)

        return project

class ApplicantSkillSerializer(serializers.ModelSerializer):
    """User skill with human-readable skill name for applicant listings."""
    # Get the human-readable skill name instead of just the code
    skill = serializers.CharField(source='skill.name')

    class Meta:
        model = UserSkill
        fields = ('skill', 'level')


class ApplicantSerializer(serializers.ModelSerializer):
    """
    Applicant information for project owners (privacy compliant).
    
    Only includes username, email, and skills. Sensitive fields excluded.
    """
    # Serialize user's skills using ApplicantSkillSerializer
    # source='user_skills' uses the related_name from UserSkill model
    skills = ApplicantSkillSerializer(source='user_skills', many=True)

    class Meta:
        model = User
        # Only include non-sensitive fields for privacy
        fields = ('id', 'username', 'email', 'skills')


class ProjectInterestSerializer(serializers.ModelSerializer):
    """Project interest record with privacy-compliant user information."""
    # Use ApplicantSerializer to respect privacy constraints
    # Only shows username, email, and skills - not other personal info
    user = ApplicantSerializer(read_only=True)

    class Meta:
        model = ProjectInterest
        fields = ('id', 'user', 'project', 'expressed_at', 'status')


class ResetPasswordSerializer(serializers.Serializer):
    """Password reset request with email and new password."""
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)


class SkillRemoveSerializer(serializers.Serializer):
    """Remove a skill by programming language code."""
    skill = serializers.CharField()


class StatsSerializer(serializers.Serializer):
    """User statistics: projects created and contributed to."""
    projects_created = serializers.IntegerField()
    projects_contributed = serializers.IntegerField()
