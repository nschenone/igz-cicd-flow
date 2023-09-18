import mlrun
from kfp import dsl


@dsl.pipeline(name="GitOps Evaluation Pipeline", description="Evaluate a model")
def pipeline(
    model_path: str,
    train_set: str,
    test_set: str,
    label_column: str = "target",
    allow_validation_failure: bool = False,
):
    # Get our project object
    project = mlrun.get_current_project()

    validate_model = project.run_function(
        "validate",
        handler="validate_model",
        inputs={
            "train": train_set,
            "test": test_set,
        },
        params={
            "model_path": model_path,
            "label_column": label_column,
            "allow_validation_failure": allow_validation_failure,
        },
        outputs=["passed_suite"],
    )