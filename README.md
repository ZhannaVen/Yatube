### YaTube - social network for bloggers
### Description
The project is intended for publishing posts with pictures. The author of publications can subscribe to other authors and leave comments to their posts. The project is divided into groups (interests).


### Used frameworks and libraries:
- Python 3.7
- Django 2.2.16
- SQLite3
- HTML
- CSS


### How to run a project (on Unix)
- Clone the repository.
```bash
git clone git@github.com:ZhannaVen/Yatube.git
```
- Install and activate the virtual environment (requires python version >= 3.7):
```bash
python3 -m venv venv
source venv/bin/activate
```
- Install dependencies from requirements.txt:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```
- Run the required migrations:
```bash
python manage.py migrate
```
- Create a superuser:
```bash
python manage.py createsuperuser
```
- Run the project:
```bash
python manage.py runserver
```
### User roles

- Anonymous - can view all publications.
- Authenticated user (user) - can, like Anonymous, read everything, in addition, he can publish posts, can comment on other people's publications; can edit and delete own posts and comments. This role is assigned by default to every new user.
- Moderator - has the same rights as the authenticated user plus the right to delete any posts and comments.
- Administrator (admin) - has full rights to manage all project content: create and delete posts and comments, assign roles to users, create new groups.
- Superuser Django - has the same rights as Administrator.
