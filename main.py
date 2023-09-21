import click

from config import AppConfig
from src import create_and_set_project

config = AppConfig()


@click.command()
@click.option(
    "--workflow-name",
    type=click.Choice(list(config.workflows.keys())),
    required=True,
    help="Specify the workflow name.",
)
@click.option(
    "--source",
    type=click.Choice(["git", "archive"]),
    required=True,
    help="Specify the source.",
    default="archive",
)
@click.option(
    "--branch",
    type=click.Choice(config.environments),
    required=True,
    help="Specify the branch - only relevant when using git source.",
    default="development",
)
def main(workflow_name: str, source: str, branch: str) -> None:
    global config

    config.git_branch = branch
    project_source = config.git_source if source == "git" else config.archive_source

    print(f"Loading project {config.project_name} with source {project_source}")
    project = create_and_set_project(name=config.project_name, source=project_source)

    print(f"Loading config for workflow {workflow_name}...")
    workflow_config = config.get_workflow_config(workflow_name=workflow_name)

    print(f"Running workflow {workflow_name}...")
    project.run(name=workflow_name, arguments=workflow_config, dirty=True, watch=True)


if __name__ == "__main__":
    main()
