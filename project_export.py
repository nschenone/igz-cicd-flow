import click
from mlrun.datastore import StoreManager

from config import AppConfig

config = AppConfig()


def prompt_user(model_uri: str, challenger_model_tag: str) -> bool:
    while True:
        user_input = (
            input(
                f"Export model '{model_uri}' with tag '{challenger_model_tag}'? (yes/no): "
            )
            .strip()
            .lower()
        )
        if user_input == "yes":
            return True
        elif user_input == "no":
            return False
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")


@click.command()
@click.option(
    "--model-uri",
    type=str,
    required=True,
    help="Specify the model URI.",
)
@click.option(
    "--challenger-model-tag",
    type=str,
    required=True,
    help="Specify the challenger model tag.",
    default=config.challenger_model_tag,
)
@click.option(
    "--yaml-export-dir",
    type=str,
    required=True,
    help="Specify the export path for the model YAML.",
    default=config.yaml_export_dir,
)
def export_challenger_model(
    model_uri: str, challenger_model_tag: str, yaml_export_dir: str
):
    # Validate model uri
    if not model_uri.startswith("store://"):
        raise ValueError("Must be MLRun store URL with 'store://' prefix")

    # Prompt by confirmation
    if not prompt_user(model_uri=model_uri, challenger_model_tag=challenger_model_tag):
        raise ValueError("Model export cancelled")

    # Get model artifact
    store_manager = StoreManager()
    model_artifact, *_ = store_manager.get_store_artifact(url=model_uri)

    # Export given model URI to YAML
    target_path = (
        f"{yaml_export_dir}/{model_artifact.metadata.key}:{challenger_model_tag}.yaml"
    )
    print(f"Exporting model to {target_path}...")
    model_artifact.export(target_path=target_path)

    # Print out command to add to project_setup.py with challenger tag
    print(
        f"""\nAdd the following to the `project_setup.py` script:\n
project.set_artifact(
    key="{model_artifact.metadata.key}", artifact="{target_path}", tag="{challenger_model_tag}"
)"""
    )


if __name__ == "__main__":
    export_challenger_model()
