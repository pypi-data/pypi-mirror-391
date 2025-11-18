from typing import List
from pathlib import Path
from fhirclient.models.coding import Coding
from cumulus_library_kidney_transplant import guard, fhir2sql

# https://vsac.nlm.nih.gov/valueset/2.16.840.1.113883.11.20.9.68/expansion/Latest

VALUESET_DOCTYPE = 'valueset-c80-doc-typecodes.json'
VALUESET_FACILITY = 'valueset-c80-facilitycodes.json'
VALUESET_PRACTICE = 'valueset-c80-practice-codes.json'

###############################################################################
#
# Include
#
#   *DocType
#   *Facility
#   *Practice
#
###############################################################################

def include_doc_type(codes=None) -> Path:
    """
    :param codes: list of codes for "type"
    :return: str file  inclusion criteria for `study_population`
    """
    if not codes:
        codes = get_valueset_doctype()
    codes = guard.as_list_coding(codes)
    return fhir2sql.include(codes, 'doc_type')

def include_doc_facility(codes=None) -> Path:
    """
    :param codes: list of codes for "facility"
    :return: SQL inclusion criteria for `study_population`
    """
    if not codes:
        codes = get_valueset_facility()
    codes = guard.as_list_coding(codes)
    return fhir2sql.include(codes, 'doc_facility')

def include_doc_practice(codes=None) -> Path:
    """
    :param codes: list of codes for "practice"
    :return: inclusion criteria for `study_population`
    """
    if not codes:
        codes = get_valueset_practice()
    codes = guard.as_list_coding(codes)
    return fhir2sql.include(codes, 'doc_practice')


###############################################################################
#
# Get Coding using the "key" code
#
#   *DocType
#   *Facility
#   *Practice
#
###############################################################################

def get_coding_doctype(code: str) -> Coding:
    """ lookup doctype by code
    :param code: key for lookup
    :return: Coding with {code, system, display}
    """
    return get_coding(code, VALUESET_DOCTYPE)

def get_coding_facility(code: str) -> Coding:
    """ lookup facility by code
    :param code: key for lookup
    :return: Coding with {code, system, display}
    """
    return get_coding(code, VALUESET_FACILITY)

def get_coding_practice(code: str) -> Coding:
    """ lookup practice by code
    :param code: key for lookup
    :return: Coding with {code, system, display}
    """
    return get_coding(code, VALUESET_PRACTICE)

def get_coding(code: str, valueset_json: str) -> Coding:
    """
    Big(O) time for this method is slow (N), optimize if used heavily.
    :param code: code to find in valueset
    :param valueset_json: ValueSet containing [System, Code, Display]
    :return: Coding type
    """
    for entry in fhir2sql.valueset2codelist(valueset_json):
        if entry.code == code:
            return entry

###############################################################################
#
# Get ValueSet
#
#   *DocType
#   *Facility
#   *Practice
#
###############################################################################

def get_valueset_doctype() -> List[Coding]:
    return fhir2sql.valueset2codelist(VALUESET_DOCTYPE)

def get_valueset_facility() -> List[Coding]:
    return fhir2sql.valueset2codelist(VALUESET_FACILITY)

def get_valueset_practice() -> List[Coding]:
    return fhir2sql.valueset2codelist(VALUESET_PRACTICE)
