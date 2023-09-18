import mlrun
from kfp import dsl


@dsl.pipeline(name="GitOps Deployment Pipeline", description="Deploy a model")
def pipeline(
    model_path: str,
    test_set: str,
    model_name: str = "model",
    label_column: str = "target"
):
    # Get our project object
    project = mlrun.get_current_project()

    # Deploy model to endpoint
    serving_fn = project.get_function("serving")
    serving_fn.set_tracking()
    deploy = project.deploy_function(
        serving_fn, models=[{"key": model_name, "model_path": model_path}]
    )
    
    # Test model endpoint
    test = project.run_function(
        "model-server-tester",
        inputs={
            "table": test_set,
        },
        params={
            "addr": deploy.outputs["endpoint"],
            "label_column": label_column,
            "model": model_name,
        },
    )