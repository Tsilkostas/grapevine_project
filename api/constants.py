"""
Constants used throughout the Greapevine Collaborator Finder API.

Centralizes configuration values and messages for easy maintenance.
"""

# Skill management
MAX_SKILLS_PER_USER = 3

# Supported programming languages
SUPPORTED_LANGUAGES = [
    'cpp', 'js', 'py', 'java', 'lua', 'rust', 'go', 'julia'
]

# Skill levels
SKILL_LEVELS = ['beginner', 'experienced', 'expert']

# Interest statuses
INTEREST_STATUS_PENDING = 'pending'
INTEREST_STATUS_ACCEPTED = 'accepted'
INTEREST_STATUS_DECLINED = 'declined'

# Response messages
MESSAGES = {
    'skill_added': 'Skill added successfully',
    'skill_removed': 'Skill removed successfully',
    'project_created': 'Project created successfully',
    'project_completed': 'Project marked as completed',
    'project_deleted': 'Project deleted successfully',
    'interest_registered': 'Interest registered successfully',
    'interest_accepted': 'Interest accepted successfully',
    'interest_declined': 'Interest declined successfully',
    'password_reset': 'Password reset successful',
}

