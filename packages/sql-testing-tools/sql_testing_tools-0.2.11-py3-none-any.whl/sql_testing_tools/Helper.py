try:
    import BaseAccess as Ba
    import TokenProcessing as Tp
except ImportError:
    from . import BaseAccess as Ba
    from . import TokenProcessing as Tp

import requests
import sqlparse

from sqlparse.sql import Identifier, IdentifierList, Where, Comparison, Function, Parenthesis
from sqlparse.tokens import Keyword, DML, Name, Wildcard


sql = ""
sol = ""
bd = None

def setup(sqlPath,solPath):
    global sql, sol, bd    
    if(bd == None):
        bd = Ba.getTableDict()
    if(sqlPath and sqlPath != ""):
        sql = normalizeSQLQuery(Ba.getSQLFromFile(sqlPath), bd)
    if(solPath and solPath != ""):
        sol = normalizeSQLQuery(Ba.getSQLFromFile(solPath), bd)
    if(sql=='' or sol==''):
        raise Exception("\n\nSQL-Datei ist leer. Aufgabe wurde noch nicht bearbeitet.")
    

def normalizeSQLQuery(query, baseDict):
    try:
        query = query.replace("\"", "'")
        parsed = sqlparse.parse(query)[0]
        parsed.tokens = [token for token in parsed.tokens if not token.is_whitespace]
    except Exception as e:
        raise Exception(f"\nSyntax-Fehler in der SQL-Abfrage.")

    formatted_query = []
    alias_map = {}

    # First pass to process FROM clause and populate alias_map
    for token in parsed.tokens:
        if token.is_whitespace:
            continue
        elif token.ttype is Keyword and token.value.upper() == 'FROM':
            formatted_query.append('FROM')
            pass
        elif isinstance(token, Identifier) and formatted_query and formatted_query[-1] == 'FROM':
            il = IdentifierList([token])
            formatted_query.append(Tp._from(il, alias_map, baseDict))
            Tp._from(il, alias_map, baseDict)
        elif isinstance(token, IdentifierList) and formatted_query and formatted_query[-1] == 'FROM':
            formatted_query.append(Tp._from(token, alias_map, baseDict))
            Tp._from(token, alias_map, baseDict)

    formatted_query = []

    # Second pass to process SELECT, WHERE, GROUP BY, ORDER BY, and LIMIT clauses
    for token in parsed.tokens:
        if token.is_whitespace:
            continue
        elif token.ttype is DML and token.value.upper() == 'SELECT':
            formatted_query.append('SELECT')
        elif token.ttype is Keyword and token.value.upper() == 'FROM':
            formatted_query.append('FROM')  
        elif token.ttype is Keyword and token.value.upper() == 'GROUP BY':
            formatted_query.append('GROUP BY')
        elif token.ttype is Keyword and token.value.upper() == 'ORDER BY':
            formatted_query.append('ORDER BY')
        elif token.ttype is Keyword and token.value.upper() == 'LIMIT':
            formatted_query.append('LIMIT')
        elif (isinstance(token, IdentifierList) or isinstance(token, Identifier)) and formatted_query and formatted_query[-1] == 'FROM':
            formatted_query.append(Tp._from(token, alias_map, baseDict))
        elif (isinstance(token, IdentifierList) or isinstance(token, Identifier)) and formatted_query and formatted_query[-1] == 'GROUP BY':
            formatted_query.append(Tp._groupby(token, alias_map, baseDict))
        elif (isinstance(token, IdentifierList) or isinstance(token, Identifier)) and formatted_query and formatted_query[-1] == 'ORDER BY':
            formatted_query.append(Tp._orderby(token, alias_map, baseDict))
        elif isinstance(token, Where):
            formatted_query.append('WHERE')
            formatted_query.append(Tp._where(token, alias_map, baseDict))
        elif formatted_query and formatted_query[-1] == 'SELECT' and (isinstance(token, IdentifierList) or isinstance(token, Function) or isinstance(token, Identifier)):
            if isinstance(token, Function):
                token = IdentifierList([token])
            formatted_query.append(Tp._select(token, alias_map, baseDict))
        elif formatted_query and formatted_query[-1] == 'LIMIT':
            formatted_query.append(Tp._limit(token))
        else:
            formatted_query.append(str(token))

    return " ".join(formatted_query)

