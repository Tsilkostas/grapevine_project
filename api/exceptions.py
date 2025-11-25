"""
Custom exceptions for the Greapevine Collaborator Finder API.

These exceptions extend DRF's APIException to provide domain-specific
error handling with consistent error messages and HTTP status codes.
All exceptions return 400 Bad Request status codes as they represent
client errors (invalid requests or business rule violations).
"""
from rest_framework.exceptions import APIException
from rest_framework import status


class MaxSkillsExceeded(APIException):
    """
    Exception raised when user tries to add more than 3 skills.
    
    Business rule: Users can have a maximum of 3 skills at any time.
    This exception is raised when attempting to add a 4th skill.
    
    Status Code: 400 Bad Request
    Error Code: 'max_skills_exceeded'
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Maximum of 3 skills allowed per user'
    default_code = 'max_skills_exceeded'


class ProjectFullException(APIException):
    """
    Exception raised when a project has no available seats for contributors.
    
    Business rule: Projects have a maximum number of collaborators.
    This exception is raised when:
    - User tries to express interest in a full project
    - Owner tries to accept interest when project is full
    
    Status Code: 400 Bad Request
    Error Code: 'project_full'
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'No seats available for this project'
    default_code = 'project_full'


class InterestAlreadyExpressed(APIException):
    """
    Exception raised when user tries to express interest in a project twice.
    
    Business rule: A user can only express interest once per project.
    This is enforced by the unique_together constraint on (user, project).
    
    Status Code: 400 Bad Request
    Error Code: 'interest_already_expressed'
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'You have already expressed interest in this project'
    default_code = 'interest_already_expressed'


class InterestAlreadyHandled(APIException):
    """
    Exception raised when trying to accept/decline an already processed interest.
    
    Business rule: Once an interest is accepted or declined, it cannot be
    processed again. Only 'pending' interests can be accepted or declined.
    
    Status Code: 400 Bad Request
    Error Code: 'interest_already_handled'
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'This interest has already been handled'
    default_code = 'interest_already_handled'

