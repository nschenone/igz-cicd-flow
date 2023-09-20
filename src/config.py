from typing import Optional

from pydantic import BaseModel, BaseSettings


class Config(BaseSettings):
    # Project
    project_name: str = "cicd-flow"
    local_source: str = "v3io:///bigdata/cicd-flow.zip"
    git_repo: str = "git://github.com/igz-us-sales/igz-cicd-flow"
    git_branch: str = "master"
    
    # Workflow parameters
    source_url: str = "./data/heart.csv"
    label_column: str = "target"
    allow_validation_failure: bool = True
    ohe_columns: list = ["sex", "cp", "slope", "thal", "restecg"]
    test_size: float = 0.1
    deploy_model_name: str = "model"
    deploy_condition_metric: str = "evaluation_accuracy"
    force_deploy: bool = False
    
    # Artifacts
    challenger_model_tag: str = "challenger"
    champion_model_tag: str = "champion"

    
    @property
    def git_source(self):
        return f"{self.git_repo}#{self.git_branch}"
    

class TrainConfig(BaseModel):
    source_url: str
    label_column: str
    allow_validation_failure: bool
    ohe_columns: list
    test_size: float

    
class DeployConfig(BaseModel):
    challenger_model_tag: str
    champion_model_tag: str
    label_column: str
    deploy_model_name: str
