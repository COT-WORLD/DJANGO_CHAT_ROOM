# DJANGO_CHAT_ROOM

**Django Chat Room** is a real-time web application that allows users to create and join topic-based study rooms, engage in threaded conversations, and manage personalized user profiles. It features user authentication, including Google SSO integration, responsive design, and activity tracking to enhance collaboration and communication.On Render's free deployment, the application runs faster due to query optimization with **Django Debug Toolbar**. Despite slow database connections, the website remains highly responsive and performs well, providing a smooth experience for users.

## Website Link

You can access the website at the following link:

[CHAT-ROOM](https://django-chat-room.onrender.com/)

## Login Details

For testing purposes, you can use the following credentials to log in:

- **Email**: `jasmine@gmail.com`
- **Password**: `password123`

> Note: These credentials are for demo/testing purposes only.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Google SSO & Superuser Automation](#google-sso--superuser-automation)
- [Production Gzip Compression](#production-gzip-compression)
- [Errors](#errors)
- [Contributing](#contributing)

---

## Features

- **Create Study Rooms**: Users can create study rooms around specific topics.
- **Join & Chat**: Users can join rooms and participate in real-time chat.
- **User Profiles**: Each user has a personalized profile with an avatar, name, and bio.
- **Authentication System**: Full authentication support including Sign Up, Login, and Logout functionalities.
- **Google SSO**: Seamless Google Single Sign-On (SSO) integration for quick registration and login.
- **Activity Feed**: View recent updates in rooms, such as new messages and activities.
- **Room Search**: Easily find study rooms by searching for topics.
- **Automated Setup**: Google OAuth app and superuser account are auto-setup using Django signals.

---

## Installation

### Option 1: Docker Setup

#### Prerequisites

- Docker

#### Steps

1. Clone the repository:

```bash
git clone https://github.com/COT-WORLD/DJANGO_CHAT_ROOM.git
cd DJANGO_CHAT_ROOM
```

2. Rename .env.sample to .env and configure environment variables (see Configuration).

3. Run the project:

```bash
docker compose up
```

**Option 2: Local Development Setup**

**Prerequisites**

- Python 3.x
- PostgreSQL or supported DB
- pip

**Steps**

1. Create and activate virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

2. Clone the repository:

```bash
git clone https://github.com/COT-WORLD/DJANGO_CHAT_ROOM.git
cd DJANGO_CHAT_ROOM
```

3. Create a .env file in the project root:

```bash
EXTERNAL_DATABASE_URL=postgres://<username>:<password>@<host>:<port>/<database>
CLIENT_ID=your_google_client_id_here
CLIENT_SECRET=your_google_client_secret_here
DJANGO_SUPER_USER_USERNAME=admin_username
DJANGO_SUPER_USER_EMAIL=admin@example.com
DJANGO_SUPER_USER_PASSWORD=securepassword123
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Collect static files, apply migrations, and run the server:

```bash
python manage.py collectstatic
python manage.py migrate
python manage.py runserver
```

## Configuration

Make sure your .env file includes the following variables:

```bash
EXTERNAL_DATABASE_URL=postgres://user:pass@host:port/db
CLIENT_ID=google-oauth-client-id
CLIENT_SECRET=google-oauth-client-secret
DJANGO_SUPER_USER_USERNAME=admin_username
DJANGO_SUPER_USER_EMAIL=admin@example.com
DJANGO_SUPER_USER_PASSWORD=yourpassword
```

These environment variables allow:

    Automatic creation of the Google social app

    Auto-creation of a Django superuser during initial migrations

## Google SSO & Superuser Automation

Google Single Sign-On is integrated via django-allauth. You only need to set the Google CLIENT_ID and CLIENT_SECRET in your .env file.

On the first run after migrations:

A Site instance will be created (or reused)

A SocialApp for Google will be auto-configured and linked to the site

A superuser will be created with credentials from the .env file

This is done using Django’s post_migrate signal.

## Production Gzip Compression

To optimize static files for production, the project uses WhiteNoise with Gzip support.

Key settings in settings.py:

```bash
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    ...
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
```

This ensures all static assets like CSS/JS are served compressed with .gz and .br versions.

## Errors

If you run into issues like:

Site matching query does not exist: Make sure SITE_ID matches the ID of the auto-created site.

Google SocialApp not found: Double-check your .env values for CLIENT_ID and CLIENT_SECRET.

## Contributing

Feel free to fork and submit pull requests. If you'd like to collaborate, open an issue to discuss your feature idea or bug fix.
