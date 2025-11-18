import pandas as pd
from cumulus_library_kidney_transplant import filetool, fhir2sql
from variable import loinc_names
from cumulus_library_kidney_transplant.spreadsheet.document import (
    type_of_service,
    subject_matter_domain,
    kind,
    role,
    study_keywords
)

##############################################################################
# LOINC 2.8.1 files
#
#   AccessoryFiles/DocumentOntology/DocumentOntology.csv
#   LoincTable/Loinc.csv
#
#   For simplicity, these CSV files have been processed into "valueset",
#   code, display, system='http://loinc.org'
#
##############################################################################
ONTOLOGY_CSV = filetool.path_spreadsheet('document/DocumentOntology.csv')
ONTOLOGY_VALUESET_CSV = filetool.path_spreadsheet('document/DocumentOntology_valueset.csv')

def term_frequency(part_type_name:str):
    """
    Get frequency for each LOINC Part, for example, each
        Document.SubjectMatterDomain
    :param part_type_name: Document.SubjectMatterDomain, etc
    :return: counts
    """
    df = pd.read_csv(ONTOLOGY_CSV)
    mask = df["PartTypeName"] == part_type_name
    return df.loc[mask, "PartName"].value_counts()

def print_tf(part_type_name:str)-> None:
    """
    Print frequency of each LOINC Part
    """
    for part_name, tf in term_frequency(part_type_name).items():
        print(f"'{part_name}',", '\t#', tf)

def ontology2valueset():
    """
    Save ONTOLOGY_CSV as {code,display,system}
    """
    ont = pd.read_csv(ONTOLOGY_CSV)
    loinc = loinc_names.loinc2valueset(loinc_names.LOINC_CSV)

    ont['LoincNumber'] = ont['LoincNumber'].str.strip()
    loinc['code'] = loinc['code'].str.strip()

    ont_keys = set(ont['LoincNumber'].dropna().unique())

    filtered = loinc[loinc['code'].isin(ont_keys)].copy()
    filtered.to_csv(filetool.path_spreadsheet(ONTOLOGY_VALUESET_CSV), index=False)
    fhir2sql.csv2view(ONTOLOGY_VALUESET_CSV, 'irae__doc_ontology')

def include_loinc_part(loinc_part_type:str = None) -> None:
    """
    Create inclusion CSV/SQL files based on INCLUDE criteria

    See INCLUDE criteria for:
    * `role.py`
    * `kind.py`
    * `subject_matter_domain.py`
    * `type_of_service.py`
    :param loinc_part_type: Document.SubjectMatterDomain, etc
    """
    if loinc_part_type is None:
        include_loinc_part('Document.Kind')
        include_loinc_part('Document.TypeOfService')
        include_loinc_part('Document.SubjectMatterDomain')
        include_loinc_part('Document.Role')

    ontology_df = pd.read_csv(ONTOLOGY_CSV)
    loinc_df = loinc_names.loinc2valueset()
    loinc_df = loinc_df.drop_duplicates(subset="code", keep="first")
    lookup = loinc_df.set_index("code")["display"].to_dict()
    matches = dict()

    for row in ontology_df.itertuples(index=False):
        name = row.PartName
        code = row.LoincNumber
        display = None
        if loinc_part_type == row.PartTypeName:
            if row.PartTypeName == 'Document.Kind':
                if name in kind.INCLUDE:
                    display = lookup[code]
            elif row.PartTypeName == 'Document.TypeOfService':
                if name in type_of_service.INCLUDE:
                    display = lookup[code]
            elif row.PartTypeName == 'Document.SubjectMatterDomain':
                if name in subject_matter_domain.INCLUDE:
                    display = lookup[code]
            elif row.PartTypeName == 'Document.Role':
                if name in role.INCLUDE:
                    display = lookup[code]
            if display and code not in matches.keys():
                matches[code] = display

    # convert to list output CSV
    output = list()
    for code, display in matches.items():
        matches = study_keywords.match_list(display)
        matches = '|'.join(matches)
        output.append({'system':'http://loinc.org',
                       'code':code,
                       'display':display,
                       'keyword':matches})

    loinc_part_alias = loinc_part_type.replace('Document.', '').lower()

    output = sorted(output, key=lambda x: x['code'])
    output_csv = f"document/doc_{loinc_part_alias}.csv"
    view_name = f"irae__doc_ontology_{loinc_part_alias}"

    df_filtered = pd.DataFrame(output, columns=['system', 'code', 'display', 'keyword'])
    df_filtered.to_csv(filetool.path_spreadsheet(output_csv), index=False)
    fhir2sql.csv2view(filetool.path_spreadsheet(output_csv), view_name)

def main():
    ontology2valueset()
    include_loinc_part()

if __name__ == "__main__":
    # main()
    print('Are you sure you want to recompile document type selections for this study?')
    print('If YES, run main() above and then review the output SQL selections in athena')
    pass