import sqlparse
from sqlparse.sql import Identifier, IdentifierList, Where, Comparison, Function, Parenthesis, Token
from sqlparse.tokens import Keyword, DML, Name, Wildcard, Whitespace, Newline

try:
    import Helper as He
except ImportError:
    from . import Helper as He

        
#####################################
#####################################

def _identifier(identifier, alias_map, baseDict: dict):
        if isinstance(identifier, Identifier):
            if identifier.get_real_name() and identifier.get_parent_name() and identifier.get_parent_name().lower() in alias_map.keys():
                return f"{alias_map[identifier.get_parent_name().lower()].lower()}.{identifier.get_real_name().lower()}"
            elif identifier.get_real_name():
                tables = He.findTableForColumn(baseDict, identifier.get_real_name(), alias_map.keys())
                if len(tables) == 1:
                    alias_map[tables[0].lower()] = tables[0]
                    return f"{tables[0].lower()}.{identifier.get_real_name().lower()}"
                else:
                    return f"{identifier.get_real_name().lower()}"
        return str(identifier)

        
#####################################
#####################################


def _select(select, alias_map, baseDict: dict, insideFunction=False):
    select_tokens = []
    for token in select.tokens:
        if isinstance(token, IdentifierList):
            for identifier in token.get_identifiers():
                select_tokens.append(f"{_identifier(identifier, alias_map, baseDict).lower()} as {identifier.get_real_name().lower()}")
        elif isinstance(token, Identifier):
            if insideFunction:
                select_tokens.append(_identifier(token, alias_map, baseDict).lower())
            else:
                select_tokens.append(f"{_identifier(token, alias_map,  baseDict).lower()} as {token.get_real_name().lower()}")
        elif isinstance(token, Function):
            #select_tokens.append(f"{token.get_name().lower()}({_identifier(token.get_parameters(), alias_map, baseDict).lower()})")
            for par in token.tokens:
                if isinstance(par, Identifier):
                    select_tokens.append(par.get_name().lower()+"(")
                if isinstance(par, Parenthesis):
                    select_tokens[-1] += _select(par, alias_map, baseDict, True)+") as funcResult" 
        elif token.ttype is Wildcard:
            select_tokens.append("*")
        else:
            continue
    select_tokens.sort()
    return ",".join(select_tokens)


#####################################
#####################################


def _from(from_, alias_map, baseDict: dict):
    from_tokens = []
    if hasattr(from_, 'tokens'):
        for token in from_.tokens:
            if isinstance(token, IdentifierList):
                for identifier in token.get_identifiers():
                    alias_map[identifier.get_real_name().lower()] = identifier.get_alias() or identifier.get_real_name()
                    from_tokens.append(f"{identifier.get_real_name().lower()} {alias_map[identifier.get_real_name().lower()].lower()}")
            elif isinstance(token, Identifier):
                alias_map[token.get_real_name().lower()] = token.get_alias() or token.get_real_name()
                from_tokens.append(f"{token.get_real_name().lower()} {alias_map[token.get_real_name().lower()].lower()}")
            elif token.ttype is not None and token.ttype is Name:
                alias_map[token.value.lower()] = token.value.lower()
                from_tokens.append(f"{token.value.lower()} {alias_map[token.value.lower()].lower()}")
            else:
                continue
    from_tokens.sort()
    return ",".join(from_tokens)


#####################################
#####################################


def _groupby(groupby_, alias_map, baseDict: dict):
    groupby_tokens = []
    if(isinstance(groupby_, Identifier)):
        groupby_tokens.append(_identifier(groupby_, alias_map, baseDict).lower())
    elif isinstance(groupby_, IdentifierList):
        for identifier in groupby_.get_identifiers():
            groupby_tokens.append(_identifier(identifier, alias_map, baseDict).lower())
    groupby_tokens.sort()
    return ",".join(groupby_tokens)

def _orderby(orderby_, alias_map, baseDict: dict):
    orderby_tokens = []
    if isinstance(orderby_, Identifier):
        if len(orderby_.tokens) > 0 and orderby_.tokens[-1].ttype==Keyword.Order:
            for tok in orderby_.tokens:
                if isinstance(tok, Identifier):
                    orderby_tokens.append(_identifier(tok, alias_map, baseDict).lower())
                if tok.ttype==Keyword.Order:
                    orderby_tokens[-1] += (" "+tok.value)
        else:
            orderby_tokens.append(_identifier(orderby_, alias_map, baseDict).lower())
            orderby_tokens[-1] += " ASC"
    elif isinstance(orderby_, IdentifierList):
        for tok in orderby_.tokens:
            if isinstance(tok, Identifier):
                orderby_tokens.append(_identifier(tok, alias_map, baseDict).lower())
    #elif isinstance(orderby_, Order):
    #    pass
   # orderby_tokens.sort()
    return ",".join(orderby_tokens)

