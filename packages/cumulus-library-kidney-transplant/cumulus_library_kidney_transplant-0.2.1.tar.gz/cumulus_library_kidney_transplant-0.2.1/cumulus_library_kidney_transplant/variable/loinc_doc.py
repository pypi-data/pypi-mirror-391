from typing import List
from pathlib import Path
from cumulus_library_kidney_transplant import filetool, fhir2sql

#####################################################################################################################
#
# README:
#
# make() assumes that LOINC DocumentOntology curation has already been done by a human being with eyeballs.
#
# There is no substitute for human expert review and careful selection of document types.
# If you desire to DIY and compile a different selection of ontology concepts, see
# `spreadsheet/document/assist_curation.py`
# `spreadsheet/document/kind.py`
# `spreadsheet/document/role.py`
# `spreadsheet/document/type_of_service.py`
# `spreadsheet/document/subject_matter_domain.py`
#
#####################################################################################################################
def inline_template(template) -> Path:
    sql = filetool.load_template(f"{template}.sql")
    view_name = fhir2sql.name_prefix(template)
    return filetool.save_athena_view(view_name, sql)

def make() -> List[Path]:
    templates = [
        'doc_ontology',
        'doc_ontology_kind',
        'doc_ontology_role',
        'doc_ontology_service',
        'doc_ontology_domain',
        'doc_ontology_include',
    ]
    return [inline_template(t) for t in templates]

if __name__ == "__main__":
    make()
