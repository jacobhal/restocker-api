# restocker-api
A python API for checking restocking of products on websites.  

## Guide to create a python API for heroku 
<https://stackabuse.com/deploying-a-flask-application-to-heroku/>

## Heroku config for private variables
Add config to Heroku and add the same config in a .env file to make heroku local work.

## Update requirements.txt
```pip freeze > requirements.txt```

## Selenium
For this project, we had to use selenium since the web scraping depended on a certain dropdown value being chosen first (a certain product).

The geckodriver for running Selenium in Firefox was added using ```heroku buildpacks:add https://github.com/ronnielivingsince1994/heroku-integrated-firefox-geckodriver```

Remember to also set the necessary CONFIG vars on Heroku for the buildpack to work when deployed.

## If heroku local connection is busy
Find process for port: ```lsof -n -i4TCP:5000```
Kill process: ```kill -9 PID```
