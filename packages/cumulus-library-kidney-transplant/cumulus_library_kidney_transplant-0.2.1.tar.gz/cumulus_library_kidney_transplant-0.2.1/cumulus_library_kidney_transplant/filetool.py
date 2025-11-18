import os
import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Iterable, Generator
from cumulus_library_kidney_transplant import jsonifiers, guard

PREFIX = 'irae'

###############################################################################
# Root
###############################################################################
def path_home(filename=None) -> Path:
    """
    Get path to python package home directory
    :param filename: optionally with `filename`
    :return: Path to project home directory, optionally with `filename`
    """
    if filename:
        return Path(os.path.join(os.path.dirname(__file__), filename))
    else:
        return Path(os.path.dirname(__file__))

def path_parent(filename=None) -> Path:
    """
    Get path to the "parent" folder where `README.MD` and `pyproject.toml` live
    :param filename: optional name of file to get path for in parent folder
    :return: Path to project parent directoy, otionally with `filename`
    """
    parent = Path(os.path.abspath(os.path.join(path_home(), os.pardir)))
    if filename:
        return Path(os.path.join(parent, filename))
    else:
        return parent

###############################################################################
#
# Valueset(s)
#
###############################################################################

def path_valueset(filename: Path | str) -> Path:
    """
    :param filename: name of JSON file
    :return: Path to JSON valueset
    """
    return Path(os.path.join(path_home(), 'valueset', filename))

def load_valueset(filename: Path | str) -> dict:
    """
    :param filename: name of JSON file
    :return: dict of valueset contents
    """
    return read_json(path_valueset(filename))

def save_valueset(filename: Path | str, contents: dict) -> Path:
    """
    Save JSON to valueset folder.
    :param filename: name of JSON file (destination)
    :param contents: dict JSON
    :return: Path to JSON filename
    """
    return Path(write_json(contents, path_valueset(filename)))


###############################################################################
#
# Spreadsheets, uploaded by user
#
###############################################################################

def path_spreadsheet(filename: Path | str) -> Path:
    """
    :param filename: name of csv or tsv
    :return: Path to filename
    """
    return Path(os.path.join(path_home(), 'spreadsheet', filename))

def list_spreadsheet_csv(pattern:str = '*.csv') -> list[Path]:
    spreadsheet_dir = path_home() / 'spreadsheet'
    return list(spreadsheet_dir.glob(pattern))

###############################################################################
#
# Template(s)
#
###############################################################################
def name_template(table_file: list | str) -> list | str:
    """
    Strips `study_prefix` from the table str or list 
    :param table_file: name of table to load (with .sql
    :return: 
    """
    if guard.is_list_type(table_file, str):
        return [name_template(t) for t in table_file]
    else:
        return table_file.replace(f'{PREFIX}__', '')

def path_template(file_sql: Path | str) -> Path:
    template = name_template(file_sql)
    return Path(os.path.join(path_home(), 'template', template))

def load_template(file_sql: Path | str) -> str:
    return inline_template(read_text(path_template(file_sql)))

def copy_template(file_sql: str) -> Path:
    """
    :param file_sql: name of SQL file to copy from "template" to "athena" with the $prefix replaced.
    :return: Manifest Path to athena/$prefix__$file_sql
    """
    sql = inline_template(read_text(path_template(file_sql)))
    return save_athena(f"{PREFIX}__{file_sql}", sql)

def inline_template(sql: str, variable: str = None) -> str:
    sql = sql.replace('$prefix', PREFIX)
    if variable:
        sql = sql.replace('$variable_list', variable)
        sql = sql.replace('$variable', variable)
    return sql


###############################################################################
#
# prompt (Large Language Model)
#
###############################################################################
def path_prompt(filename: Path | str = None) -> Path:
    if filename:
        return Path(os.path.join(path_home(), 'prompt', filename))
    else:
        return Path(os.path.join(path_home(), 'prompt'))

def load_prompt_text(filename: Path | str) -> str:
    return read_text(path_prompt(filename))

def save_prompt_json(filename: Path | str, contents: dict) -> Path:
    return Path(write_json(contents, path_prompt(filename)))

def load_prompt_json(filename: Path | str) -> dict:
    return read_json(path_prompt(filename))

def save_prompt_text(filename: Path | str, text: str) -> Path:
    return Path(write_text(text, path_prompt(filename)))

###############################################################################
#
# Athena SQL File(s)
#
###############################################################################

def path_athena(file_sql: Path | str) -> Path:
    return Path(os.path.join(os.path.dirname(__file__), 'athena', file_sql))

def save_athena(file_sql: Path | str, contents: str) -> Path:
    return Path(write_text(contents, path_athena(file_sql)))

