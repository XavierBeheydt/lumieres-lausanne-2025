# Makefile for the Lumieres Lausanne project
#
# Authors:
#   - Xavier Beheydt <xavier.beheydt@gmail.com>

.DEFAULT_GOAL := all

ifeq ($(OS), Windows_NT)
	WEB_BROWSER = powershell -Command Start-Process
	RM			= rm -Force
	CP			= copy
else
	WEB_BROWSER = open
	RM			= rm -rf
	CP			= cp -r
endif

PROJECT_PATH = $(CURDIR)/app

SERVICES ?=

# Common targets

.PHONY: all
all:  ## Build all targets
	@echo "Building all targets..."

.PHONY: dev/init
dev/init:  ## Initialize the development environment
	@echo "Initializing the development environment..."
	$(CP) .env.template .env

.PHONY: install
install:  ## Install dependencies
	@echo "Installing dependencies..."
	ln -sf $(CURDIR)/mnt/media $(CURDIR)/app/media
	pip install -e .

.PHONY: up
up:  ## Up all services
	@echo "Up all services..."
	docker compose -f docker-compose.yml up -d ${SERVICES}

.PHONY: down
down:  ## Down all services
	@echo "Down all services..."
	docker compose -f docker-compose.yml down ${SERVICES}

.PHONY: start
start:  ## Start all services
	@echo "Starting all services..."
	docker compose -f docker-compose.yml start ${SERVICES}

.PHONY: stop
stop:  ## Stop all services
	@echo "Stopping all services..."
	docker compose -f docker-compose.yml stop ${SERVICES}

.PHONY: restart
restart:  ## Restart all services
	@echo "Restarting all services..."
	docker compose -f docker-compose.yml restart ${SERVICES}

.PHONY: logs
logs:  ## Logs containers in the stack.
	@echo "Logs containers in the stack..."
	docker compose -f docker-compose.yml logs -f ${SERVICES}

.PHONY: db/restore
db/restore:  ## Restore the database
	@echo "Restoring the database..."
	docker compose -f docker-compose.yml exec -T db \
		mysql -u$$MYSQL_USER -p$$MYSQL_PASSWORD \
		$$MYSQL_DATABASE < mnt/sql/2025_LL_django-v5.2.sql
	@echo "Database restored."

.PHONY: tools/clean-urls
tools/clean-urls:  ## Clean URLs in the app service
	@echo "Cleaning URLs in the app service..."
	python tools/clean-urls.py
	@echo "URLs cleaned."

.PHONY: runserver
runserver:  ## Run the developement server
	@echo "Running the development server..."
	python $(PROJECT_PATH)/manage.py runserver

.PHONY: migrate
migrate:  ## Run database migrations
	@echo "Running database migrations..."
	python $(PROJECT_PATH)/manage.py migrate

.PHONY: makemigrations
makemigrations:  ## Make migrations
	@echo "Running database make migrations..."
	python $(PROJECT_PATH)/manage.py makemigrations

.PHONY: shell
shell:  ## Run the Django shell
	@echo "Running the Django shell..."
	python $(PROJECT_PATH)/manage.py shell

.PHONY: createsuperuser
createsuperuser:  ## Create a superuser
	@echo "Creating a superuser..."
	python $(PROJECT_PATH)/manage.py createsuperuser


# Cleaning

.PHONY: fclean
fclean:  ## Clean the development environment
fclean: clean
	@echo "Cleaning the development environment..."
	$(RM) .env
	$(RM) tmp/
	$(RM) mnt/

.PHONY: clean
clean:  ## remove all build, test, coverage and Python artifacts
clean: clean-build clean-pyc clean-test
	@echo "Cleaning up..."

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
	@echo "Cleaning up Python artifacts..."
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	
.PHONY: clean-test
clean-test:  ## remove test and coverage artifacts
	@echo "Cleaning up test and coverage artifacts..."
	$(RM) .tox/
	$(RM) .coverage
	$(RM) htmlcov/
	
.PHONY: clean-build
clean-build: ## remove build artifacts
	@echo "Cleaning up build artifacts..."
	$(RM) build/
	$(RM) dist/
	$(RM) .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	

# Version 2024

V2024_SERVICES ?= app db phpmyadmin search

