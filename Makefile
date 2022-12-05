local:
	python manage.py runserver

test:
	coverage run --source='people/' manage.py test .
	coverage report -m

build:
	docker-compose up --build