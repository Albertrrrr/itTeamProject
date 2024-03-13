## EasyCook Web application 
UofG Information Technology TeamProject
### Introduction
This is the back-end implementation of the EasyCook website, which is a part of the University of Glasgow's MSC Information Technology programme.
### Environment Preparation
#### Install Anaconda Environment
```
conda create -n itTeamProject python=3.9
conda activate itTeamProject
```
#### Install required packages
```
pip install -r requirements.txt
```

### Database Preparation
The most important thing is that you should replace your database configuration.   
After followed that, you can use the basic tools of Django to build your database by 
```
python manage.py migrate 
```
If you would like to change our design of database, you can overwrite our models and then run this command.
```
python manage.py migrate 
```
We recommend the following software to manage the database：
* Navicat
* Datagrip

### Run
This project is based on Django REST Framework, Redis, and you should start the service with the following command.
#### Notice
* You must ensure that your Redis service is turned on.
* Your pip requirements are all installed.

```
python manage.py runserve  
celery -A itTeamProject worker -l info
```

### SAMPLE
You can view the backend project for this by visiting the following url: 
http://35.242.165.34/#/
