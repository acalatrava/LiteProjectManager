# Lite Project Manager

Lite Project Manager is a simple project management tool that allows you to create, manage and track your projects for small teams. It allows you to create projects, add tasks to them, assign them to users, and track their progress. It will also generate a Gantt chart for each project. Users can login and register. They will have different roles and permissions like:
 - Admin: Can create, edit and delete projects, tasks, users and roles.
 - User: Can view projects, tasks and their own tasks.
Also, an user can be assigned to multiple projects and have different roles in each project:
 - Project Manager: Can create, edit and delete tasks in a project. It can also assign tasks to other users.
 - Project Member: Can view tasks in a project, and update their own tasks.

### Prerequisites

You need to have Python 3.6 or higher installed on your machine. You can download it from [here](https://www.python.org/downloads/).

### Installing

1. Clone the repository
```bash
git clone https://github.com/acalatrava/app_template
```

2. Change the directory
```bash
cd app_template
```

3. Install the requirements
```bash
cd backend
pip install -r requirements.txt
```

4. Run the server in developer mode
```bash
uvicorn app.main:app --reload &
cd ../frontend
npm run dev --
```

Once the app is running you can check the docs via `http://127.0.0.1:8000/docs`

## Usage

The application provides the following endpoints:

### Authentication

- `POST /signup`: Create a new user. The request body should include `username` and `password`. 

- `POST /token`: Authenticate a user and return an access token. The request body should include `username` and `password`.

### Projects

- `GET /api/v1/projects`: Get all projects.

- `POST /api/v1/projects`: Create a new project. The request body should include `name` and `description`.

- `PUT /api/v1/projects/<project_id>`: Update a project. The request body should include `name` and `description`.

- `DELETE /api/v1/projects/<project_id>`: Delete a project.

### Tasks

- `GET /api/v1/tasks`: Get all tasks.

- `POST /api/v1/tasks`: Create a new task. The request body should include `name` and `description`.

- `PUT /api/v1/tasks/<task_id>`: Update a task. The request body should include `name` and `description`.

- `DELETE /api/v1/tasks/<task_id>`: Delete a task.

### Users

- `GET /api/v1/users`: Get all users.

- `POST /api/v1/users`: Create a new user. The request body should include `username` and `password`.

- `PUT /api/v1/users/<user_id>`: Update a user. The request body should include `username` and `password`.

- `DELETE /api/v1/users/<user_id>`: Delete a user.

### Gantt Chart

- `GET /api/v1/gantt/<project_id>`: Get the Gantt chart for a project.


## Deployment

This application can also be run using Docker, which can help to ensure consistency across different environments.

### Prerequisites

You need to have Docker installed on your machine. You can download it from [here](https://www.docker.com/products/docker-desktop).

### Building the Docker Image

To build the Docker image, navigate to the directory containing the `Dockerfile` and run the following command:

```bash
docker build -t your-image-name .
```

Replace `your-image-name` with the name you want to give to your Docker image.

You can also use Docker Compose like:

```bash
docker compose --build
```

### Running the Docker Container

After the image has been built, you can start the application by running a container from that image:

```bash
docker run -p 8000:8000 your-image-name
```

or with Docker Compose

```bash
docker compose up --build -d
```

This command maps port 8000 in the container to port 8000 on your machine. You can replace the first `8000` with a different port number if you want to access the application on a different port.

Now, you should be able to access the application at `http://localhost:8000` (or your chosen port number).


## Built With

* [FastAPI](https://fastapi.tiangolo.com/) - The web framework used
* [OAuth2PasswordBearer](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) - For user authentication
