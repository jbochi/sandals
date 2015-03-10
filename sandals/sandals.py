import sqlparse
import numpy as np


class STATES():
    SELECT = 0
    COLUMNS = 1
    FROM = 2
    TABLE = 3
    GROUP = 4
    ORDER = 5
    LIMIT = 6
    END = 7


def sql(query, tables):
    statement = sqlparse.parse(query)[0]

    state = STATES.SELECT
    df = None
    columns = None
    functions = []

    for token in statement.tokens:
        if token.is_whitespace():
            pass

        #select
        elif token.ttype == sqlparse.tokens.DML:
            assert token.value.upper() == "SELECT"
            assert state == STATES.SELECT
            state = STATES.COLUMNS

        #columns
        elif token.ttype == sqlparse.tokens.Wildcard:
            assert state == STATES.COLUMNS
        elif state == STATES.COLUMNS and is_identifier(token):
            columns = [token.get_name()]
        elif state == STATES.COLUMNS and is_identifierlist(token):
            columns = [col.get_name()
                for col in token.get_identifiers() if is_identifier(col)]
            functions = [f for f in token.get_identifiers() if is_function(f)]
        elif is_keyword(token, "FROM"):
            assert state == STATES.COLUMNS
            state = STATES.TABLE

        #table
        elif state == STATES.TABLE and is_identifier(token):
            table_name = token.get_name()
            df = tables[table_name]
            if columns and not functions:
                df = df[columns]

        #where clause
        elif is_where(token):
            df = df[where_to_filter(df, token)]

        #group by
        elif is_keyword(token, "GROUP"):
            assert state == STATES.TABLE
            state = STATES.GROUP
        elif is_keyword(token, "BY") and state == STATES.GROUP:
            pass
        elif state == STATES.GROUP and is_identifier(token):
            df = aggregate(df, columns, functions, [token.get_name()])
        elif state == STATES.GROUP and is_identifierlist(token):
            group_by_cols = [t.get_name() for t in token.tokens
                if is_identifier(t)]
            df = aggregate(df, columns, functions, group_by_cols)

        #order
        elif is_keyword(token, "ORDER"):
            assert state == STATES.TABLE or STATES.GROUP
            state = STATES.ORDER
        elif is_keyword(token, "BY") and state == STATES.ORDER:
            pass
        elif state == STATES.ORDER and is_identifier(token):
            descending = is_order_descending(token)
            df = df.sort(token.get_name(), ascending=not descending)
        elif state == STATES.ORDER and is_identifierlist(token):
            column_identifiers = [t for t in token.tokens if is_identifier(t)]
            column_names = [c.get_name() for c in column_identifiers]
            orders = [0 if is_order_descending(c) else 1
                for c in column_identifiers]
            df = df.sort(column_names, ascending=orders)

        #limit
        elif is_keyword(token, "LIMIT"):
            assert state == STATES.TABLE or STATES.GROUP or STATES.ORDER
            state = STATES.LIMIT
        elif state == STATES.LIMIT:
            limit = token_value(token)
            df = df.head(limit)
            state = None

        #end
        elif token.ttype == sqlparse.tokens.Punctuation:
            state = STATES.END

        else:
            raise ValueError("Could not parse token %r in statement %r" %
                (token, statement))
    return df


def where_to_filter(df, where):
    agg_filter = None
    combine_function = lambda a, b: b
    column = None

    for token in where.tokens:
        if is_keyword(token, "WHERE"):
            pass
        elif token.is_whitespace():
            pass
        elif token.ttype == sqlparse.tokens.Punctuation:
            pass
        elif isinstance(token, sqlparse.sql.Comparison):
            agg_filter = combine_function(
                agg_filter,
                comparison_to_filter(df, token))
        elif is_keyword(token, "AND"):
            combine_function = lambda a, b: a & b
        elif is_keyword(token, "OR"):
            combine_function = lambda a, b: a | b
        elif is_identifier(token):
            column = select_column(df, token)
        elif is_keyword(token, "IS"):
            pass
        elif is_keyword(token, "NOT NULL"):
            agg_filter = combine_function(agg_filter, column.notnull())
        elif is_keyword(token, "NULL"):
            agg_filter = combine_function(agg_filter, column.isnull())
        else:
            raise ValueError("Could not parse token %r in WHERE clause %r" %
                (token, where))
    return agg_filter


def comparison_to_filter(df, comparison):
    column = select_column(df, comparison.left)
    value = token_value(comparison.right)
    symbol = [t for t in comparison.tokens if is_comparison(t)][0]
    if symbol.value == "=":
        return column == value
    if symbol.value == ">":
        return column > value
    if symbol.value == ">=":
        return column >= value
    if symbol.value == "<":
        return column < value
    if symbol.value == "<=":
        return column <= value
    raise ValueError("Unknown comparison symbol: %r" % symbol)


def is_keyword(token, keyword):
    return token.is_keyword and token.value.upper() == keyword.upper()


def is_identifier(token):
    return isinstance(token, sqlparse.sql.Identifier)


def is_identifierlist(token):
    return isinstance(token, sqlparse.sql.IdentifierList)


def is_where(token):
    return isinstance(token, sqlparse.sql.Where)


def is_comparison(token):
    return token.ttype == sqlparse.tokens.Token.Operator.Comparison


def is_function(token):
    return isinstance(token, sqlparse.sql.Function)


def token_value(token):
    value = token.value
    repr_name = token._get_repr_name()
    if repr_name == "Single" or repr_name == "Identifier":
        if value.startswith('"'):
            return value.strip('"')
        elif value.startswith("'"):
            return value.strip("'")
        return value
    elif repr_name == "Integer":
        return int(value)
    elif repr_name == "Float":
        return float(value)
    raise ValueError("Unknown token value %r" % token)


def select_column(df, token):
    column_name = token.value
    if "." in column_name:
        table_name, column_name = column_name.split(".", 1)
        #TODO: Assert table name is correct
    #TODO: Catch KeyError exception and raise error saying column does not exist
    return df[column_name]


def aggregate(df, columns, functions, group_by_cols):
    agg_dict = dict(agg_tuple(f, group_by_cols) for f in functions)
    res = df.groupby(group_by_cols).agg(agg_dict)
    return res


def agg_tuple(f, group_by_cols):
    # Returns tupple (column, function) for aggregation
    return (column_from_function(f, group_by_cols),
            function_from_name(f.get_name()))


def column_from_function(f, group_by_cols):
    function_args = f.tokens[1].tokens[1]
    if function_args.ttype == sqlparse.tokens.Token.Wildcard:
        return group_by_cols[0]
    return function_args.value


def function_from_name(function_name):
    if function_name.upper() == "AVG":
        return np.mean
    elif function_name.upper() == "COUNT":
        return np.size
    raise ValueError("Unknown function %f" % function_name)


def is_order_descending(token):
    return any(t.value == "DESC" for t in token.tokens if
        t.ttype == sqlparse.tokens.Token.Keyword.Order)
