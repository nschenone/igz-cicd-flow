import click

from src import create_and_set_project, load_config, TrainConfig, EvaluateConfig, DeployConfig


PIPELINE_MAPPING = {
    "train" : TrainConfig,
    "evaluate" : EvaluateConfig,
    "deploy" : DeployConfig
}
SOURCES = ["git", "local"]
BRANCHES = ["development", "staging", "master"]


@click.command()
@click.option(
    "--workflow-name",
    type=click.Choice(list(PIPELINE_MAPPING.keys())),
    required=True,
    help="Specify the workflow name.",
)
@click.option(
    "--source",
    type=click.Choice(SOURCES),
    required=True,
    help="Specify the source.",
    default="local"
)
@click.option(
    "--branch",
    type=click.Choice(BRANCHES),
    required=True,
    help="Specify the branch - only relevant when using git source.",
    default="development"
)
def main(
    workflow_name: str,
    source: str,
    branch: str
) -> None:
    
    config = load_config(git_branch=branch)
    project_source = config.git_source if source == "git" else config.local_source
    
    print(f"Loading project {config.project_name} with source {project_source}")
    project = create_and_set_project(name=config.project_name, source=project_source)
    
    print(f"Loading config for workflow {workflow_name}...")
    workflow_config = PIPELINE_MAPPING[workflow_name](**config.dict())
    
    print(f"Running workflow {workflow_name}...")
    run_id = project.run(
        name=workflow_name,
        arguments=workflow_config.dict(),
        dirty=True,
        watch=True
    )
    


if __name__ == "__main__":
    main()