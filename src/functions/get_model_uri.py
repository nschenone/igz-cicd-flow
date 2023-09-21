import mlrun


@mlrun.handler(outputs=["model_uri", "test_set_uri"])
def get_model_uri_from_tag(
    context: mlrun.MLClientCtx, model_name: str, model_tag: str
) -> str:
    project = context.get_project_object()

    model_artifact = project.list_models(
        name=model_name, tag=model_tag, best_iteration=True
    )[0]

    return model_artifact.uri, model_artifact.extra_data["test_set"]
