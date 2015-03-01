import sqlparse

class STATES():
    SELECT = 0
    COLUMNS = 1
    FROM = 2
    TABLE = 3
    LIMIT = 4
    END = 5


def sql(query, tables):
    statement = sqlparse.parse(query)[0]

    state = STATES.SELECT
    df = None
    columns = None

    for token in statement.tokens:
        if token.is_whitespace():
            pass

        elif token.ttype == sqlparse.tokens.DML:
            assert token.value.upper() == "SELECT"
            assert state == STATES.SELECT
            state = STATES.COLUMNS

        elif token.ttype == sqlparse.tokens.Wildcard:
            assert state == STATES.COLUMNS
        elif state == STATES.COLUMNS and is_identifier(token):
            columns = [token.get_name()]
        elif state == STATES.COLUMNS and is_identifierlist(token):
            columns = [col.get_name() for col in token.get_identifiers()]

        elif is_keyword(token, "FROM"):
            assert state == STATES.COLUMNS
            state = STATES.TABLE

        elif state == STATES.TABLE and is_identifier(token):
            table_name = token.get_name()
            df = tables[table_name]
            if columns:
                df = df[columns]

        elif is_where(token):
            df = df[where_to_filter(df, token)]

        elif is_keyword(token, "LIMIT"):
            assert state == STATES.TABLE
            state = STATES.LIMIT
        elif state == STATES.LIMIT:
            limit = token_value(token)
            df = df.head(limit)
            state = None

        elif token.ttype == sqlparse.tokens.Punctuation:
            state = STATES.END

        else:
            raise ValueError(u"Could not parse token %r in statement %r" %
                (token, statement))
    return df


def where_to_filter(df, where):
    agg_filter = None
    combine_function = None

    for token in where.tokens:
        if is_keyword(token, "WHERE"):
            pass
        elif token.is_whitespace():
            pass
        elif token.ttype == sqlparse.tokens.Punctuation:
            pass
        elif isinstance(token, sqlparse.sql.Comparison):
            if combine_function == None:
                agg_filter = comparison_to_filter(df, token)
            else:
                agg_filter = combine_function(
                    agg_filter, comparison_to_filter(df, token))
                combine_function = None
        elif is_keyword(token, "AND"):
            combine_function = lambda a, b: a & b
        elif is_keyword(token, "OR"):
            combine_function = lambda a, b: a | b
        else:
            raise ValueError("Could not parse token %r in WHERE clause %r" %
                (token, where))
    return agg_filter


def comparison_to_filter(df, comparison):
    column = df[comparison.left.value]
    value = token_value(comparison.right)
    symbol = filter(is_comparison, comparison.tokens)[0]
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
