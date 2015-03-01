import pandas
import pytest
import sandals


@pytest.fixture
def tips():
    return pandas.read_csv("tests/data/tips.csv")


def test_select(tips):
    result = sandals.sql("SELECT * FROM tips", locals())
    assert result.shape == tips.shape


def test_select_should_accept_trailing_semicolon(tips):
    result = sandals.sql("SELECT * FROM tips;", locals())
    assert result.shape == tips.shape


def test_select_should_accept_line_break(tips):
    result = sandals.sql("SELECT * \n FROM tips;", locals())
    assert result.shape == tips.shape


def test_select_is_case_insensitive(tips):
    result = sandals.sql("select * from tips;", locals())
    assert result.shape == tips.shape


def test_select_with_limit(tips):
    result = sandals.sql("SELECT * FROM tips LIMIT 5", locals())
    assert result.shape[0] == 5
    assert result.shape[1] == tips.shape[1]


def test_select_with_limit_is_case_insensitive(tips):
    result = sandals.sql("SELECT * from tips limit 5", locals())
    assert result.shape[0] == 5
    assert result.shape[1] == tips.shape[1]


def test_single_column_selection(tips):
    result = sandals.sql("SELECT sex FROM tips", locals())
    assert list(result.columns.values) == ["sex"]
    assert result.shape[0] == tips.shape[0]


def test_column_selection(tips):
    result = sandals.sql("SELECT total_bill, sex FROM tips", locals())
    assert list(result.columns.values) == ["total_bill", "sex"]
    assert result.shape[0] == tips.shape[0]


def test_where(tips):
    result = sandals.sql(
        "SELECT * FROM tips WHERE time = 'Dinner'", locals())
    assert result.shape == tips[tips["time"] == "Dinner"].shape


def test_where_with_double_quote(tips):
    result = sandals.sql(
        'SELECT * FROM tips WHERE time = "Dinner"', locals())
    assert result.shape == tips[tips["time"] == "Dinner"].shape


def test_where_with_greater_than(tips):
    result = sandals.sql(
        'SELECT * FROM tips WHERE tip > 5.0', locals())
    assert result.shape == tips[tips["tip"] > 5.0].shape


def test_where_with_greater_or_eq_than(tips):
    result = sandals.sql(
        'SELECT * FROM tips WHERE tip >= 5.0', locals())
    assert result.shape == tips[tips["tip"] >= 5.0].shape


def test_where_with_less_than(tips):
    result = sandals.sql(
        'SELECT * FROM tips WHERE tip < 5.0', locals())
    assert result.shape == tips[tips["tip"] < 5.0].shape


def test_where_with_less_or_eq_than(tips):
    result = sandals.sql(
        'SELECT * FROM tips WHERE tip <= 5.0', locals())
    assert result.shape == tips[tips["tip"] <= 5.0].shape


def test_where_with_eq(tips):
    result = sandals.sql(
        'SELECT * FROM tips WHERE tip = 5', locals())
    assert result.shape == tips[tips["tip"] == 5].shape

def test_where_with_and(tips):
    result = sandals.sql(
        "SELECT * FROM tips WHERE time = 'Dinner' AND tip > 5.00;", locals())
    expected = tips[(tips["tip"] > 5) & (tips["time"] == "Dinner")]
    assert result.shape == expected.shape
