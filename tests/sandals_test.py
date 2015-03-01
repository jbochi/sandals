import pandas
import pytest
import sandals


@pytest.fixture
def tips():
    return pandas.read_csv("tests/data/tips.csv")


def test_select(tips):
    result = sandals.sql("SELECT * from tips", locals())
    assert result.shape == tips.shape


def test_select_with_limit(tips):
    result = sandals.sql("SELECT * FROM tips LIMIT 5", locals())
    assert result.shape[0] == 5
    assert result.shape[1] == tips.shape[1]


def test_select_with_limit_is_case_insensitive(tips):
    result = sandals.sql("SELECT * from tips limit 5", locals())
    assert result.shape[0] == 5
    assert result.shape[1] == tips.shape[1]
