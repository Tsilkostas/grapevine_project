"""
Custom permission classes for the Greapevine Collaborator Finder API.

These permissions provide reusable authorization logic across views.
"""
from rest_framework import permissions


class IsProjectOwner(permissions.BasePermission):
    """
    Permission check to ensure user is the project owner.
    
    Used for operations that require project ownership such as:
    - Updating/deleting projects
    - Marking projects as completed
    - Viewing/managing pending interests
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if the authenticated user is the owner of the project."""
        return obj.owner == request.user


class IsProjectOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access to everyone, write access to owners only.
    
    Useful for endpoints where anyone can view but only owners can modify.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission for the view."""
        # Read permissions for all users
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions require authentication
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission for the object."""
        # Read permissions for all users
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only for project owners
        return obj.owner == request.user