def save_athena_view(view_name: str, contents: str) -> Path:
    return Path(write_text(contents, path_athena(f'{view_name}.sql')))


###############################################################################
#
# Read/Write Text
#
###############################################################################
def read_text(text_file: Path | str, encoding: str = 'UTF-8') -> str:
    """
    Read text from file
    :param text_file: absolute path to file
    :param encoding: provided file's encoding
    :return: file text contents
    """
    if file_exists(text_file):
        with m_open(file=text_file, encoding=encoding) as t_file:
            return t_file.read()

def write_text(contents: str, file_path: Path | str, encoding: str = 'UTF-8') -> str:
    """
    Write file contents
    :param contents: string contents
    :param file_path: absolute path of target file
    :param encoding: provided file's encoding
    :return: text_file name
    """
    with m_open(file=file_path, mode='w', encoding=encoding) as file_path:
        file_path.write(contents)
        file_path.close()
        return file_path.name

def write_bytes(data: str, file_path: str) -> None:
    """
    Writes provided bytes to provided file path
    :param data: bytes contents
    :param file_path: absolute path to file
    :return:
    """
    with m_open(file=file_path, mode='wb') as bytes_file:
        bytes_file.write(data.encode('UTF-8'))

def read_bytes(binary_file: str) -> bytes:
    """
    Read bytes from binary file
    :param binary_file: absolute path to file
    :return: bytes file contents
    """
    if file_exists(binary_file):
        with m_open(file=binary_file, mode='rb') as bin_file:
            return bytes(bin_file.read())

def file_exists(filename: Path | str) -> bool:
    """
    FAIL FAST if not exists `filename`
    :param filename: check for existance
    :return: BOOL True or raise exception (fail fast)
    """
    target = Path(filename)
    if not target.exists():
        raise Exception('file not found: ' + str(target))
    return True

def m_open(**kwargs):
    """
    Wrapper for built in open with exception handling and logging
    :return: file like object
    """
    try:
        return open(**kwargs)
    except Exception:
        print('m_open raised an exception', exc_info=True)
        raise

###############################################################################
#
# Read/Write JSON
#
###############################################################################
def read_json(json_file: Path | str, encoding: str = 'UTF-8') -> Dict[Any, Any]:
    """
    Read json from file
    :param json_file: absolute path to file
    :param encoding: provided file's encoding
    :return: json file contents
    """
    if file_exists(json_file):
        with m_open(file=json_file, encoding=encoding) as j_file:
            return json.load(j_file)

def write_json(contents: Dict[Any, Any], json_file_path: Path | str, encoding: str = 'UTF-8') -> Path:
    """
    Write JSON to file
    :param contents: json (dict) contents
    :param json_file_path: absolute destination file path
    :param encoding: provided file's encoding
    :return: file name
    """
    directory = os.path.dirname(json_file_path)
    os.makedirs(directory, exist_ok=True)
    with m_open(file=json_file_path, mode='w', encoding=encoding) as json_file_path:
        json.dump(contents, json_file_path, indent=4, cls=jsonifiers.CustomJsonEncoder)
        return Path(json_file_path.name)

###############################################################################
#
# Read/Write CSV
#
###############################################################################

def write_csv(rows: Iterable[List[str]], file_csv: Path | str, delimiter: str = ',', quote_char: str = '"'):
    """Write csv file.
    :param rows: The contents to write to file.
    :param file_csv: absolute path to the csv
    :param delimiter: the delimiter used in the csv
    :param quote_char: the quote character used in the csv
    :return: an iterator of row values
    """
    with open(file_csv, 'w+') as csvfile:
        writer = csv.writer(csvfile, delimiter=delimiter, quotechar=quote_char)
        for row in rows:
            writer.writerow(row)


def read_csv(file_csv: Path | str, delimiter: str = ',', quote_char: str = '"') -> Generator[List[str], None, None]:
    """
    Parse csv file
    :param file_csv: absolute path to the csv
    :param delimiter: the delimiter used in the csv
    :param quote_char: the quote character used in the csv
    :return: an iterator of row values
    """
    if file_exists(file_csv):
        with m_open(file=file_csv) as csv_file:
            for row in csv.reader(csv_file, delimiter=delimiter, quotechar=quote_char):
                yield row

def list_from_csv_column(file_csv: Path | str, column: str, delimiter: str = ',', quote_char: str = '"') -> List[str]:
    """
    Parses csv file and returns all values from the provided column
    :param file_csv: absolute path to the csv
    :param column: the column from which to gather values
    :param delimiter: the delimiter used in the csv
    :param quote_char: the quote character used in the csv
    :return: a list of all values from the requested column
    """
    return [row[column] for row in read_csv(file_csv=file_csv, delimiter=delimiter, quote_char=quote_char)]