def replace_not_with_parenthesis(where_tokens):
    new_tokens = []
    i = 0
    while i < len(where_tokens):
        if where_tokens[i].ttype is Keyword and where_tokens[i].value.upper() == "NOT":
            if i + 1 < len(where_tokens):
                not_token = where_tokens[i]
                next_token = where_tokens[i + 1]
                parenthesis = Parenthesis([not_token, Token(Whitespace, ' '), next_token])
                new_tokens.append(parenthesis)
                i += 2  # Skip the next token as it is already added inside the parenthesis
            else:
                new_tokens.append(where_tokens[i])
                i += 1
        else:
            new_tokens.append(where_tokens[i])
            i += 1
    return new_tokens

def _condition(token, alias_map, baseDict: dict):
    left, operator, right = [t for t in token.tokens if not t.is_whitespace]

    flipAllowed = True
    leftLiteral = False
    rightLiteral = False

    if is_value(right):
        flipAllowed = False
        rightLiteral = True

    if is_value(left):
        left, right = right, left
        if operator.value == ">":
            operator.value = "<"
        elif operator.value == "<":
            operator.value = ">"
        elif operator.value == ">=":
            operator.value = "<="
        elif operator.value == "<=":
            operator.value = ">="
        leftLiteral = rightLiteral
        rightLiteral = True
        flipAllowed = False

    left = _identifier(left, alias_map, baseDict)
    right = _identifier(right, alias_map, baseDict)

    if operator.value.strip() in ("!=", "<>"):
        return f"(NOT {left.lower()} LIKE {right})"
    if operator.value.lower().strip() == "not like":
        return f"(NOT {left.lower()} LIKE {right})"
    if operator.value.strip() == "=" and rightLiteral and "%" not in right and "_" not in right:
        return f"{left.lower()} LIKE {right}" # less strict testing allowing minor deviations in upper/lower case



    if flipAllowed and left.lower() >= right.lower():
        left, right = right, left
        if operator.value == ">":
            operator = "<"
        elif operator.value == "<":
            operator = ">"
        if operator.value == ">=":
            operator = "<="
        elif operator.value == "<=":
            operator = ">="

    return f"{left if leftLiteral else left.lower()} {operator.value.upper()} {right if rightLiteral else right.lower()}"

def is_value(token):
    return token.ttype in (sqlparse.tokens.Token.Literal.Number.Integer,
                            sqlparse.tokens.Token.Literal.Number.Float,
                            sqlparse.tokens.Token.Literal.String.Single,
                            sqlparse.tokens.Token.Literal.String.Symbol)



#####################################
#####################################


def _paranthesis(parenthesis, alias_map, baseDict: dict):
    toks = []

    bracketsRequired = True
    closeBracketsAfterNext = False

    and_count = sum(1 for token in parenthesis.tokens if token.ttype is Keyword and token.value == "AND")  # Zähle "AND"-Tokens
    or_count = sum(1 for token in parenthesis.tokens if token.ttype is Keyword and token.value == "OR")  # Zähle "AND"-Tokens


    if(and_count==1 and or_count == 0):
        val = _2element_par(parenthesis, alias_map, baseDict, "AND")
        return val
    elif(and_count==0 and or_count == 1):
        val = _2element_par(parenthesis, alias_map, baseDict, "OR")
        return val






    for token in parenthesis.tokens:
        if isinstance(token, Comparison):
            toks.append(_condition(token, alias_map, baseDict))
        elif isinstance(token, Parenthesis):
            toks.append(_paranthesis(token, alias_map, baseDict))

        elif token.ttype is Keyword: #AND,OR
            if token.value == "AND":
                pass
            elif token.value == "OR":
                pass
            elif token.value == "NOT":
                pass

        elif token.value == '(':
            toks.append(token.value)
        else:
            continue
    x = parenthesis.flatten()
    return " ".join(toks)


def _2element_par(parenthesis, alias_map, baseDict: dict, keyword):
    toks = []

    for token in parenthesis.tokens:
        if isinstance(token, Comparison):
            toks.append(_condition(token, alias_map, baseDict))
        elif isinstance(token, Parenthesis):
            toks.append(_paranthesis(token, alias_map, baseDict))
    toks = toks.sort()
    fill = (" "+keyword+" ")
    return fill.join(toks)


def count_keywordValues(tokens, values):
    return len([token for token in tokens if token.ttype is Keyword and token.value.upper() in values])


def find_index_of_keyword(tokens, keyword):
    for index, token in enumerate(tokens):
        if token.ttype is Keyword and token.value.upper() == keyword:
            return index
    return -1  # Wenn kein AND-Token gefunden wird


