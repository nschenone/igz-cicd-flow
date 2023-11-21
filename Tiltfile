HOST = "localhost"
NAMESPACE = "mlrun"
DOCKER_REGISTRY_URL = "myregistry-cicd:5000"

# https://github.com/tilt-dev/tilt-extensions/tree/master/dotenv
load("ext://dotenv", "dotenv")

# https://github.com/tilt-dev/tilt-extensions/tree/master/helm_resource
load("ext://helm_resource", "helm_resource", "helm_repo")

# https://github.com/tilt-dev/tilt-extensions/tree/master/namespace
load("ext://namespace", "namespace_create")

# https://github.com/tilt-dev/tilt-extensions/tree/master/secret
load("ext://secret", "secret_yaml_registry")

# If secrets are required
dotenv(fn=".env")

# MLRun namespace
namespace_create(name=NAMESPACE)

# Create volume mount for Jupyter
k8s_yaml("k8s/jupyter-pv.yaml")

# Install MLRun CE
# helm_repo(name="mlrun-ce", url="https://mlrun.github.io/ce")
update_settings(k8s_upsert_timeout_secs=960)
helm_resource(
    name="mlrun-ce-k3d",
    chart="./k8s/mlrun-ce",
    # chart="mlrun-ce/mlrun-ce",
    # resource_deps=["mlrun-ce"],
    namespace=NAMESPACE,
    flags=[
        "--wait",
        "--timeout=960s",
        "--set",
        "global.registry.url=" + DOCKER_REGISTRY_URL,
        "--set",
        "global.externalHostAddress=" + HOST,
        "--set",
        "sparkOperator.enabled=false",
        "--set",
        "pipelines.images.mysql.repository=nschenone/mysql",
        "--set",
        "nuclio.dashboard.kaniko.insecurePushRegistry=true",
        "--set",
        "nuclio.dashboard.kaniko.insecurePullRegistry=true",
        "--set",
        "mlrun.api.image.tag=1.4.1",
        "--set",
        "mlrun.ui.image.tag=1.4.1",
        "--set",
        "jupyterNotebook.persistence.existingClaim=jupyter-claim",
    ],
)
