import click

from src import create_and_set_project, load_config, TrainConfig, EvaluateConfig, DeployConfig


config = load_config()


PIPELINE_MAPPING = {
    "train" : TrainConfig,
    "evaluate" : EvaluateConfig,
    "deploy" : DeployConfig
}

SOURCE_MAPPING = {
    "local" : config.local_source,
    "git" : config.git_source
}

@click.command()
@click.option(
    "--workflow-name",
    type=click.Choice(list(PIPELINE_MAPPING.keys())),
    required=True,
    help="Specify the workflow name.",
)
@click.option(
    "--source",
    type=click.Choice(list(SOURCE_MAPPING.keys())),
    required=True,
    help="Specify the source.",
    default="local"
)
def main(
    workflow_name: str,
    source: str
) -> None:
    global config
    
    print(f"Loading project {config.project_name} with source {source}")
    project = create_and_set_project(name=config.project_name, git_source=SOURCE_MAPPING[source])
    
    print(f"Loading config for workflow {workflow_name}...")
    config = load_config()
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