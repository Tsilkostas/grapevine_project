"""
Django Admin configuration for the Greapevine Collaborator Finder API.

This module registers all models with Django's admin interface, allowing
administrators to manage users, skills, projects, and interests through
the Django admin panel.

Admin classes customize how models appear in the admin interface:
- list_display: Fields shown in the list view
- search_fields: Fields searchable in admin (can be added)
- list_filter: Filters available in sidebar (can be added)
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Skill, UserSkill, Project, ProjectInterest


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for User model.
    
    Extends Django's built-in UserAdmin to provide user management
    functionality in the admin panel. Includes all standard user fields
    plus custom fields (age, country, residence).
    """
    pass


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """
    Admin interface for Skill model.
    
    Displays programming language skills in the admin panel.
    
    List Display:
        - name: Programming language name
    """
    list_display = ('name',)


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    """
    Admin interface for UserSkill model.
    
    Displays user-skill associations with proficiency levels.
    
    List Display:
        - user: User who has the skill
        - skill: Programming language
        - level: Proficiency level (beginner/experienced/expert)
    """
    list_display = ('user', 'skill', 'level')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Admin interface for Project model.
    
    Displays projects with key information for administration.
    
    List Display:
        - project_name: Name of the project
        - owner: User who created the project
        - maximum_collaborators: Maximum number of contributors
        - created_at: When the project was created
    """
    list_display = ('project_name', 'owner', 'maximum_collaborators', 'created_at')


@admin.register(ProjectInterest)
class ProjectInterestAdmin(admin.ModelAdmin):
    """
    Admin interface for ProjectInterest model.
    
    Displays interest expressions for projects.
    
    List Display:
        - user: User who expressed interest
        - project: Project they're interested in
        - expressed_at: When interest was expressed
    """
    list_display = ('user', 'project', 'expressed_at')