def findTableForColumn(data_dict, target_value, relevantTables):
    l = []
    for key, value_list in data_dict.items():
        if key.lower() in relevantTables:
            for sublist in value_list:
                if sublist and sublist[0].lower() == target_value.lower():
                    l.append(key)
    if len(l) == 0:
        for key, value_list in data_dict.items():
            for sublist in value_list:
                if sublist and sublist[0].lower() == target_value.lower():
                    l.append(key)
    return l

def getTableScheme(table_name: str, tableDict: dict):
    tab = tableDict[table_name]

    # Format the schema
    schema = "(" + ",".join([f"{col[0]}:{col[1]}" for col in tab]) + ")"
    return schema

def getCosetteKeyFromFile():
    try:
        with open("cosette_apikey.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "NOKEY"

def buildAndSendCosetteRequest(baseDict, sql, sol):

    err = ""
    for i in range(2):
        try:
            apiKey=getCosetteKeyFromFile()


            schema = ""
            for tab in baseDict.keys():
                schema += f"schema sch{tab}{getTableScheme(tab, baseDict)};\n"
            for tab in baseDict.keys():
                schema += f"table {tab}(sch{tab});\n"

            q1 = "query q1\n`"+sql+"`;\n"
            q2 = "query q2\n`"+sol+"`;\n"

            cosette = "-- random Kommentar\n" + schema + q1 + q2 + "verify q1 q2;\n"
            print(cosette)

            r = requests.post("https://demo.cosette.cs.washington.edu/solve",data={"api_key": apiKey, "query": cosette}, verify=False)

            print(r.text)
            return (r.json()['result'],r.text)
            #return r.json()['result']

        except Exception as e:
            err = str(e)
    return ("ERR", err)


def checkKeywords(startWord:str, endWords:list):
    #global sql,sol

    startWord = startWord.lower()

    if(startWord not in sol.lower() and startWord not in sql.lower()):
        return ""

    if(startWord in sql.lower()):
        start = sql.lower().find(startWord) + len(startWord)
        end = -1
        for kw in endWords:
            index = sql.lower().find(kw.lower(), start)
            if -1 < index < end or end == -1:
                end = index
        if(end == -1):
            end = len(sql)

        submission = str.strip(sql[start:end])
        #print("'"+submission+"'")

        start = sol.lower().find(startWord) + len(startWord)
        end = -1
        
        for kw in endWords:
            index = sol.lower().find(kw.lower(), start)
            if -1 < index < end or end == -1:
                end = index
        if(end == -1):
            end = len(sol)

        solution = str.strip(sol[start:end])

        if submission == solution:
            return ""
    return "Der '"+startWord+"' Teil der SQL-Abfrage ist nicht korrekt (oder nicht automatisch überprüfbar)."


def checkColumns(sqlPath="", solPath=""):
    #global sql,sol
    setup(sqlPath, solPath)
    return checkKeywords("SELECT ", ["FROM", "WHERE", "GROUP BY", "ORDER BY", "LIMIT", ";", "HAVING"])


def checkTables(sqlPath="", solPath=""):
    #global sql,sol
    setup(sqlPath, solPath)
    return checkKeywords("FROM ", ["SELECT", "WHERE", "GROUP BY", "ORDER BY", "LIMIT", ";", "HAVING"])


def checkCondition(sqlPath="", solPath=""):
    #global sql,sol
    setup(sqlPath, solPath)
    return checkKeywords("WHERE ", ["SELECT", "FROM", "GROUP BY", "ORDER BY", "LIMIT", ";", "HAVING"])


def checkOrder(sqlPath="", solPath=""):
    #global sql,sol
    setup(sqlPath, solPath)
    return checkKeywords("ORDER BY ", ["SELECT", "WHERE", "GROUP BY", "FROM", "LIMIT", ";", "HAVING"])


def checkGroup(sqlPath="", solPath=""):
    #global sql, sol
    setup(sqlPath, solPath)
    return checkKeywords("GROUP BY ", ["SELECT", "WHERE", "FROM BY", "ORDER BY", "LIMIT", ";", "HAVING"])


def checkEquality(sqlPath="", solPath=""):
    #global sql, sol
    setup(sqlPath, solPath)

    if sql == sol:
        return ""

    result = buildAndSendCosetteRequest(bd, sql, sol)

    if result[0] == "ERR":
        return "\n\nFehler bei der automatischen Überprüfung der Abgabe. Es kann keine Aussage über die Korrektheit der Abgabe getroffen werden."
    elif result[0] != "EQ":
        return "\n\nDie Abgabe stimmt nicht mit der Musterlösung überein."
    return ""


