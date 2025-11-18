import copy
import csv
from typing import List
from pathlib import Path
from fhirclient.models.coding import Coding
from cumulus_library_kidney_transplant import guard, filetool
from cumulus_library_kidney_transplant.study_prefix import PREFIX
from cumulus_library_kidney_transplant.variable.aspect import AspectKey
from cumulus_library_kidney_transplant.filetool import save_athena_view

###############################################################################
#
# naming conventions
#
###############################################################################
def name_prefix(table: list | str) -> list | str:
    if guard.is_list(table):
        return [f'{PREFIX}__{table}' for table in guard.as_list_unique(table)]
    else:
        return f'{PREFIX}__{table}'

def name_suffix(name: str, suffix=None) -> str:
    return f'{name}_{suffix}' if suffix else name

def name_simple(table) -> str:
    simple = table
    for part in ['cohort_', 'count_', 'valueset_']:
        simple = simple.replace(name_prefix(part), '')
    return simple.replace(name_prefix(''), '')

def name_join(part: str, table: str) -> str:
    return name_prefix('_'.join([part, name_simple(table)]))

def name_sample(table: str, suffix=None) -> str:
    part = name_suffix('sample', suffix)
    return name_join(part, table)

def name_cohort(table: str, suffix=None) -> str:
    part = name_suffix('cohort', suffix)
    return name_join(part, table)

def name_study_population(suffix=None) -> str:
    table = name_suffix('study_population', suffix)
    return name_join('cohort', table)

def name_study_variables(suffix=None) -> str:
    table = name_suffix('study_variables', suffix)
    return name_join('cohort', table)

def name_cube(table: str, suffix: str = None) -> str:
    part = f'count_{suffix}' if suffix else 'count'
    return name_join(part, table)

def name_valueset(table: str, suffix=None) -> str:
    part = f'valueset_{suffix}' if suffix else 'valueset'
    return name_join(part, table)

def list_table_aspect(table:str, aspect_list=None) -> List[str]:
    if aspect_list is None:
        aspect_list = AspectKey.list_keys()
    return [f'{table}_{aspect}' for aspect in aspect_list]

###############################################################################
#
# SQL Helper functions
#
###############################################################################
def sql_escape(sql: str) -> str:
    """
    :param sql: SQL potentially containing special chars
    :return: special chars removed like tic(') and semi(;).
    """
    return sql.replace("'", "").replace(";", ".")

def sql_iter(clauses_list, operator=',') -> str:
    if not isinstance(clauses_list, list):
        return sql_iter([clauses_list])
    return f' {operator} \n'.join(sorted(list(set(clauses_list))))

def sql_and(clauses_list) -> str:
    return sql_iter(clauses_list, 'and')

def sql_or(clauses_list) -> str:
    return sql_iter(clauses_list, 'or')

def sql_list(clauses_list) -> str:
    return sql_iter(clauses_list, ',')

def sql_paren(statement: str) -> str:
    return f'({statement})'


###############################################################################
#
# Transforms X->Y
#
###############################################################################

def valueset2codelist(valueset_json: Path | str | dict) -> List[Coding]:
    """
    Obtain a list of Coding "concepts" from a ValueSet.
    This method currently supports only "include" of "concept" defined fields.
    Not supported: recursive fetching of contained ValueSets, which requires UMLS API Key and Wget, etc.

    examples
    https://vsac.nlm.nih.gov/valueset/2.16.840.1.113762.1.4.1146.1629/expansion/Latest
    https://cts.nlm.nih.gov/fhir/res/ValueSet/2.16.840.1.113762.1.4.1146.1629?_format=json

    :param valueset_json: ValueSet file, expecially those provided by NLM/ONC/VSAC
    :return: list of codeable concepts (system, code, display) to include
    """
    if not isinstance(valueset_json, dict):
        valueset_json = filetool.load_valueset(valueset_json)

    parsed = list()
    if not valueset_json.get('compose'):
        print('warning, no valueset content. Extension?')
        return list()

    for include in valueset_json['compose']['include']:
        if 'concept' in include.keys():
            for concept in include['concept']:
                concept['system'] = include['system']
                parsed.append(Coding(concept))
    return parsed

def expansion2codelist(valueset_json: dict | str) -> List[Coding]:
    if isinstance(valueset_json, str):
        valueset_json = filetool.load_valueset(valueset_json)

    contains = valueset_json.get('expansion').get('contains')
    return [Coding(c) for c in contains]

