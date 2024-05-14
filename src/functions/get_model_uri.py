import mlrun
from mlrun.artifacts import get_model


@mlrun.handler(outputs=["model_uri", "test_set_uri"])
def get_model_uri_from_tag(
    context: mlrun.MLClientCtx, model_name: str, model_tag: str
) -> str:
    project = context.get_project_object()

    model_uri = project.get_artifact_uri(
        key=model_name,
        category="model",
        tag=model_tag,
        iter=0
    )
    _, _, extra_data = get_model(model_uri)

    return model_uri, str(extra_data["test_set"])
