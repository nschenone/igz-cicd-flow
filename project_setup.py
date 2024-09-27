import os
from pathlib import Path

import mlrun


def setup(project: mlrun.projects.MlrunProject) -> mlrun.projects.MlrunProject:
    source = project.get_param("source")
    default_image = project.get_param("default_image")
    default_base_image = project.get_param("default_base_image", "mlrun/mlrun:1.6.2")
    image_requirements_file = project.get_param(
        "image_requirements_file", "requirements.txt"
    )
    artifact_path = project.get_param("artifact_path")
    secrets_file = project.get_param("secrets_file")
    force_build = project.get_param("force_build", False)

    # Set MLRun project secrets via secrets file
    if secrets_file and os.path.exists(secrets_file):
        project.set_secrets(file_path=secrets_file)
        mlrun.set_env_from_file(secrets_file)

    # Set artifact path
    if artifact_path:
        project.artifact_path = artifact_path

    # Load artifacts
    project.register_artifacts()

    # Set default project docker image - functions that do not specify image will use this
    if default_base_image and image_requirements_file and force_build:
        requirements = Path(image_requirements_file).read_text().split()
        command = f'pip install {" ".join(requirements)}'
        project.build_image(
            base_image=default_base_image,
            commands=[command],
            set_as_default=True,
            overwrite_build_params=True,
            with_mlrun=False,
        )
    if project.default_image is None and default_image:
        project.set_default_image(default_image)

    # Set project git/archive source and enable pulling latest code at runtime
    if source:
        print(f"Project Source: {source}")
        project.set_source(source, pull_at_runtime=True)

        if ".zip" in source:
            print(f"Exporting project as zip archive to {source}...")
            project.export(source)

    # Set MLRun functions
    project.set_function(
        name="data", func="src/functions/data.py", kind="job", with_repo=True
    )
    project.set_function(
        name="describe",
        func="hub://describe",
        kind="job",
        handler="analyze",
    )
    project.set_function(
        name="train",
        func="src/functions/train.py",
        kind="job",
        handler="train_model",
        image=default_base_image,
    )
    project.set_function(
        name="validate",
        func="src/functions/validate.py",
        kind="job",
    )
    project.set_function(
        name="test",
        func="src/functions/test_classifier.py",
        kind="job",
        handler="test_classifier",
    )
    project.set_function(
        name="serving",
        func="hub://v2_model_server",
        kind="serving",
        image=default_base_image,
        requirements_file=image_requirements_file,
    )
    project.set_function(
        name="model-server-tester",
        func="hub://v2_model_tester",
        kind="job",
        handler="model_server_tester",
    )
    project.set_function(
        name="get-model-uri",
        func="src/functions/get_model_uri.py",
        kind="job",
        handler="get_model_uri_from_tag",
    )

    # Set MLRun workflows
    project.set_workflow(name="train", workflow_path="src/workflows/train_workflow.py")
    project.set_workflow(
        name="deploy", workflow_path="src/workflows/deploy_workflow.py"
    )

    # Set artifacts
    project.set_artifact(
        key="model", artifact="artifacts/model:challenger.yaml", tag="challenger"
    )

    # Save and return the project:
    project.save()
    return project
