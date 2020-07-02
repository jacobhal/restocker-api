# restocker-api
A python API for checking restocking of products on websites.  

## Guide to create a python API/Cron job for Heroku 
<https://stackabuse.com/deploying-a-flask-application-to-heroku/>

1. Create a Git repository for your app.

2. Create a virtual environment: ```python -m venv <NAME>/```.

3. Activate it: ```source <NAME>/bin/activate```.

4. If you’re creating an API: `pip install flask` && `pip install gunicorn`.

If you’re creating a Cron job: Install APScheduler through pip or some other scheduler

5. If you’re creating an API: Create app.py and setup a basic Flask template and test it locally with `python app.py`.

If you’re creating a Cron job: Create a file cron_job.py or similar and setup a basic Blockingscheduler function

6. Use `pip freeze > requirements.txt` to create a requirements.txt with all the packages installed which
will install them on the Heroku server.

7. Create a file named "Procfile".

If you’re creating an API: add the line `web: gunicorn app:app` or copy the config in section [Procfile](#procfile-config-for-flaskcron-jobs).

If you’re creating a Cron job application: If you are implementing some scheduled script you can use the Procfile config for that in section [Procfile](#procfile-config-for-flaskcron-jobs).

8. Create a new app on Heroku (if you haven't made a git repo yet you can use `git init .` and do it now).

9. Push all your changes to git and use `heroku login -i` to login to Heroku through the terminal.

10. Use `heroku git:remote -a {your-project-name}` where the project name is the name of the app on Heroku.

11. Use `git push heroku master` to push your latest git changes to Heroku. You can also setup a connection to your Git repo on Heroku and deploy your branches directly on there if you like.

## Heroku config for private variables
If you have config variables that are used on Heroku, such as API keys, personal emails etc. you can add those to a local .env file which will be picked up automatically by Heroku when you run `heroku local` instead of running a python file.

## Procfile config for Flask/Cron jobs
Procfile flask config: ```web: gunicorn app:app --worker-class eventlet --timeout 120 --log-level debug --workers 3```

Procfile cronjob config: ```clock: python cron_job.py``` --> Run following command when deployed: ```heroku ps:scale clock=1``` which will scale clock dynos to 1.

## Selenium
For this project, we had to use selenium since the web scraping depended on a certain dropdown value being chosen first (a certain product).

The geckodriver for running Selenium in Firefox was added using ```heroku buildpacks:add https://github.com/ronnielivingsince1994/heroku-integrated-firefox-geckodriver```

Remember to also set the necessary CONFIG vars on Heroku for the buildpack to work when deployed.
The local .env variables for MAC are as following for me:

```
FIREFOX_BIN=/Applications/Firefox.app/Contents/MacOS/firefox-bin
GECKODRIVER_PATH=/usr/local/bin/geckodriver`
```

## If heroku local connection is busy
Find process for port: ```lsof -n -i4TCP:5000```
Kill process: ```kill -9 PID```