def _where(where, alias_map, baseDict: dict):
    conditions = []
    current_condition = []



    isParanthesis = isinstance(where, Parenthesis)
    
    where_tokens = [token for token in where.tokens if (token.ttype is not Whitespace and token.ttype is not Newline) and token.value != "WHERE"]
    where_tokens = replace_not_with_parenthesis(where_tokens)

    # No parentheses in where_string!
    where_string = " ".join([str(token) for token in where_tokens])

    and_count = where_string.upper().count(" AND ")
    or_count = where_string.upper().count(" OR ")

    # No AND / OR
    if and_count + or_count == 0:
        return _where_simpleCondition(where, alias_map, baseDict)

    # only ANDs / only ORs
    elif and_count == 0 or or_count == 0:
        return _where_sameStrengthKeywords(where_tokens, alias_map, baseDict, " AND " if and_count > 0 else " OR ")
    
    # ANDs and ORs


    # count keywords on top level
    top_and_count = count_keywordValues(where_tokens, ["AND"])
    top_or_count = count_keywordValues(where_tokens, ["OR"])

    # two conditions on top level
    if top_and_count + top_or_count == 1:
        keyword = " AND " if top_and_count == 1 else " OR "
        return _where_twoConditionsOnTopLevel(where, alias_map, baseDict, keyword, isParanthesis)
    else:
        where_tokens = _where_addBracketsAroundAND(where, alias_map, baseDict)
        return _where(Where(where_tokens), alias_map, baseDict)

def _where_addBracketsAroundAND(where, alias_map, baseDict: dict):
    index = find_index_of_keyword(where.tokens, "AND")
    par = Parenthesis(where.tokens[index-2:index+3])
    where_tokens = where.tokens[:index-2] + [par] + where.tokens[index+3:]
    return where_tokens



    # for token in where.tokens:
    #     if token.is_whitespace or (token.ttype is Keyword and token.value.upper() == "WHERE"):
    #         continue

    #     if token.ttype is Keyword and token.value.upper() in ('AND', 'OR'):
    #         if current_condition:
    #             conditions.append(''.join(str(t) for t in current_condition).strip())
    #             current_condition = []
    #         conditions.append(token.value.upper())
    #     else:
    #         current_condition.append(token)

    # if current_condition:
    #     conditions.append(''.join(str(t) for t in current_condition).strip())

    # sorted_conditions = []
    # current_group = []
    # last_connector = ""

    # if "OR" not in conditions:
    #     for condition in conditions:
    #         if condition == 'AND':
    #             pass
    #         else:
    #             current_group.append(condition)

    #     if current_group:
    #         sorted_conditions.extend(sorted(current_group))

    #     return " AND ".join(sorted_conditions)
    # else:
    #     return " ".join(conditions)

    #     where_index = query.upper().find('WHERE')
        
    #     normalized_query = query[:where_index + 5] + ' ' + ' '.join(sorted_conditions)



def _where_simpleCondition(where_tokens, alias_map, baseDict: dict):
    cond = []
    for tok in where_tokens:
        if tok.ttype == Keyword and tok.value.upper() == "NOT":
            cond.append("NOT ")
        if isinstance(tok, Comparison):
            cond.append(_condition(tok, alias_map, baseDict))
        elif isinstance(tok, Parenthesis):
            for _tok in tok.tokens:
                if isinstance(_tok, Comparison):
                    cond.append(_condition(_tok, alias_map, baseDict))
                elif isinstance(_tok, Parenthesis):
                    tok = _tok
    return "".join(cond)

def _where_sameStrengthKeywords(where_tokens, alias_map, baseDict: dict, keyword: str):
    cond = []
    for tok in where_tokens:
        if isinstance(tok, Comparison):
            cond.append(_where_simpleCondition([tok], alias_map, baseDict))
        elif isinstance(tok, Parenthesis):
            isNot = tok.tokens[0].ttype == Keyword and tok.tokens[0].value.upper() == "NOT"
            cond.append(("(" if isNot else "") + _where(tok, alias_map, baseDict) + (")" if isNot else ""))
    cond.sort()
    return keyword.join(cond)

def _where_twoConditionsOnTopLevel(where, alias_map, baseDict: dict, keyword, isParanthesis):
    current_condition = []
    for tok in where.tokens:
        if isinstance(tok, Comparison):
            current_condition.append(_condition(tok, alias_map, baseDict))
        elif isinstance(tok, Parenthesis):
            current_condition.append(_where(tok, alias_map, baseDict))
        current_condition.sort()
        if keyword == " AND " or isParanthesis:
            return "(" + keyword.join(current_condition) + ")"
        else:
            return keyword.join(current_condition)


def _limit(limit):
    return str(limit).strip()
