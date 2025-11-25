# Greapevine Collaborator Finder API

A Django REST Framework API for connecting programmers with open-source projects. Users can register, manage their programming skills, create or join projects, and collaborate with other developers.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Data Models](#data-models)
- [Business Logic & Rules](#business-logic--rules)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## Overview

The **Greapevine Collaborator Finder API** is a RESTful API built with Django and Django REST Framework. It enables:

- **User Registration & Authentication**: Token-based authentication system
- **Skill Management**: Add/remove programming language skills (max 3 per user)
- **Project Management**: Create, view, update, delete, and complete projects
- **Interest System**: Express interest in projects, with owner approval workflow
- **Statistics**: Track projects created and contributed to
- **Privacy Controls**: Limited data visibility in interest workflows

---

## Features

### ✅ Core Functionality

1. **User Authentication**
   - Registration with profile information
   - Token-based login
   - Password reset functionality

2. **Skill Management**
   - Add programming language skills (up to 3 per user)
   - Remove skills from profile
   - Support for 8 programming languages: C++, Javascript, Python, Java, Lua, Rust, Go, Julia
   - Skill levels: Beginner, Experienced, Expert

3. **Project Management**
   - Create projects with descriptions and collaborator limits
   - List all projects or filter open projects (with available seats)
   - Update and delete projects (owner only)
   - Mark projects as completed
   - Add initial collaborators during creation

4. **Interest & Collaboration Workflow**
   - Express interest in projects
   - View pending interests (project owner only)
   - Accept or decline interests
   - Automatic contributor assignment on acceptance
   - Privacy: Only username, email, and skills visible to project owners

5. **User Statistics**
   - Track number of projects created
   - Track number of projects contributed to

---

## Technology Stack

- **Python 3.8+**: Programming language
- **Django 4.2+**: Web framework
- **Django REST Framework 3.14+**: REST API framework
- **drf-spectacular 0.26+**: OpenAPI/Swagger documentation
- **SQLite**: Default database (easily switchable to PostgreSQL/MySQL)

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher**
  - Check version: `python --version` or `python3 --version`
  - Download: [python.org](https://www.python.org/downloads/)

- **pip** (Python package installer)
  - Usually comes with Python
  - Check version: `pip --version` or `pip3 --version`

- **Git** (optional, for cloning the repository)
  - Check version: `git --version`

---

## Installation & Setup

### Step 1: Clone or Download the Repository

If you have the repository URL:
```bash
git clone <repository-url>
cd Greapevine_assesement
```

Or download and extract the ZIP file to your desired location.

### Step 2: Create a Virtual Environment

A virtual environment isolates project dependencies from your system Python installation.

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Note:** Once activated, your terminal prompt should show `(.venv)` prefix.

**Troubleshooting:** If you get an error about execution policies on Windows PowerShell, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies

With your virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

This installs:
- Django (web framework)
- Django REST Framework (API framework)
- drf-spectacular (API documentation)

**Expected Output:**
```
Successfully installed Django-4.x.x djangorestframework-3.x.x drf-spectacular-0.x.x ...
```

### Step 4: Verify Installation

Check that Django is installed correctly:
```bash
python manage.py --version
```

You should see the Django version number.

---

## Database Setup

The application uses SQLite by default (no additional setup required). The database file `db.sqlite3` will be created automatically.

### Step 1: Run Migrations

Migrations create the database tables for the application:

```bash
python manage.py migrate
```

**What this does:**
- Creates the database file (`db.sqlite3`)
- Creates tables for: Users, Skills, UserSkills, Projects, ProjectInterests
- Seeds initial data (8 programming language skills)

**Expected Output:**
```
Operations to perform:
  Apply all migrations: admin, api, auth, authtoken, contenttypes, sessions
Running migrations:
  Applying api.0001_initial... OK
  Applying api.0002_add_completed_and_seed_skills... OK
  Applying api.0003_rename_project_fields... OK
  ...
```

### Step 2: Create a Superuser (Optional)

A superuser account allows you to access the Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter:
- Username
- Email address (optional)
- Password (twice)

**Admin Panel URL:** `http://127.0.0.1:8000/admin/`

---

## Running the Application

### Start the Development Server

```bash
python manage.py runserver
```

**Expected Output:**
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
Django version 4.x.x, using settings 'greapevine.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK (Windows) or CTRL-C (Linux/macOS).
```

The server is now running! Open your browser to:
- **API Base URL**: `http://127.0.0.1:8000/api/`
- **Interactive API Docs (Swagger)**: `http://127.0.0.1:8000/api/docs/`
- **Admin Panel**: `http://127.0.0.1:8000/admin/`

### Stop the Server

Press `CTRL+C` (or `CTRL+BREAK` on Windows) in the terminal where the server is running.

---

## API Documentation

### Interactive API Documentation (Swagger UI)

The easiest way to explore and test the API is through the Swagger UI interface:

**URL:** `http://127.0.0.1:8000/api/docs/`

**Features:**
- Browse all available endpoints
- View request/response schemas
- Test API endpoints directly from the browser
- See example request/response data

### API Schema (OpenAPI JSON)

**URL:** `http://127.0.0.1:8000/api/schema/`

Returns the OpenAPI schema in JSON format for use with API testing tools like Postman or Insomnia.

---

## API Endpoints

### Base URL

All API endpoints are prefixed with `/api/`

```
http://127.0.0.1:8000/api/
```

### Authentication Endpoints

#### 1. Register a New User

**Endpoint:** `POST /api/auth/register/`

**Description:** Creates a new user account and returns an authentication token.

**Authentication Required:** No (public endpoint)

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "age": 25,
  "country": "USA",
  "residence": "New York"
}
```

**Required Fields:**
- `username` (string, unique)
- `email` (string)
- `password` (string)

**Optional Fields:**
- `first_name`, `last_name`, `age`, `country`, `residence`

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "age": 25,
  "country": "USA",
  "residence": "New York",
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

**Example cURL:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

---

#### 2. Login

**Endpoint:** `POST /api/auth/login/`

**Description:** Authenticates a user and returns an authentication token.

**Authentication Required:** No (public endpoint)

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

**Example cURL:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepassword123"
  }'
```

---

#### 3. Reset Password

**Endpoint:** `POST /api/auth/reset-password/`

**Description:** Resets a user's password using their email address.

**Authentication Required:** No (public endpoint)

**Request Body:**
```json
{
  "email": "john@example.com",
  "new_password": "newsecurepassword456"
}
```

**Response (200 OK):**
```json
{
  "detail": "Password reset successful"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "User with this email not found"
}
```

---

### Skill Management Endpoints

#### 4. Add Skill to Profile

**Endpoint:** `POST /api/skills/add/`

**Description:** Adds a programming language skill to the authenticated user's profile.

**Authentication Required:** Yes (include token in header)

**Constraints:**
- Maximum 3 skills per user
- Cannot add duplicate skills
- Skill must be one of the supported languages

**Request Body:**
```json
{
  "skill": "py",
  "level": "experienced"
}
```

**Supported Languages:**
- `cpp` - C++
- `js` - Javascript
- `py` - Python
- `java` - Java
- `lua` - Lua
- `rust` - Rust
- `go` - Go
- `julia` - Julia

**Skill Levels:**
- `beginner`
- `experienced`
- `expert`

**Response (201 Created):**
```json
{
  "id": 1,
  "user": 1,
  "skill": {
    "id": 1,
    "name": "py"
  },
  "level": "experienced"
}
```

**Error Responses:**
- `400 Bad Request`: Max 3 skills exceeded, duplicate skill, or invalid skill/level
- `401 Unauthorized`: Missing or invalid authentication token

**Example cURL:**
```bash
curl -X POST http://127.0.0.1:8000/api/skills/add/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -d '{
    "skill": "py",
    "level": "experienced"
  }'
```

---

#### 5. Remove Skill from Profile

**Endpoint:** `POST /api/skills/remove/`

**Description:** Removes a programming language skill from the authenticated user's profile.

**Authentication Required:** Yes

**Request Body:**
```json
{
  "skill": "py"
}
```

**Response (200 OK):**
```json
{
  "detail": "Skill removed successfully"
}
```

**Error Responses:**
- `404 Not Found`: Skill not found in user's profile
- `401 Unauthorized`: Missing or invalid authentication token

---

### Project Management Endpoints

#### 6. Create Project

**Endpoint:** `POST /api/projects/`

**Description:** Creates a new project. The authenticated user becomes the project owner.

**Authentication Required:** Yes

**Request Body:**
```json
{
  "project_name": "My Awesome Project",
  "description": "A project for building something amazing",
  "maximum_collaborators": 3,
  "collaborators": ["username1", "username2"]
}
```

**Required Fields:**
- `project_name` (string)
- `maximum_collaborators` (integer)

**Optional Fields:**
- `description` (string)
- `collaborators` (array of usernames)

**Response (201 Created):**
```json
{
  "id": 1,
  "project_name": "My Awesome Project",
  "description": "A project for building something amazing",
  "owner": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  },
  "maximum_collaborators": 3,
  "completed": false,
  "created_at": "2024-01-15T10:30:00Z",
  "contributors": [
    {
      "id": 1,
      "username": "johndoe"
    },
    {
      "id": 2,
      "username": "username1"
    }
  ]
}
```

---

#### 7. List All Projects

**Endpoint:** `GET /api/projects/`

**Description:** Returns a list of all projects in the system.

**Authentication Required:** No (public endpoint)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "project_name": "My Awesome Project",
    "description": "A project description",
    "owner": {
      "id": 1,
      "username": "johndoe"
    },
    "maximum_collaborators": 3,
    "completed": false,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

#### 8. Get Project Details

**Endpoint:** `GET /api/projects/{id}/`

**Description:** Returns detailed information about a specific project.

**Authentication Required:** No (public endpoint)

**Response (200 OK):** Same structure as Create Project response

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

---

#### 9. Get Projects with Open Seats

**Endpoint:** `GET /api/projects/open/`

**Description:** Returns projects that have available seats for contributors (not full).

**Authentication Required:** No (public endpoint)

**Logic:** A project is considered "open" if:
```
number_of_contributors < maximum_collaborators
```

**Response (200 OK):** Array of project objects (same structure as List Projects)

---

#### 10. Update Project

**Endpoint:** `PUT /api/projects/{id}/` or `PATCH /api/projects/{id}/`

**Description:** Updates project details. Only the project owner can update.

**Authentication Required:** Yes

**Authorization:** Only project owner

**Request Body (PATCH example):**
```json
{
  "description": "Updated description"
}
```

**Response (200 OK):** Updated project object

---

#### 11. Delete Project

**Endpoint:** `DELETE /api/projects/{id}/`

**Description:** Deletes a project. Only the project owner can delete.

**Authentication Required:** Yes

**Authorization:** Only project owner

**Response (204 No Content):** Empty response body

**Error Response (403 Forbidden):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

#### 12. Mark Project as Completed

**Endpoint:** `POST /api/projects/{id}/complete/`

**Description:** Marks a project as completed. Only the project owner can complete a project.

**Authentication Required:** Yes

**Authorization:** Only project owner

**Response (200 OK):**
```json
{
  "id": 1,
  "project_name": "My Awesome Project",
  "completed": true,
  ...
}
```

---

### Interest & Collaboration Endpoints

#### 13. Express Interest in Project

**Endpoint:** `POST /api/projects/{id}/interest/`

**Description:** Expresses interest in contributing to a project. Creates a pending interest.

**Authentication Required:** Yes

**Constraints:**
- Cannot express interest if project is full
- Cannot express interest twice in the same project
- Cannot express interest in your own project

**Request Body:** None required

**Response (201 Created):**
```json
{
  "id": 1,
  "user": 2,
  "project": 1,
  "status": "pending",
  "expressed_at": "2024-01-15T11:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Project is full, duplicate interest, or other validation error
- `401 Unauthorized`: Missing authentication token

---

#### 14. View Pending Interests

**Endpoint:** `GET /api/projects/{id}/pending_interests/`

**Description:** Returns all pending interests for a project. **Only the project owner can view this.**

**Authentication Required:** Yes

**Authorization:** Only project owner

**Privacy:** Only returns `username`, `email`, and `skills` for each applicant (not `first_name`, `last_name`, `age`, `country`, `residence`)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user": {
      "username": "applicant1",
      "email": "applicant1@example.com",
      "skills": [
        {
          "skill": {
            "id": 1,
            "name": "py"
          },
          "level": "experienced"
        }
      ]
    },
    "status": "pending",
    "expressed_at": "2024-01-15T11:00:00Z"
  }
]
```

---

#### 15. Accept Interest

**Endpoint:** `POST /api/projects/{id}/interest/{interest_id}/accept/`

**Description:** Accepts a pending interest. The user becomes a contributor to the project.

**Authentication Required:** Yes

**Authorization:** Only project owner

**Constraints:**
- Cannot accept if project is full
- Cannot accept an already handled interest

**Response (200 OK):**
```json
{
  "id": 1,
  "status": "accepted",
  "detail": "Interest accepted. User added as contributor."
}
```

**Error Responses:**
- `400 Bad Request`: Project is full or interest already handled
- `403 Forbidden`: Not the project owner
- `404 Not Found`: Project or interest not found

---

#### 16. Decline Interest

**Endpoint:** `POST /api/projects/{id}/interest/{interest_id}/decline/`

**Description:** Declines a pending interest. The user does NOT become a contributor.

**Authentication Required:** Yes

**Authorization:** Only project owner

**Constraints:**
- Cannot decline an already handled interest

**Response (200 OK):**
```json
{
  "id": 1,
  "status": "declined",
  "detail": "Interest declined."
}
```

---

### Statistics Endpoint

#### 17. Get User Statistics

**Endpoint:** `GET /api/users/me/stats/`

**Description:** Returns statistics for the authenticated user.

**Authentication Required:** Yes

**Response (200 OK):**
```json
{
  "projects_created": 5,
  "projects_contributed": 3
}
```

**Note:** `projects_contributed` counts actual contributions (users in the `contributors` field), NOT pending interests.

---

## Authentication

### Token-Based Authentication

The API uses **Token Authentication** from Django REST Framework.

### How It Works

1. **Registration or Login**: User receives a token
   ```json
   {
     "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
   }
   ```

2. **Include Token in Requests**: Add the token to the `Authorization` header
   ```
   Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
   ```

3. **Token Persistence**: Tokens are permanent until the user logs out or the token is deleted from the database.

### Example Authenticated Request

```bash
curl -X GET http://127.0.0.1:8000/api/projects/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

### Testing Authentication in Swagger UI

1. Go to `http://127.0.0.1:8000/api/docs/`
2. Click the **Authorize** button (lock icon)
3. Enter: `Token <your-token-here>` (include the word "Token" and a space)
4. Click **Authorize**
5. Now you can test protected endpoints

---

## Data Models

### User Model

Extended Django user model with additional profile fields.

**Fields:**
- `username` (string, unique, required)
- `email` (string, required)
- `password` (hashed, required)
- `first_name` (string, optional)
- `last_name` (string, optional)
- `age` (integer, optional)
- `country` (string, optional)
- `residence` (string, optional)

**Related Data:**
- `user_skills`: All skills associated with the user
- `owned_projects`: Projects created by the user
- `contributed_projects`: Projects the user contributes to
- `interests`: Interest expressions by the user

---

### Skill Model

Represents a programming language in the system.

**Fields:**
- `name` (string, unique): Language code (`py`, `js`, `cpp`, etc.)
- `id` (integer, auto-generated)

**Supported Languages:** C++, Javascript, Python, Java, Lua, Rust, Go, Julia

---

### UserSkill Model

Links users to their programming skills with proficiency levels.

**Fields:**
- `user` (ForeignKey to User)
- `skill` (ForeignKey to Skill)
- `level` (string): `beginner`, `experienced`, or `expert`

**Constraints:**
- Unique together: `(user, skill)` - prevents duplicate skills
- Max 3 skills per user (enforced at API level)

---

### Project Model

Represents an open-source project.

**Fields:**
- `project_name` (string, required)
- `description` (text, optional)
- `owner` (ForeignKey to User, required)
- `maximum_collaborators` (integer, required)
- `contributors` (ManyToMany to User)
- `completed` (boolean, default=False)
- `created_at` (datetime, auto-set)

**Relationships:**
- One owner (user who created the project)
- Many contributors (users contributing to the project)
- Many interests (ProjectInterest objects)

---

### ProjectInterest Model

Tracks user interest in projects with approval workflow.

**Fields:**
- `user` (ForeignKey to User)
- `project` (ForeignKey to Project)
- `status` (string): `pending`, `accepted`, or `declined`
- `expressed_at` (datetime, auto-set)

**Constraints:**
- Unique together: `(user, project)` - prevents duplicate interests

**Status Flow:**
1. `pending`: Initial state when user expresses interest
2. `accepted`: Owner accepted → user becomes contributor
3. `declined`: Owner declined → user does NOT become contributor

---

## Business Logic & Rules

### Skill Management Rules

1. **Maximum 3 Skills**: Each user can have at most 3 skills at any time
   - Adding a 4th skill returns `400 Bad Request`
   - Must remove a skill before adding a new one

2. **No Duplicate Skills**: A user cannot have the same skill twice
   - Attempting to add a duplicate skill returns `400 Bad Request`

3. **Valid Skill Names**: Only the 8 supported languages are accepted
   - Invalid skill names return `400 Bad Request`

4. **Valid Skill Levels**: Only `beginner`, `experienced`, or `expert` are accepted

---

### Project Rules

1. **Project Ownership**: Only the project owner can:
   - Update the project
   - Delete the project
   - Mark the project as completed
   - View pending interests
   - Accept/decline interests

2. **Open Projects Logic**: A project is considered "open" (has available seats) if:
   ```
   contributors.count() < maximum_collaborators
   ```
   - **Important**: Uses contributor count, NOT interest count
   - Even if there are many pending interests, the project is open until contributors reach the limit

3. **Project Completion**: Completed projects still appear in lists and statistics

4. **Initial Collaborators**: When creating a project, you can specify initial collaborators by username
   - Invalid usernames are silently skipped
   - Owner is automatically added as a contributor

---

### Interest Workflow Rules

1. **Expressing Interest**:
   - Cannot express interest if project is full (`contributors.count() >= maximum_collaborators`)
   - Cannot express interest twice in the same project
   - Cannot express interest in your own project

2. **Accepting Interest**:
   - Only project owner can accept
   - Cannot accept if project is full
   - Accepting adds the user to `contributors` ManyToMany field
   - Status changes from `pending` to `accepted`

3. **Declining Interest**:
   - Only project owner can decline
   - Declining does NOT add the user as a contributor
   - Status changes from `pending` to `declined`

4. **Privacy Constraint**: When viewing pending interests, only these fields are visible:
   - ✅ `username`
   - ✅ `email`
   - ✅ `skills`
   - ❌ `first_name`, `last_name`, `age`, `country`, `residence` are NOT visible

---

### Statistics Rules

1. **Projects Created**: Counts all projects where `user == project.owner`

2. **Projects Contributed**: Counts all projects where `user in project.contributors.all()`
   - **Important**: Counts actual contributions, NOT pending interests
   - Completed projects are still counted
   - Declined interests are NOT counted

---

## Testing

### Running Tests

#### Fast Test Execution (Recommended)

Using `--keepdb` and `--parallel` flags significantly speeds up test execution:

```bash
# Run all tests (70-75% faster)
python manage.py test api.tests --keepdb --parallel

# Run specific test file
python manage.py test api.tests.test_auth --keepdb

# Run specific test class
python manage.py test api.tests.test_auth.RegistrationTests --keepdb

# Run specific test method
python manage.py test api.tests.test_auth.RegistrationTests.test_register_user_success --keepdb
```

**Performance:**
- Standard: ~133-159 seconds
- Optimized: ~40-50 seconds (with `--keepdb --parallel`)

#### Standard Test Execution

```bash
# Run all tests
python manage.py test api.tests

# Run with verbose output
python manage.py test api.tests --verbosity=2
```

#### Test Coverage

```bash
# Install coverage (if not already installed)
pip install coverage

# Run tests with coverage
python -m coverage run --source='api' manage.py test api.tests

# View coverage report
python -m coverage report

# Generate HTML coverage report
python -m coverage html

# Open HTML report
# Windows: start htmlcov/index.html
# macOS: open htmlcov/index.html
# Linux: xdg-open htmlcov/index.html
```

### Test Coverage

The test suite provides comprehensive coverage:

- **Total Test Files**: 6
- **Total Test Methods**: ~80+
- **Endpoints Covered**: All 9 required endpoints
- **Coverage**: ~99%

**Test Files:**
1. `test_auth.py` - Authentication tests (registration, login, password reset)
2. `test_skills.py` - Skill management tests (add/remove, constraints)
3. `test_projects.py` - Project management tests (CRUD, open projects)
4. `test_interest.py` - Interest workflow tests (express, accept, decline)
5. `test_stats.py` - User statistics tests
6. `test_interest_flow.py` - End-to-end flow tests

For detailed test coverage information, see `TEST_COVERAGE.md`.

---

## Project Structure

```
Greapevine_assesement/
├── api/                          # Main application package
│   ├── __init__.py
│   ├── admin.py                  # Django admin configuration
│   ├── apps.py                   # App configuration
│   ├── models.py                 # Database models (User, Skill, Project, etc.)
│   ├── serializers.py            # API serializers (request/response handling)
│   ├── views.py                  # API views (endpoint handlers)
│   ├── urls.py                   # URL routing for API endpoints
│   ├── exceptions.py             # Custom exceptions
│   ├── migrations/               # Database migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_add_completed_and_seed_skills.py
│   │   └── 0003_rename_project_fields.py
│   └── tests/                    # Test suite
│       ├── test_auth.py
│       ├── test_skills.py
│       ├── test_projects.py
│       ├── test_interest.py
│       ├── test_stats.py
│       └── test_interest_flow.py
├── greapevine/                   # Django project settings
│   ├── __init__.py
│   ├── settings.py               # Main settings file
│   ├── urls.py                   # Root URL configuration
│   ├── wsgi.py                   # WSGI configuration
│   └── asgi.py                   # ASGI configuration
├── db.sqlite3                    # SQLite database (auto-generated)
├── manage.py                     # Django management script
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── TEST_COVERAGE.md              # Detailed test coverage report
└── venv/                         # Virtual environment (not in git)
```

---

## Configuration

### Settings File

Main configuration: `greapevine/settings.py`

**Key Settings:**

- **Database**: SQLite (default)
  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.sqlite3',
          'NAME': BASE_DIR / 'db.sqlite3',
      }
  }
  ```

- **Authentication**: Token Authentication
  ```python
  REST_FRAMEWORK = {
      'DEFAULT_AUTHENTICATION_CLASSES': [
          'rest_framework.authentication.TokenAuthentication',
      ],
      'DEFAULT_PERMISSION_CLASSES': [
          'rest_framework.permissions.AllowAny',
      ],
  }
  ```

- **Custom User Model**:
  ```python
  AUTH_USER_MODEL = 'api.User'
  ```

### Changing Database (Production)

To use PostgreSQL or MySQL instead of SQLite:

1. Install database adapter:
   ```bash
   # For PostgreSQL
   pip install psycopg2-binary
   
   # For MySQL
   pip install mysqlclient
   ```

2. Update `settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',  # or 'mysql'
           'NAME': 'your_database_name',
           'USER': 'your_username',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