def filter_expansion(valueset_json: Path | str, search_terms: list) -> List[dict]:
    """
    :param valueset_json: source ValueSet that potentially contains thousands of codes
    :param search_terms: terms to match on either Coding CODE or DISPLAY
    :return: List[dict] where length is 1 because codes are merged into a single ValueSet entry.
    List[dict must be presevered as that is expected everywhere per VSAC API
    """
    valueset_list = filetool.load_valueset(valueset_json)

    matches = list()
    for valueset in valueset_list:
        for code in expansion2codelist(valueset):
            search_string = f'{code.code.lower()} {code.display.lower()}'
            for term in guard.as_list_str(search_terms):
                if term.lower() in search_string:
                    matches.append(code.as_json())

    filtered = copy.deepcopy(valueset_list[0])
    filtered['expansion']['contains'] = matches
    return [filtered]


def codelist2view(codelist: List[Coding], view_name) -> str:
    """
    :param codelist: list of concepts
    :param view_name: like define_type
    :return: SQL command
    """
    header = f"create or replace view {view_name} as select * from (values"
    footer = ") AS t (system, code, display) ;"
    content = list()
    for concept in codelist:
        safe_display = sql_escape(concept.display)
        content.append(f"('{concept.system}', '{concept.code}', '{safe_display}')")
    content = '\n,'.join(content)
    return header + '\n' + content + '\n' + footer

def criteria2view(view_name, cols: list, values: list) -> Path:
    """
    Single inline_template_casedef CVAS statement where col[1...n] = value[1...n]
    :param view_name: create view name
    :param cols: list of column names
    :param values: values for the column names
    :return:
    """
    cols = ','.join(guard.as_list_str(cols))
    values = ','.join(guard.as_list_str(values))
    sql = [f"create or replace view {view_name} as ",
           f"select * from (values",
           f"({values})",
           f") AS t ({cols}) ;"]
    sql = '\n'.join(sql)
    return save_athena_view(view_name, sql)

def csv_headers(file_csv: Path|str) -> List[str]:
    with file_csv.open(newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        return next(reader)

def csv2view(file_csv:Path|str, view_name) -> Path:
    """
    :param file_csv: path to CSV file, especially `casedef_custom.csv`
    :param view_name:  target view name like casedef_custom_csv
    :return: Path to SQL file
    """
    header_list = csv_headers(file_csv)
    create = f"create or replace view {view_name} as select * from (values"
    footer = f") AS t ({','.join(header_list)}) ;"
    content = list()

    with open(file_csv) as f:
        for row in csv.DictReader(f, header_list):
            parsed = list()
            for col in header_list:
                value = row[col]
                if value not in header_list:
                    if value is None or len(str(value)) == 0:
                        parsed.append("''")
                    else:
                        value = sql_escape(value)
                        parsed.append(f"'{value}'")
            if len(parsed) > 0:
                parsed = ','.join(parsed)
                content.append(f"\n({parsed})")
        _sql = create + '\n' + ','.join(content) + '\n' + footer
        return save_athena_view(view_name, _sql)

def union_view_list(view_list: List[str], view_name: str) -> Path:
    dest = name_prefix(view_name)
    cvas = f"create or replace view {PREFIX}__{view_name} as \n "
    select = [f"select '{name_simple(view)}' as valueset, system, code, display from \n {view}" for view in sorted(view_list)]
    sql = cvas + '\n UNION ALL\n'.join(select)
    return save_athena_view(dest, sql)

def define(codelist: List[Coding], view_name: str) -> Path:
    dest = name_prefix(view_name)
    sql = codelist2view(codelist, dest)
    return Path(save_athena_view(dest, sql))

def include(codelist: List[Coding], view_name: str) -> Path:
    """
    NOTE: Inclusion criteria is currently supported, not exclusion.
    :param codelist: List of codes to include in selection of `study_population`
    :param view_name: criteria view name
    :return: Path to SQL inclusion criteria file.
    """
    return define(codelist, f'include_{view_name}')

def exclude(codelist: List[Coding], view_name: str) -> Path:
    """
    NOTE: Exclusion criteria is not yet implemented in `study_population`, and may never be.
    :param codelist: List of codes to exclude from `study_population`
    :param view_name: criteria view name
    :return: Path to SQL exclusion criteria file.
    """
    return define(codelist, f'exclude_{view_name}')

###############################################################################
#
# naming conventions
#
###############################################################################

def select_union_study_variables(variable_list: List[str]) -> str:
    sql = list()
    for variable in variable_list:
        variable = name_simple(variable)
        select = f"\tselect distinct '{variable}'\t as variable, valueset, code, display, system, encounter_ref, subject_ref "
        from_table = f" from {PREFIX}__cohort_{variable}"
        sql.append(select + from_table)
    return ' UNION ALL\n'.join(sql)

def select_lookup_study_variables(variable_list: List[str]) -> str:
    sql = list()
    for variable in variable_list:
        variable = name_simple(variable)
        sql.append(f"\tIF(lookup.variable='{variable}', lookup.valueset) AS {variable}")
    return ',\n'.join(sql)
