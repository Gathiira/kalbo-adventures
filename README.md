# adventure system

##### dumping initial data

python manage.py dumpdata auth.Group --indent 4 --natural-primary --natural-foreign > initial_data.json

#### loading initial data

python manage.py loaddata initial_data.json