### Security Settings (Production)

**⚠️ Important:** Before deploying to production:

1. **Change SECRET_KEY**:
   ```python
   SECRET_KEY = 'your-secret-key-here'  # Generate a new secret key
   ```

2. **Set DEBUG = False**:
   ```python
   DEBUG = False
   ```

3. **Configure ALLOWED_HOSTS**:
   ```python
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   ```

4. **Use Environment Variables**:
   ```python
   import os
   SECRET_KEY = os.environ.get('SECRET_KEY')
   DEBUG = os.environ.get('DEBUG', 'False') == 'True'
   ```

5. **Use HTTPS**: Configure SSL/TLS certificates

6. **Configure CORS** (if needed for frontend):
   ```bash
   pip install django-cors-headers
   ```

---

## Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'django'"

**Solution:** Activate your virtual environment:
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

Then reinstall dependencies:
```bash
pip install -r requirements.txt
```

---

#### 2. "python: command not found" or "python3: command not found"

**Solution:** 
- **Windows**: Use `py` instead: `py manage.py runserver`
- **macOS/Linux**: Install Python or use `python3`

---

#### 3. "OperationalError: no such table"

**Solution:** Run migrations:
```bash
python manage.py migrate
```

---

#### 4. "Port 8000 already in use"

**Solution:** Use a different port:
```bash
python manage.py runserver 8080
```

