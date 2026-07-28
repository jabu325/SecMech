# SecMech

SecMech is a Django-based burglar alarm monitoring dashboard. It provides a login screen, protected dashboard pages, access reports, intrusion notifications, live camera/audio embeds, Firebase Realtime Database integration, and PWA assets.

## Features

- User authentication with Django's built-in auth system
- Protected dashboard, report, and notification pages
- Firebase Realtime Database reads and writes for alarm status and logs
- Live camera and audio stream embeds for local security monitoring
- Progressive Web App manifest and service worker assets
- Font Awesome based UI icons and custom static styles

## Project Structure

```text
.
|-- manage.py
|-- db.sqlite3
|-- main/
|   |-- urls.py
|   |-- views.py
|   |-- models.py
|   `-- migrations/
|-- secMech/
|   |-- settings.py
|   |-- urls.py
|   |-- static/
|   `-- templates/
`-- task list
```

## Requirements

- Python 3.12 or newer recommended
- Django 5.x
- django-pwa

## Setup

1. Clone the repository.

   ```bash
   git clone https://github.com/jabu325/SecMech.git
   cd SecMech
   ```

2. Create and activate a virtual environment.

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies.

   ```bash
   pip install -r requirements.txt
   ```

4. Apply database migrations.

   ```bash
   python manage.py migrate
   ```

5. Create an admin or dashboard user.

   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server.

   ```bash
   python manage.py runserver
   ```

7. Open the app at `http://127.0.0.1:8000/`.

## Routes

- `/` - login page
- `/index` - main dashboard
- `/report` - access report page
- `/notification` - intrusion notification page
- `/logout/` - log out
- `/admin/` - Django admin

## Configuration Notes

- The app currently uses SQLite for local development.
- Firebase configuration is referenced directly in the frontend templates.
- The live video and audio feeds point to a local IP camera endpoint: `192.168.43.1:8080`.
- Before production deployment, move sensitive configuration into environment variables, set `DEBUG = False`, restrict `ALLOWED_HOSTS`, and rotate any exposed credentials.

## Development

Run Django's built-in checks before committing changes:

```bash
python manage.py check
```
