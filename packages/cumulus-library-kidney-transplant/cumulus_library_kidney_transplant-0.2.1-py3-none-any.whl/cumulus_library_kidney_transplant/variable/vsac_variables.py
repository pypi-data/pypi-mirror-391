import os
from typing import List
from pathlib import Path
from cumulus_library_kidney_transplant import filetool
from cumulus_library_kidney_transplant import fhir2sql
from cumulus_library_kidney_transplant.study_prefix import PREFIX
from cumulus_library_kidney_transplant.variable.aspect import Aspect, AspectMap, AspectKey      # TODO: refactor
from cumulus_library_kidney_transplant.variable.vsac_variables_defined import get_aspect_map
from cumulus_library.apis import umls
# Cancer valueset are currently a special corner case
DX_CANCER_LIST = ['carcinoma',
                  'squamous',
                  'basal',
                  'melanoma',
                  'skin',
                  'lymph',
                  'leukemia',
                  'kidney',
                  'malignant',
                  'neoplasm']

###############################################################################
#
# VSAC Variables and Valuesets
#
###############################################################################
def list_view_variables() -> List[str]:
    """
    :return: list $variable SQL Tablename
    """
    variable_list = list()
    for aspect in get_aspect_map().as_list():
        for variable in aspect.variable_list:
            variable_list.append(variable.name)
    return fhir2sql.name_prefix(variable_list)

def list_view_valuesets() -> List[str]:
    """
    :return: list $variable_$valueset SQL Tablename
    """
    valueset_list = list()
    for aspect in get_aspect_map().as_list():
        for variable in aspect.variable_list:
            for valueset in variable.valueset_list:
                valueset_list.append(f"{variable.name}_{valueset.name}")
    return fhir2sql.name_prefix(valueset_list)

###############################################################################
#
# Make
#
###############################################################################
def make_aspect(aspect: Aspect) -> List[Path]:
    """
    Download and store JSON and generate SQL for each VSAC ValueSet.
    Each Valueset is cached in valueset to enable faster build caching.

    `fhir2sql.py` converts FHIR json into SQL tables for each valueset.

    :param aspect: see `list_aspects()`, Dx, Rx, Lab, LabPanel, Proc, Doc
    :return: Path to SQL File to create variable definition valuesets.
    """
    api = umls.UmlsApi()
    var_list = list()
    print('================================')
    print(f'* aspect {aspect.key.as_json()}')
    for variable in aspect.variable_list:
        print(f'** {variable.name}')
        valueset_list = list()
        for valueset in variable.valueset_list:
            print(f'*** {variable.name} -> {valueset.name}')
            json_file = filetool.path_valueset(f"{PREFIX}__{variable.name}/{valueset.name}.json")
            view_name = f"{PREFIX}__{variable.name}_{valueset.name}"
            view_file = filetool.path_athena(f'{view_name}.sql')

            if not os.path.exists(json_file):
                print(f'**** Downloading {variable.name} {valueset.as_json()}')
                if isinstance(valueset.oid, list):
                    json_list = list()
                    for oid in valueset.oid:
                        print(oid)
                        json_list += api.get_vsac_valuesets(url=None, oid=oid)
                    filetool.save_valueset(json_file, json_list)
                else:
                    json_list = api.get_vsac_valuesets(url=None, oid=valueset.oid)
                    filetool.save_valueset(json_file, json_list)

            if not os.path.exists(view_file):
                print(f'**** Writing {view_file}')
                code_list = list()
                for entry in filetool.read_json(json_file):
                    code_list += fhir2sql.expansion2codelist(entry)
                sql = fhir2sql.codelist2view(code_list, view_name)
                filetool.save_athena_view(view_name, sql)

            var_list.append(view_file)
            valueset_list.append(view_name)
        var_list.append(fhir2sql.union_view_list(valueset_list, variable.name))
    return var_list

def make() -> List[Path]:
    """
    VSAC ValueSet Authority Center is an NLM hosted site of human-expert curated Valuesets.
    Valuesets also known as codesets. Whenever possible, we use VSAC curated valuesets that have been human reviewed.

     `vsac_variables_defined`
        .get_labs()
        .get_medications()
        .get_diagnoses()
        .get_documents()
        .get_procedures()}

    Each $variable contains 1+ named valuesets, resulting in tables like "rx_immunosuppressive"
    Each $valueset has a prefix and a name like "dx_transplant", "rx_everolimus".

    :return: List SQL files to define each vsac_variable.
    """
    file_list = list()
    for aspect in get_aspect_map().as_list():
        file_list += make_aspect(aspect)
    return file_list


if __name__ == "__main__":
    make()