Then access at `http://127.0.0.1:8080/`

---

#### 5. "401 Unauthorized" when making authenticated requests

**Solution:** 
1. Ensure you're including the token in the Authorization header:
   ```
   Authorization: Token <your-token-here>
   ```
2. Verify the token is correct (re-login to get a new token if needed)
3. Make sure there's a space between "Token" and the token value

---

#### 6. "Permission denied" errors on Windows PowerShell

**Solution:** Run this command:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

#### 7. Migration errors

**Solution:** 
1. Delete the database file: `db.sqlite3` (if using SQLite)
2. Delete migration files in `api/migrations/` (except `__init__.py`)
3. Recreate migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

---

#### 8. Tests failing

**Solution:**
1. Ensure the database is migrated: `python manage.py migrate`
2. Run tests with verbose output to see details:
   ```bash
   python manage.py test api.tests --verbosity=2
   ```
3. Check `TEST_COVERAGE.md` for expected test behavior

---

### Getting Help

1. **Check the Logs**: Look at the terminal output for error messages
2. **Swagger UI**: Use `http://127.0.0.1:8000/api/docs/` to test endpoints
3. **Django Shell**: Debug interactively:
   ```bash
   python manage.py shell
   ```
4. **Admin Panel**: Check data at `http://127.0.0.1:8000/admin/`

---

## Additional Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **Django REST Framework**: https://www.django-rest-framework.org/
- **drf-spectacular**: https://drf-spectacular.readthedocs.io/

---

**Happy Coding! 🚀**
