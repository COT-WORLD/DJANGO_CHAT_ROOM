# DJANGO_CHAT_ROOM

This is a Django-based web application designed to [briefly describe the purpose of the app, e.g., manage a blog, track projects, etc.].

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Errors](#errors)
- [Contributing](#contributing)

## Features

- Create study rooms: Users can create study rooms with specific topics.
- Join study rooms: Users can join study rooms created by other users.
- Chat within study rooms: Users can chat with other users in the study rooms they have joined.
- User profiles: Users can create profiles with information such as their name, bio, and profile picture.
- Authentication: Users can register and log in to the application.
- Search functionality: Users can search for study rooms by topic.
- Activity feed: The application displays recent activity in study rooms, such as new messages and replies.
- SSO(Signle Sign On)- The application has SSO for Google.

## Installation

### Prerequisites

Ensure you have the following installed:
- Python 3.x
- Django 3.x or newer
- PostgreSQL (or any other DB backend used)

### Steps

1. Set up a virtual environment:

```bash
Copy code
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
2. Clone the repository:
```bash
git clone https://github.com/COT-WORLD/DJANGO_CHAT_ROOM.git
cd DJANGO_CHAT_ROOM
```
3. Set-up-the-environment-variables
Create .env file in root of django project and then three environment variables.
```bash
EXTERNAL_DATABASE_URL="postgres://<username>:<password>@<host>:<port>/<database>"
Client_ID="Google API OAUTH Client ID"
Client_secret="Google API OAUTH Client SECRET"
```

3. Install required dependencies:

```bash
pip install -r requirements.txt
```
4. Once you have setup database then Apply migrations, create superuser and runserver.

```bash 
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
## Configuration
Access the Admin Panel
Once the server is running, you can access the Django Admin Panel by navigating to:
```bash
http://127.0.0.1:8000/admin/
```
Create site in site model through django-admin and set data as below:
```bash
Domain Name: http://127.0.0.1:8000
Display Name: http://127.0.0.1:8000
```
Now goto Social accounts model and one social applications where set data as below:

```bash
Provider: Google
Name: google
Client Id: from env file
Client secret: from env file
Sites: http://127.0.0.1:8000 to chosen sites which is always empty unless you add something.
```
## Errors
Fixing the SITE_ID Error in Django
If you're encountering a SITE_ID error, it usually means the site ID isn't properly set in your Django settings. Here's how to resolve it:

Find the Correct SITE_ID:

Go to the Django admin interface: 
```bash 
http://127.0.0.1:8000/admin/.
```
Under the Sites section, find your site and note the ID in the URL, e.g., 
```bash
http://127.0.0.1:8000/admin/sites/site/15/change/ 
```
here, 15 is the SITE_ID.
Update settings.py:

In your settings.py, set the correct SITE_ID:
```bash
SITE_ID = 15
```
Restart the Server:
Save the changes and restart your Django development server:
```bash
python manage.py runserver
```
## Contributing

Contributions are welcome! Please follow these steps to contribute:

Fork the repository.
Create a new branch (git checkout -b feature-branch).
Commit your changes (git commit -m 'Add feature').
Push to the branch (git push origin feature-branch).
Create a pull request with a description of your changes.

