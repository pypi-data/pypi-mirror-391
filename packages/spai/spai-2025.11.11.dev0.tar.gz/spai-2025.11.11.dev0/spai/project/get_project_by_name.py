from ..repos import APIRepo


def get_project_by_name(user, project_name, workspace_name):
    repo = APIRepo()
    projects, error = repo.retrieve_projects_in_workspace(user, workspace_name)
    if error:
        raise Exception(f"Something went wrong: {error}")
    found_project = None
    for project in projects:
        if project['name'] == project_name:
            found_project = project

    if not found_project:
        raise Exception(f"Project '{project_name}' not found in workspace '{workspace_name}'")
    return found_project

