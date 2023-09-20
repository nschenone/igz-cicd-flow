import mlrun
from kfp import dsl


@dsl.pipeline(name="GitOps Deployment Pipeline", description="Deploy a model")
def pipeline(
    challenger_model_tag: str,
    champion_model_tag: str,
    label_column: str,
    deploy_model_name: str,
):
    # Get our project object
    project = mlrun.get_current_project()
    
    # Get challenger model URI
    get_challenger_model = project.run_function(
        "get-model-uri",
        params={
            "model_name" : "model",
            "model_tag" : challenger_model_tag
        },
        outputs=["model_uri", "test_set_uri"]
    )

    # Deploy model to endpoint
    serving_fn = project.get_function("serving")
    serving_fn.set_tracking()
    deploy = project.deploy_function(
        serving_fn, models=[
            {
                "key": deploy_model_name,
                "model_path": get_challenger_model.outputs["model_uri"]
            }
        ]
    )
    
    # Test model endpoint
    test = project.run_function(
        "model-server-tester",
        inputs={
            "table": get_challenger_model.outputs["test_set_uri"],
        },
        params={
            "addr": deploy.outputs["endpoint"],
            "label_column": label_column,
            "model": deploy_model_name,
        },
    )