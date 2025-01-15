@pytest.fixture(scope="session")
def test_db(test_db_path):
    # Override the database path
    import app.core.config as config
    config.SQLITE_PATH = test_db_path

    # Configure test database
    DB.init(test_db_path)
    DB.connect()

    # Create tables
    from app.models.project import Project, ProjectMember
    from app.models.task import Task
    DB.create_tables([User, AuthToken, Project, ProjectMember, Task])

    yield DB

    # Cleanup
    DB.close()
