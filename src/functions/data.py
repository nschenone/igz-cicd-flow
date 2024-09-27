import mlrun
import pandas as pd
import pandera as pa
from pandera.typing import DataFrame
from sklearn.compose import make_column_transformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

from src.functions.models import HeartSchema


@mlrun.handler(outputs=["data"])
@pa.check_types(lazy=True)
def get_data(data: pd.DataFrame) -> DataFrame[HeartSchema]:
    # Alternatively
    # HeartSchema.validate(data, lazy=True)
    return data.copy()


@mlrun.handler(outputs=["train", "test", "preprocessor:object"])
def process_data(
    data: pd.DataFrame,
    label_column: str,
    test_size: float,
    ohe_columns: list = None,
    random_state: int = 42,
):
    train, test = train_test_split(data, test_size=test_size, random_state=random_state)

    ohe_columns = ohe_columns if ohe_columns else []
    preprocessor = make_pipeline(
        make_column_transformer(
            (OneHotEncoder(sparse=False), ohe_columns),
            remainder="passthrough",
            verbose_feature_names_out=False,
        )
    )

    preprocessor.fit(train)

    # Sklearn pipeline outputs numpy array - convert back to dataframe
    train = pd.DataFrame(
        data=preprocessor.transform(train), columns=preprocessor.get_feature_names_out()
    )
    test = pd.DataFrame(
        data=preprocessor.transform(test), columns=preprocessor.get_feature_names_out()
    )

    return train, test, preprocessor
