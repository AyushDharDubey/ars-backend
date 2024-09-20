# Assignment Review System (ARS)

This repository contains the backend implementation for the **Assignment Review System (ARS)**, designed to streamline and manage the assignment-review process over multiple iterations. The project is built using Django and Django REST framework for the backend, and supports various roles, including admin, reviewer, and reviewee.

## Features

- **Authentication**: 
  - Conventional username-password authentication.
  - OTP-based email verification
  - Channel I OAuth-based login.
- **Roles**: Users can act as admins, reviewers, or reviewees.
  - **Reviewer**:
    - Create assignments with attachments (PDF, DOCX, images, links, etc.).
    - Assign tasks and reviewers.
    - Review assignments over multiple iterations.
  - **Reviewee**:
    - Submit assignments with attachments.
    - Tag reviewers and resubmit assignments.
  - **Admin**: Oversee the entire system. (not implemented yet)
- **Access Rights**: Managed using Django's permission system.
- **Team Submissions**: Enable team-based assignment submissions.

## Local Setup

1. Clone the repository:
    ```
    git clone https://github.com/ayushdhardubey/ars-backend.git
    cd ars-backend
    ```

2. Set up a virtual environment:
    ```
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

4. Load your environment with the following environment variables: :
    ```
    # Database configuration
    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=your_db_hostname
    DB_PORT=your_db_port

    # Channel I OAuth configuration
    CHANNELI_CLIENT_ID=your_channeli_client_id
    CHANNELI_CLIENT_SECRET=your_channeli_client_secret

    # Backend base URL
    BACKEND_BASE_URL=http://localhost:8000

    ```

5. Apply database migrations:
    ```
    python manage.py migrate
    ```

6. Create User groups:
    ```
    python manage.py create_groups
    ```

7. Run the development server:
    ```
    python manage.py runserver
    ```