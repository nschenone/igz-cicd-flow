import os

import mlrun


def create_and_set_project(
    name: str,
    source: str,
    default_image: str = None,
    default_base_image: str = "mlrun/mlrun:1.4.1",
    image_requirements_file: str = "requirements.txt",
    artifact_path: str = None,
    user_project: bool = False,
    secrets_file: str = None,
    force_build: bool = False,
):
    """
    Creating the project for this demo.
    :param source:                  the source of the project.
    :param name:                    project name
    :param default_image:           the default image of the project
    :param user_project:            whether to add username to the project name

    :returns: a fully prepared project for this demo.
    """

    # Get / Create a project from the MLRun DB:
    project = mlrun.get_or_create_project(
        name=name, context="./", user_project=user_project
    )

    # Set MLRun project secrets via secrets file
    if secrets_file and os.path.exists(secrets_file):
        project.set_secrets(file_path=secrets_file)

    # Set artifact path
    if artifact_path:
        project.artifact_path = artifact_path

    # Load artifacts
    project.register_artifacts()

    # Set or build the default image:
    if force_build or project.default_image is None:
        if default_image is None:
            print("Building default project image...")
            image_builder = project.set_function(
                func="src/project_setup.py",
                name="image-builder",
                handler="assert_build",
                kind="job",
                image=default_base_image,
            )
            build_status = project.build_function(
                function=image_builder,
                base_image=default_base_image,
                requirements=image_requirements_file,
            )
            default_image = build_status.outputs["image"]

        project.set_default_image(default_image)

    # Export project to zip if relevant
    if ".zip" in source:
        print(f"Exporting project as zip archive to {source}...")
        project.export(source)

    # Set the project source
    project.set_source(source, pull_at_runtime=True)

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
        requirements=image_requirements_file,
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
