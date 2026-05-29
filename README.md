# FMCG POS & Inventory Management System

Django + Django REST Framework foundation for wholesale/retail FMCG operations with role-based access, JWT authentication, and a responsive web UI.

## Features (Phase 1)

- Custom `User` model (`personID` + default `username`)
- JWT login (24-hour session via httpOnly cookies)
- Roles: SuperAdmin, Admin, SalesPerson
- SuperAdmin user management (no public registration)
- Mandatory complete-profile flow
- Django admin at `/admin/` (unchanged, username/password)
- REST API under `/api/`
- Blue (#4297C8 / #0E3692) and white responsive UI with sidebar

## Setup

```bash
cd e:\Software\software
pip install -r requirements.txt
python manage.py migrate
python manage.py bootstrap_superadmin
# If login fails (wrong password / deactivated account):
python manage.py bootstrap_superadmin --reset
python manage.py createsuperuser
python manage.py runserver
```

- **Application login:** http://127.0.0.1:8000/login/ (Person ID + password)
- **Django admin:** http://127.0.0.1:8000/admin/ (username + password from `createsuperuser`)

Default bootstrap SuperAdmin: `personID=SA001`, password `Admin@123` (change after first login).

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Login with `personID`, `password` |
| POST | `/api/auth/logout/` | Logout (clears cookies) |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| GET/PUT | `/api/auth/profile/` | Profile read/update |
| GET/POST | `/api/users/` | SuperAdmin: list/create users |
| GET | `/api/users/<id>/` | SuperAdmin: user detail |

## Project Structure

```
accounts/          # User model, auth, permissions, API
application/       # Template views, mixins, context processors
templates/         # HTML templates
static/            # CSS, JS
software/          # Project settings & URLs
```

Future modules (inventory, POS, bulk orders) can be added as new Django apps and wired into `INSTALLED_APPS` and sidebar navigation.
