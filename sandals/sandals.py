import sqlparse

class STATES():
    LIMIT = 1


def sql(query, tables):
    stmt = sqlparse.parse(query)[0]
    assert stmt.get_type() == "SELECT"

    state = None
    df = None

    for token in stmt.tokens:
        if isinstance(token, sqlparse.sql.Identifier):
            table_name = token.get_name()
            df = tables[table_name]
        elif token.is_keyword and token.value == "LIMIT":
            state = STATES.LIMIT
        elif state == STATES.LIMIT and not token.is_whitespace():
            limit = int(token.value)
            df = df.head(limit)
            state = None
        else:
            print repr(token), state, token.is_whitespace()

    return df
