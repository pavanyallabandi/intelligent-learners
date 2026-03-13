# StudyHub: Video Learning Platform

A Django-based application to curate a roadmap of YouTube videos for learners. Instructors and group admins can track the progress of the community.

## Features
- Premium, glassmorphic UI with changing motivational quotes
- Group privacy controls (Admin public groups vs User private groups)
- Embedded YouTube Player
- Real-time progress tracking calculation
- Access Request Management

## Local Setup
1. Create a virtual environment: `python -m venv venv`
2. Activate the virtual environment
3. Install dependencies: `pip install django pillow psycopg2-binary dj-database-url`
4. Apply migrations: `python manage.py migrate`
5. Create a superuser: `python manage.py createsuperuser`
6. Run server: `python manage.py runserver`

## Upgrading & Enhancements
The application is designed to be easily extensible. All major logics are cleanly segregated in `studyhub/views.py` and `studyhub/models.py`.

### Where to add features?
- **Badges/Gamification**: Add a `Badge` model in `models.py` and assign badges when `UserProgress` reaches 100% in `mark_video` view. Update `group_detail.html` to display them.
- **Comments/Discussions**: Create a `Comment` model linked to a `Video` or `StudyGroup` and add a comment section layout below the video player in `group_detail.html`.
- **Custom Backgrounds**: Users could upload their own motivational background image. Add a `background_image` ImageField to `StudyGroup` and override the javascript background cycler directly from the template context.

## Connecting to Supabase
Currently, the app uses a local SQLite database (`db.sqlite3`). To connect it to your Supabase PostgreSQL database:

1. Log into your [Supabase Dashboard](https://supabase.com).
2. Create a new Organization and Project.
3. Go to `Project Settings` -> `Database` and find your **Connection string** (URI).
4. Install postgres libraries if not already installed:
```bash
pip install psycopg2-binary dj-database-url
```
5. Modify your `core/settings.py` `DATABASES` section to look like this:

```python
import dj_database_url
import os

# Set this environment variable in your production environment or .env file
# E.g: os.environ['DATABASE_URL'] = "postgresql://postgres:[YOUR-PASSWORD]@[YOUR-HOST]:5432/postgres"

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600
    )
}
```
6. Run migrations to initialize the Supabase tables: `python manage.py migrate`