.PHONY: v2024/pull
tmp/v2024:
	@echo "Pulling the 2024 version rebuilt of the project..."
	@git clone https://github.com/XavierBeheydt/lumieres-lausanne-2024 tmp/v2024
v2024/pull: tmp/v2024
v2024/pull:  ## Pull the latest version of the project

.PHONY: v2024/up
v2024/up:  ## Up all v2024 services
v2024/up: v2024/pull
	@echo "Up all v2024 services..."
	docker compose -f docker/docker-compose.v2024.yml up -d ${V2024_SERVICES}
	@echo "All v2024 services are up."

.PHONY: v2024/down
v2024/down:  ## Down all v2024 services
	@echo "Down all v2024 services..."
	docker compose -f docker/docker-compose.v2024.yml down ${V2024_SERVICES}
	@echo "All v2024 services are down."

.PHONY: v2024/start
v2024/start:  ## Start all v2024 services
	@echo "Starting all v2024 services..."
	docker compose -f docker/docker-compose.v2024.yml start ${V2024_SERVICES}
	@echo "All v2024 services are started."

.PHONY: v2024/stop
v2024/stop:  ## Stop all v2024 services
	@echo "Stopping all v2024 services..."
	docker compose -f docker/docker-compose.v2024.yml stop ${V2024_SERVICES}
	@echo "All v2024 services are stopped."

.PHONY: v2024/createsuperuser
v2024/createsuperuser:  ## Create a superuser for the v2024 service
v2024/createsuperuser: v2024/up
	@echo "Creating a superuser for the v2024 service..."
	docker compose -f docker/docker-compose.v2024.yml exec app python manage.py createsuperuser
	@echo "Superuser created."

.PHONY: v2024/logs
v2024/logs:  ## Logs containers in the v2024 stack.
	@echo "Logs containers in the v2024 stack..."
	docker compose -f docker/docker-compose.v2024.yml logs -f

.PHONY: v2024/db/up
v2024/db/up:  ## Up db v2024 service
v2024/db/up: v2024/pull
	@echo "Up the v2024 db service..."
	docker compose -f docker/docker-compose.v2024.yml up -d db

.PHONY: v2024/db/restore
v2024/db/restore:  ## Restore the db v2024 service
v2024/db/restore:  v2024/db/up
	@echo "Restoring the v2024 databse..."
	docker compose -f docker/docker-compose.v2024.yml exec -T db \
		mysql -uroot -ppassword lumie_django_v3 < mnt/sql/v2024/2024-08-23_LL_django-v1.sql
	@echo "Database restored."

.PHONY:	v2024/app/up
v2024/app/up:  ## Up the v2024 app service
v2024/app/up: v2024/pull
	@echo "Starting the v2024 app service..."
	docker compose -f docker/docker-compose.v2024.yml up -d app
	@echo "v2024 app service is up."

.PHONY: v2024/app/down
v2024/app/down:  ## Down the v2024 app service
	@echo "Stopping the v2024 app service..."
	docker compose -f docker/docker-compose.v2024.yml stop app
	@echo "v2024 app service is down."

.PHONY: v2024/app/media/cp
v2024/app/media/cp:  ## Copy media files to the v2024 app service
v2024/app/media/cp: v2024/app/up
	@echo "Copying media files to the v2024 app service..."
	docker compose -f docker/docker-compose.v2024.yml cp mnt/media/. app:/usr/src/lumieres/media/
	@echo "Media files copied."

.PHONY: v2024/tools/up
v2024/tools/up:  ## Up the v2024 app tools service
v2024/tools/up: v2024/pull
	@echo "Starting the v2024 app tools service..."
	docker compose -f docker/docker-compose.v2024.yml up -d tools
	@echo "v2024 app tools service is up."

.PHONY: v2024/tools/down
v2024/tools/down:  ## Down the v2024 app tools service
	@echo "Stopping the v2024 app tools service..."
	docker compose -f docker/docker-compose.v2024.yml stop tools
	@echo "v2024 app tools service is down."

.PHONY: v2024/tools/clean-urls
v2024/tools/clean-urls:  ## Clean URLs in the v2024 app service
v2024/tools/clean-urls: v2024/db/up v2024/tools/up
	@echo "Cleaning URLs in the v2024 app service..."
	docker compose -f docker/docker-compose.v2024.yml exec -T tools python clean-urls.py
	@echo "URLs cleaned."