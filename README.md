### This is a course work university project that was developed in a team of four people using Jira as a project management software.

In a nutshell, this project is a website where users can do following:

- Rate and read manga;
- Create up to 20 personal lists;
- Add manga to those lists;
- Create teams of translators;
- Add translations of manga.

I was completely responsible for backend (without tests) and database development. 
Looking back at it, I can see many ways to improve it, 
starting from project architecture and finishing with code documentation and many other things.\
Backend features `celery` as a background worker and `Cloudinary` as an image hosting service for manga pages.

### To set up and run server

1. Create and activate new virtual environment
   - `python -m venv venv`
   - `venv\scripts\activate`
1. Install all the necessary libraries
   - `pip install -r requirements.txt`
1. Start server
   - `python manage.py runserver`
1. Start background worker
   - `celery -A backend worker --pool=solo --loglevel=info`