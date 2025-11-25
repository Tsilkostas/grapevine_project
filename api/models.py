"""
Django models for the Greapevine Collaborator Finder API.

This module defines the core data models:
- User: Extended user model with additional profile fields
- Skill: Programming language skills available in the system
- UserSkill: Association between users and their skills with proficiency levels
- Project: Open-source projects that users can create and contribute to
- ProjectInterest: Tracks user interest in projects (pending/accepted/declined)
"""
from django.conf import settings
from django.db import models
from django.db.models import Count, F
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Extended user model with additional profile information.
    
    Extends Django's AbstractUser to add fields required by the API:
    - age: User's age (optional)
    - country: User's country (optional)
    - residence: User's city/residence (optional)
    
    The base AbstractUser provides: username, email, password, first_name, last_name.
    
    Attributes:
        age (PositiveIntegerField): User's age, optional field
        country (CharField): User's country, optional field
        residence (CharField): User's city or residence, optional field
    """
    age = models.PositiveIntegerField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    residence = models.CharField(max_length=100, blank=True)


class Skill(models.Model):
    """
    Programming language skill model.
    
    Represents the programming languages that users can add to their profile.
    Only the 8 specified languages are supported as per requirements.
    
    Attributes:
        name (CharField): The programming language code (e.g., 'py', 'js', 'cpp')
                         Must be one of the LANG_CHOICES, unique constraint enforced
        
    Choices:
        LANG_CHOICES: Tuple of (code, display_name) for supported languages:
            - cpp: C++
            - js: Javascript
            - py: Python
            - java: Java
            - lua: Lua
            - rust: Rust
            - go: Go
            - julia: Julia
    """
    # Supported programming languages as per requirements
    LANG_CHOICES = [
        ('cpp', 'C++'),
        ('js', 'Javascript'),
        ('py', 'Python'),
        ('java', 'Java'),
        ('lua', 'Lua'),
        ('rust', 'Rust'),
        ('go', 'Go'),
        ('julia', 'Julia'),
    ]

    # Unique constraint ensures each language exists only once in the database
    name = models.CharField(max_length=20, choices=LANG_CHOICES, unique=True)

    def __str__(self):
        """
        Return the human-readable name of the programming language.
        
        Returns:
            str: Display name of the language (e.g., "Python" instead of "py")
        """
        return dict(self.LANG_CHOICES).get(self.name, self.name)


class UserSkill(models.Model):
    """
    Association model linking users to their programming language skills.
    
    Represents a user's proficiency level in a specific programming language.
    Each user can have up to 3 skills (enforced at the view level).
    A user cannot have the same skill twice (enforced by unique_together constraint).
    
    Attributes:
        user (ForeignKey): Reference to the User who has this skill
        skill (ForeignKey): Reference to the Skill (programming language)
        level (CharField): Proficiency level - beginner, experienced, or expert
        
    Constraints:
        unique_together: Ensures a user cannot add the same skill twice
        
    Related Names:
        - user.user_skills: Access all skills for a user
        - skill.user_skills: Access all users who have this skill
    """
    # Proficiency levels as per requirements
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('experienced', 'Experienced'),
        ('expert', 'Expert'),
    ]

    # CASCADE delete: If user is deleted, their skills are deleted too
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='user_skills'
    )
    # CASCADE delete: If skill is deleted, all user associations are deleted
    skill = models.ForeignKey(
        Skill, 
        on_delete=models.CASCADE, 
        related_name='user_skills'
    )
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)

    class Meta:
        # Prevents duplicate skills for the same user
        # Enforced at database level for data integrity
        unique_together = ('user', 'skill')


class ProjectQuerySet(models.QuerySet):
    """Custom queryset methods for Project model."""
    
    def with_available_seats(self):
        """
        Filter projects that have available seats for contributors.
        
        A project has available seats if:
        - Number of contributors < maximum_collaborators
        - Project is not completed
        """
        return self.annotate(
            contributor_count=Count('contributors')
        ).filter(
            contributor_count__lt=F('maximum_collaborators'),
            completed=False
        )
    
    def open_projects(self):
        """Alias for with_available_seats - more readable."""
        return self.with_available_seats()
    
    def for_owner(self, user):
        """Filter projects owned by a specific user."""
        return self.filter(owner=user)


class ProjectManager(models.Manager):
    """Custom manager for Project model."""
    
    def get_queryset(self):
        return ProjectQuerySet(self.model, using=self._db)
    
    def with_available_seats(self):
        """Get projects with available seats."""
        return self.get_queryset().with_available_seats()
    
    def open_projects(self):
        """Get open projects (alias for with_available_seats)."""
        return self.get_queryset().open_projects()
    
    def for_owner(self, user):
        """Get projects for a specific owner."""
        return self.get_queryset().for_owner(user)


class Project(models.Model):
    """
    Open-source project model.
    
    Represents a project that users can create and collaborate on.
    Projects have a maximum number of collaborators and track completion status.
    
    Attributes:
        project_name (CharField): Name of the project (required)
        description (TextField): Detailed description of the project (optional)
        owner (ForeignKey): User who created the project (required)
        maximum_collaborators (PositiveIntegerField): Maximum number of contributors allowed
        contributors (ManyToManyField): Users who are contributing to the project
        completed (BooleanField): Whether the project is marked as completed
        created_at (DateTimeField): Timestamp when project was created (auto-set)
        
    Related Names:
        - owner.owned_projects: All projects created by a user
        - contributor.contributed_projects: All projects a user contributes to
        - project.interests: All ProjectInterest objects for this project
    """
    project_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # CASCADE: If owner is deleted, their projects are deleted
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='owned_projects'
    )
    
    # Default is 1 (just the owner), but can be increased
    maximum_collaborators = models.PositiveIntegerField(default=1)
    
    # Many-to-many: A project can have multiple contributors, a user can contribute to multiple projects
    # blank=True allows projects with no contributors initially
    contributors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='contributed_projects', 
        blank=True
    )
    
    # Track project completion status
    completed = models.BooleanField(default=False)
    
    # Automatically set when project is created
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Use custom manager
    objects = ProjectManager()

    def __str__(self):
        """Return the project name for string representation."""
        return self.project_name
    
    def is_full(self):
        """Check if project has reached maximum collaborator limit."""
        return self.contributors.count() >= self.maximum_collaborators
    
    def has_available_seats(self):
        """Check if project has available seats for contributors."""
        return not self.is_full() and not self.completed
    
    def is_owner(self, user):
        """Check if user is the project owner."""
        return self.owner == user
    
    def get_available_seats(self):
        """Get number of available seats."""
        return max(0, self.maximum_collaborators - self.contributors.count())


class ProjectInterest(models.Model):
    """
    Tracks user interest in projects.
    
    Represents a user's expression of interest to contribute to a project.
    The project owner can accept or decline the interest.
    A user can only express interest once per project (enforced by unique_together).
    
    Attributes:
        user (ForeignKey): User who expressed interest
        project (ForeignKey): Project the user is interested in
        expressed_at (DateTimeField): When the interest was expressed (auto-set)
        status (CharField): Current status - pending, accepted, or declined
        
    Status Flow:
        - pending: Initial state when user expresses interest
        - accepted: Owner accepted the interest, user becomes contributor
        - declined: Owner declined the interest
        
    Constraints:
        unique_together: Prevents duplicate interest expressions from same user for same project
        
    Related Names:
        - user.interests: All projects a user has expressed interest in
        - project.interests: All users who expressed interest in this project
    """
    # CASCADE: If user is deleted, their interests are deleted
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='interests'
    )
    # CASCADE: If project is deleted, all interests are deleted
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='interests'
    )
    
    # Automatically set when interest is first created
    expressed_at = models.DateTimeField(auto_now_add=True)
    
    # Status choices for interest workflow
    STATUS_CHOICES = [
        ('pending', 'Pending'),      # Waiting for owner's decision
        ('accepted', 'Accepted'),    # Owner accepted, user becomes contributor
        ('declined', 'Declined'),    # Owner declined the interest
    ]
    
    # Default to pending when interest is first expressed
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        # Prevents user from expressing interest in the same project multiple times
        # Enforced at database level for data integrity
        unique_together = ('user', 'project')
    
    def is_pending(self):
        """Check if interest is in pending status."""
        return self.status == 'pending'
    
    def can_be_handled(self):
        """Check if interest can be accepted or declined."""
        return self.is_pending()
    
    def accept(self):
        """
        Accept the interest and add user as contributor.
        
        Raises:
            InterestAlreadyHandled: If interest is not in pending status
            ProjectFullException: If project has no available seats
        """
        from .exceptions import InterestAlreadyHandled, ProjectFullException
        
        if not self.can_be_handled():
            raise InterestAlreadyHandled()
        
        if self.project.is_full():
            raise ProjectFullException()
        
        self.status = 'accepted'
        self.save()
        self.project.contributors.add(self.user)
    
    def decline(self):
        """
        Decline the interest.
        
        Raises:
            InterestAlreadyHandled: If interest is not in pending status
        """
        from .exceptions import InterestAlreadyHandled
        
        if not self.can_be_handled():
            raise InterestAlreadyHandled()
        
        self.status = 'declined'
        self.save()
