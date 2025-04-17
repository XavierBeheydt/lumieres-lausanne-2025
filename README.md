# Lumières-Lausanne 2025

Lumières-Lausanne 2025 is a web-based project designed to showcase the cultural and artistic initiatives of Lausanne. The project is built using Django and Docker to provide a robust and scalable development environment. It includes tools for managing content, cleaning URLs, and maintaining a structured database.


## Getting Started
<!-- FIXME: fix commands  because some are not working -->

1. Clone the project:
   ```bash
   git clone git@github.com:unil-lettres/lumieres-lausanne-2025.git
   ```

2. Start the MySQL database:
   ```bash
   docker compose up -d db
   ```

3. **Copy** `django_db_dump.sql` to the `./sql` folder.

4. Restore the database from the dump:
   ```bash
   docker exec -i db mysql -uroot -proot_password django_db < ./sql/django_db_dump.sql
   ```

5. **Copy** the `media` folder to `./django/lumieres`.

6. Start the Django server:
   ```bash
   docker compose up -d
   ```

7. Browse to `http://localhost:8000`.

8. Django admin credentials:
   - Username: `admin`
   - Password: `admin`


## Development Commands

The following commands are available via the `Makefile` to streamline development tasks:


### Environment Setup

- **Initialize the development environment**:
  ```bash
  make dev/init
  ```
  Copies `.env.template` to `.env`.

- **Install dependencies**:
  ```bash
  make install
  ```
  Installs Python dependencies and sets up symbolic links for media files.

### Docker Management
- **Start all services**:
  ```bash
  make up
  ```

- **Stop all services**:
  ```bash
  make stop
  ```

- **Restart all services**:
  ```bash
  make restart
  ```

- **View logs**:
  ```bash
  make logs
  ```

#### Database Management
- **Restore the database**:
  ```bash
  make db/restore
  ```

#### Django Commands
- **Run the development server**:
  ```bash
  make runserver
  ```

- **Run database migrations**:
  ```bash
  make migrate
  ```

- **Create database migrations**:
  ```bash
  make makemigrations
  ```

- **Open the Django shell**:
  ```bash
  make shell
  ```

- **Create a superuser**:
  ```bash
  make createsuperuser
  ```

### Tools
- **Clean URLs in the app**:
  ```bash
  make tools/clean-urls
  ```

### Cleaning
- **Clean Python artifacts**:
  ```bash
  make clean-pyc
  ```

- **Clean build artifacts**:
  ```bash
  make clean-build
  ```

- **Clean test and coverage artifacts**:
  ```bash
  make clean-test
  ```

- **Clean the development environment**:
  ```bash
  make fclean
  ```

---

### Notes
- Ensure Docker and Python dependencies are installed before running the commands.
- Use the `.env` file to configure environment variables for the project.