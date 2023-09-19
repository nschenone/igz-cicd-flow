from typing import Optional
import yaml

from pydantic import BaseModel, BaseSettings


class Config(BaseSettings):
    project_name: str
    local_source: str
    git_source: str
    source_url: str
    label_column: str
    allow_validation_failure: bool
    ohe_columns: list
    test_size: float
    model_name: str
    model_path: Optional[str]
    train_set: Optional[str]
    test_set: Optional[str]
    

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
    
    
def load_config(config_path: str = "config.yaml") -> Config:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return Config(**config)