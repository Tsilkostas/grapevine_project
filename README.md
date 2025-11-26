# Greapevine Collaborator Finder API

<span style="color: #2E7D32;">**🚀 REST API**</span> | <span style="color: #1976D2;">**🐍 Python 3.8+**</span> | <span style="color: #0288D1;">**🎯 Django 4.2+**</span> | <span style="color: #00796B;">**📚 DRF 3.14+**</span> | <span style="color: #F57C00;">**🧪 99% Test Coverage**</span>



A Django REST Framework API for connecting programmers with open-source projects. Users can register, manage their programming skills, create or join projects, and collaborate with other developers.



## <span style="color: #2E7D32;">🚀 Quick Start</span>



### Prerequisites



- Python 3.8 or higher

- pip (usually comes with Python)



### Installation



1. **Create and activate a virtual environment:**



   **Windows (PowerShell):**

   ```powershell

   python -m venv venv

   .\venv\Scripts\Activate.ps1

   ```



   **Windows (Command Prompt):**

   ```cmd

   python -m venv venv

   venv\Scripts\activate.bat

   ```



   **macOS/Linux:**

   ```bash

   python3 -m venv venv

   source venv/bin/activate

   ```



2. **Install dependencies:**

   ```bash

   pip install -r requirements.txt

   ```



3. **Run migrations:**

   ```bash

   python manage.py migrate

   ```

   

   This will:

   - Create the SQLite database (`db.sqlite3`) as the mock database

   - Automatically seed all supported programming languages (C++, Javascript, Python, Java, Lua, Rust, Go, Julia)



4. **Create a superuser (optional):**

   ```bash

   python manage.py createsuperuser

   ```



5. **Start the development server:**

   ```bash

   python manage.py runserver

   ```



The API will be available at <span style="color: #1976D2;">**`http://127.0.0.1:8000/api/`**</span>



<span style="color: #F57C00;">**💡 Note**: The application uses SQLite3 as the database (stored in `db.sqlite3`). No additional database setup is required.</span>



## <span style="color: #1976D2;">🧪 Quick Test</span>



Once the server is running, you can test the API using any of these methods:



### Option 1: Swagger UI (Recommended)

1. Open `http://127.0.0.1:8000/api/docs/` in your browser

2. Use the interactive interface to test all endpoints

3. Authenticate by clicking "Authorize" and entering your token (obtained from `/api/auth/login/`)



### Option 2: Command Line (curl)

```bash

# Register a new user

curl -X POST http://127.0.0.1:8000/api/auth/register/ \

  -H "Content-Type: application/json" \

  -d "{\"username\": \"testuser\", \"email\": \"test@example.com\", \"password\": \"testpass123\"}"



# Login and get token

curl -X POST http://127.0.0.1:8000/api/auth/login/ \

  -H "Content-Type: application/json" \

  -d "{\"username\": \"testuser\", \"password\": \"testpass123\"}"

```



### Option 3: Postman

- Import the OpenAPI schema from `http://127.0.0.1:8000/api/schema/`

- Or manually create requests using the endpoints listed in Swagger UI



## <span style="color: #0288D1;">📚 API Documentation</span>



Interactive API documentation is available at:

- <span style="color: #1976D2;">**Swagger UI**</span>: `http://127.0.0.1:8000/api/docs/`

- <span style="color: #1976D2;">**OpenAPI Schema**</span>: `http://127.0.0.1:8000/api/schema/`



## <span style="color: #F57C00;">✅ Testing</span>



### Run all tests:

```bash

python manage.py test api.tests

```



### Run tests with coverage:

```bash

pip install coverage

coverage run --source='api' manage.py test api.tests

coverage report

coverage html  # Generate HTML report in htmlcov/

```



**Test Coverage**: <span style="color: #2E7D32; font-weight: bold;">**~99%**</span> <span style="background-color: #E8F5E9; padding: 2px 6px; border-radius: 3px;">Excellent</span>



**Coverage Report Location**: 

- HTML Report: Open `htmlcov/index.html` in your browser

- Text Report: Run `coverage report` in terminal

- Detailed Test Coverage: See `TEST_COVERAGE.md` for detailed test coverage information



### Fast test execution:

```bash

# Run tests with --keepdb --parallel for better performance

python manage.py test api.tests --keepdb --parallel

```



## <span style="color: #0288D1;">✨ Key Features</span>



- **User Authentication**: Registration, login, and password reset with token-based authentication

- **Skill Management**: Add/remove programming language skills (max 3 per user)

- **Project Management**: Create, view, update, delete, and complete projects

- **Interest System**: Express interest in projects with owner approval workflow

- **User Statistics**: Track projects created and contributed to

- **Privacy Controls**: Limited data visibility in interest workflows



## <span style="color: #7B1FA2;">🛠️ Technology Stack</span>



- Python 3.8+

- Django 4.2+

- Django REST Framework 3.14+

- drf-spectacular (OpenAPI/Swagger documentation)

- SQLite3 (mock database, auto-created on first migration)



## <span style="color: #7B1FA2;">📁 Project Structure</span>



```

api/

├── models.py          # Database models

├── views.py           # API endpoints

├── serializers.py     # Request/response serializers

├── urls.py            # URL routing

├── permissions.py     # Custom permission classes

├── services.py        # Business logic services

├── constants.py       # Application constants

├── exceptions.py      # Custom exception classes

└── tests/             # Test suite



greapevine/

├── settings.py        # Django settings

└── urls.py            # Root URL configuration

```



## Additional Documentation



- **Test Coverage Report**: See `TEST_COVERAGE.md` for detailed test coverage information

- **API Endpoints**: Explore all endpoints in Swagger UI at `/api/docs/`
