import yaml

from pydantic import BaseModel


def load_config(config_path: str = "config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


class TrainConfig(BaseModel):
    source_url: str
    label_column: str
    allow_validation_failure: bool
    ohe_columns: list
    test_size: float

    
class EvaluateConfig(BaseModel):
    model_path: str
    train_set: str
    test_set: str
    label_column: str
    allow_validation_failure: bool
    
    
class DeployConfig(BaseModel):
    model_path: str
    test_set: str
    label_column: str
    model_name: str
    