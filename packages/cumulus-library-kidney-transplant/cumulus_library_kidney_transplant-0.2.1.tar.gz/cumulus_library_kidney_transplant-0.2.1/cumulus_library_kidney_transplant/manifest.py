from typing import List
from pathlib import Path
import tomllib
import tomli_w
from cumulus_library.study_manifest import StudyManifest
from cumulus_library_kidney_transplant import guard, filetool

###############################################################################
#
# StudyManifest by cumulus-library is the futureproof answer for manifest.toml
# Expect deprecation of custom manifest.toml in future IRAE study releases.
#
###############################################################################
def get_study_manifest() -> StudyManifest:
    return StudyManifest(filetool.path_parent())

###############################################################################
#
# IRAE Custom "study builder" methods for manifest.toml
#
###############################################################################
def get_file_config() -> List:
    """
    :return: section for SQL targets
    """
    return read_manifest().get('file_config')

def path_manifest() -> Path:
    return filetool.path_home('./manifest.toml')

def read_manifest(file_path: str | Path = None) -> dict:
    if not file_path:
        file_path = path_manifest()
    with open(file_path, 'rb') as f:
        data = tomllib.load(f)
    return data

def backup_manifest(file_path: str | Path = None) -> Path | None:
    if not file_path:
        file_path = path_manifest()
    n = 1
    while True:
        backup_path = file_path.with_name(f"{file_path.name}.bak.{n}")
        if not backup_path.exists():
            with open(file_path, "rb") as src, open(backup_path, "wb") as dst:
                dst.write(src.read())
            return backup_path
        n += 1

def write_manifest(file_names: List[Path] | List[str]) -> Path:
    saved = read_manifest()
    # NOTE: Adding the IRAE highlights builder manually before writing the final manifest
    file_names_copy = [*file_names]
    file_names_copy.append('cumulus_library_kidney_transplant/nlp_result_to_highlights/builder_irae_highlights.py')
    saved['file_config']['file_names'] = path_relative(file_names_copy)
    saved['export_config']['count_list'] = list_tables(file_names_copy, '_count_')

    with open(str(path_manifest()), 'wb') as f:
        tomli_w.dump(saved, f)
    print('saved ' + str(path_manifest()))
    return path_manifest()

def list_tables(file_names: List[Path] | List[str], search_term: str = None) -> List[str]:
    """
    :param file_names: SQL valuesets, cohorts, samples, etc
    :param search_term: SQL counts only, typically "_count_"
    :return: List of SQL table names
    """
    table_names = list()
    for table in path_relative(file_names):
        table = table.replace('athena/', '').replace('.sql', '')
        if search_term:
            if search_term in table:
                table_names.append(table)
        else:
            table_names.append(table)
    return table_names

def path_relative(file_names: List[Path] | List[str]) -> List[str]:
    split_token = 'cumulus-library-kidney-transplant/'
    simpler = list()
    for filename in guard.as_list_str(file_names):
        if split_token in filename:
            _, filename = filename.split(split_token)
        simpler.append(filename)
    return simpler

def get_study_prefix() -> str:
    return str(read_manifest().get('study_prefix'))

