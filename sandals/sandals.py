import sqlparse

class STATES():
    SELECT = 0
    COLUMNS = 1
    FROM = 2
    TABLE = 3
    LIMIT = 4

def sql(query, tables):
    statement = sqlparse.parse(query)[0]

    state = STATES.SELECT
    df = None
    columns = None

    for token in statement.tokens:
        if token.is_whitespace():
            pass

        elif token.ttype == sqlparse.tokens.DML:
            assert token.value == "SELECT"
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

        elif is_keyword(token, "LIMIT"):
            assert state == STATES.TABLE
            state = STATES.LIMIT
        elif state == STATES.LIMIT:
            limit = int(token.value)
            df = df.head(limit)
            state = None

        else:
            raise ValueError(u"Could not parse token %s in statment %s" %
                (repr(token), repr(statement)))
    return df

def is_keyword(token, keyword):
    return token.is_keyword and token.value.upper() == keyword.upper()

def is_identifier(token):
    return isinstance(token, sqlparse.sql.Identifier)

def is_identifierlist(token):
    return isinstance(token, sqlparse.sql.IdentifierList)
