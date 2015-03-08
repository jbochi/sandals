import pandas as pd
import numpy as np
import pytest
import sandals


@pytest.fixture
def tips():
    return pd.read_csv("tests/data/tips.csv")


# SIMPLE SELECT


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


# LIMIT


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


def test_qualified_column_selection(tips):
    result = sandals.sql("SELECT tips.total_bill, sex FROM tips", locals())
    assert list(result.columns.values) == ["total_bill", "sex"]
    assert result.shape[0] == tips.shape[0]


@pytest.mark.xfail
def test_qualified_column_selection_with_wrong_table_name(tips):
    result = sandals.sql("SELECT asdf.total_bill, sex FROM tips", locals())
    #TODO: Should fail



# WHERE

def test_where(tips):
    result = sandals.sql(
        "SELECT * FROM tips WHERE time = 'Dinner'", locals())
    assert result.shape == tips[tips["time"] == "Dinner"].shape


def test_where_with_double_quote(tips):
    result = sandals.sql(
        'SELECT * FROM tips WHERE time = "Dinner"', locals())
    assert result.shape == tips[tips["time"] == "Dinner"].shape


def test_where_with_table_name(tips):
    result = sandals.sql(
        "SELECT * FROM tips WHERE tips.time = 'Dinner'", locals())
    assert result.shape == tips[tips["time"] == "Dinner"].shape


@pytest.mark.xfail
def test_where_with_wrong_table_name(tips):
    result = sandals.sql(
        "SELECT * FROM tips WHERE asdf.time = 'Dinner'", locals())


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


def test_where_with_or(tips):
    result = sandals.sql(
        "SELECT * FROM tips WHERE tip >= 5 OR total_bill > 45;", locals())
    expected = tips[(tips["tip"] >= 5) | (tips["total_bill"] > 45)]
    assert result.shape == expected.shape


def test_where_with_special_col_name(tips):
    result = sandals.sql(
        "SELECT * FROM tips WHERE tips.size >= 5 OR total_bill > 45;", locals())
    expected = tips[(tips["size"] >= 5) | (tips["total_bill"] > 45)]
    assert result.shape == expected.shape


def test_where_is_null():
    frame = pd.DataFrame({'col1': ['A', 'B', np.NaN, 'C', 'D'],
                          'col2': ['F', np.NaN, 'G', 'H', 'I']})
    result = sandals.sql("SELECT * FROM frame WHERE col2 IS NULL;", locals())
    expected = frame[frame['col2'].isnull()]
    assert result.shape == expected.shape


def test_where_is_null_with_or():
    frame = pd.DataFrame({'col1': ['A', 'B', np.NaN, 'C', 'D'],
                          'col2': ['F', np.NaN, 'G', 'H', 'I']})
    result = sandals.sql(
        "SELECT * FROM frame WHERE col2 IS NULL OR col1 = 'C';", locals())
    expected = frame[(frame['col1'] == 'C') | (frame['col2'].isnull())]
    assert result.shape == expected.shape


def test_where_is_not_null():
    frame = pd.DataFrame({'col1': ['A', 'B', np.NaN, 'C', 'D'],
                          'col2': ['F', np.NaN, 'G', 'H', 'I']})
    result = sandals.sql("SELECT * FROM frame WHERE col2 IS NOT NULL;", locals())
    expected = frame[frame['col2'].notnull()]
    assert result.shape == expected.shape


# GROUP BY

def test_group_by(tips):
    result = sandals.sql(
        "SELECT sex, count(*) FROM tips GROUP BY sex;", locals())
    expected = tips.groupby('sex').size()
    assert result.columns == ["sex"]
    assert result["sex"]["Female"] == expected["Female"]
    assert result["sex"]["Male"] == expected["Male"]


def test_group_by_with_multiple_functions(tips):
    result = sandals.sql(
        "SELECT tips.day, AVG(tip), COUNT(*) FROM tips GROUP BY tips.day;", locals())
    expected = tips.groupby('day').agg({'tip': np.mean, 'day': np.size})
    assert result.shape == expected.shape
    assert result["tip"]["Fri"] == expected["tip"]["Fri"]
    assert result["day"]["Sun"] == expected["day"]["Sun"]


# ORDER BY

def test_order_by(tips):
    result = sandals.sql("SELECT * FROM tips ORDER BY total_bill LIMIT 3", locals())
    expected = tips.sort("total_bill")[:3]
    assert result.shape == expected.shape
    assert result.iloc[0]["total_bill"] == expected.iloc[0]["total_bill"]

def test_order_by_desc(tips):
    result = sandals.sql("SELECT * FROM tips ORDER BY total_bill DESC LIMIT 3", locals())
    expected = tips.sort("total_bill", ascending=False)[:3]
    assert result.shape == expected.shape
    assert result.iloc[0]["total_bill"] == expected.iloc[0]["total_bill"]
