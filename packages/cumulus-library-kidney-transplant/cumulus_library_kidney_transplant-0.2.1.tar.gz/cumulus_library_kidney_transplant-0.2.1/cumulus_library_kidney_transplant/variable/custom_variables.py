from typing import List
from pathlib import Path
from cumulus_library_kidney_transplant import filetool
from cumulus_library_kidney_transplant import fhir2sql

# List of aggregated Rx and Lab custom variables.
CUSTOM_LIST = ['rx_custom', 'lab_custom']

def make_union() -> List[Path]:
    """
    :return: Variable aggregations for SQL query convenience.
    """
    lab_list = fhir2sql.name_prefix(list_variables_lab())
    rx_list = fhir2sql.name_prefix(list_variables_rx())

    return [fhir2sql.union_view_list(lab_list, 'lab_custom'),
            fhir2sql.union_view_list(rx_list, 'rx_custom')]

def list_view_custom() -> List[str]:
    return fhir2sql.name_prefix(CUSTOM_LIST)

def list_variables_lab() -> List[str]:
    return list_variables('lab_*.csv')

def list_variables_rx() -> List[str]:
    return list_variables('rx_*.csv')

def list_variables(pattern) -> List[str]:
    return [path2variable(v) for v in filetool.list_spreadsheet_csv(pattern)]

def path2variable(path: Path) -> str:
    return str(path.name).replace('.csv', '')

def make_target(pattern:str) -> List[Path]:
    view_list = list()
    for lab_csv in filetool.list_spreadsheet_csv(pattern):
        var_name = path2variable(lab_csv)
        view_name = fhir2sql.name_prefix(var_name)
        view_list.append(fhir2sql.csv2view(lab_csv, view_name))
    return sorted(list(set(view_list)))

def make_lab() -> List[Path]:
    return make_target('lab_*.csv')

def make_rx() -> List[Path]:
    return make_target('rx_*.csv')

def make() -> List[Path]:
    """
    Custom variables are used when VSAC ValueSets are not sufficient for the study needs.

    currently three AspectKey have custom definitions
        * "make_dx()"  --> DX_TRANSPLANT_LIST
        * "make_lab()" --> LAB_LIST
        * "make_rx()"  --> RX_LIST
        # "make_union()" --> Valueset aggregations for SQL convenience.

    Each make target will read custom variable defintions from `spreadsheet/` folder.
    Each csv or tsv file produces a custom valueset with the same column names as a VSAC ValueSet.
    example:
     * code    32594-4
     * display Tacrolimus [Mass] of Dose
     * system  http://loinc.org

     SQL tables are written for each variable to the `athena` folder in the form
        irae__$aspect_$variable

    :return: List of athena SQL files for each custom variable
    """
    return make_lab() + make_rx() + make_union()
