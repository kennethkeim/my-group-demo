


For the final project, I made a web app for my local community church, and it's called 'My Group'. It has an events page with all our group events, and a directory page with everyone's contact information. As of now, it is only intended for my local church group to use, but I may try to expand it to be used by other community groups in the future.

Here's how it works: The app requires users to register and obtain my approval to join the private group, once that is complete, they can log in and see an events page (calendar agenda view style) with all the group events, and everyone's birthdays and anniversaries. Users can add new events, or edit and delete existing events.
There is also a directory page, and it simply displays everyone's contact info as entered by me in the database. (no user add/edit functionality for now)

The app does not have any offline capabilities, but it does have a web app manifest, which provides a nice icon set and full screen support for users who add it to their mobile device home screen.


The app is developed locally and currently running on Heroku with the following:
Python/Flask backend
Postgresql database
Javascript/HTML/CSS frontend

flask sqlalchemy talks to the database for me
Gunicorn is the production web server on Heroku
