import click
import mlrun

from config import AppConfig

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
@click.option(
    "--single-cluster-mode",
    is_flag=True,
    help="Specify whether the environments exist in the same cluster.",
    default=False,
)
def main(
    workflow_name: str, source: str, branch: str, single_cluster_mode: bool
) -> None:
    global config

    # Set source - git or archive
    config.git_branch = branch
    project_source = config.git_source if source == "git" else config.archive_source

    # Single user mode - project will be run using service account
    user_project = (
        True if single_cluster_mode and branch in ["staging", "master"] else False
    )

    print(f"Loading project {config.project_name} with source {project_source}")
    project = mlrun.get_or_create_project(
        name=config.project_name,
        parameters={
            "source": project_source,
            "artifact_path": config.artifact_path,
            "user_project": user_project,
            "force_build": False,
        },
    )

    print(f"Loading config for workflow {workflow_name}...")
    workflow_config = config.get_workflow_config(workflow_name=workflow_name)

    print(f"Running workflow {workflow_name}...")
    project.run(name=workflow_name, arguments=workflow_config, dirty=True, watch=True)


if __name__ == "__main__":
    main()
