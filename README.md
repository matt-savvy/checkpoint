#Checkpoint


## Deploying to new server

1. Sign up for a Heroku account and install cli tools
2. `heroku new {{name_of_server_you_want}}`
3. `git push heroku master`
4. `heroku run python manage.py syncdb`
5. `heroku run python manage.py migrate`
6. `heroku run python manage.py createsuperuser`
7. `heroku open`