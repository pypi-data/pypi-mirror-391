##############################################################################
#
# INCLUDE contains keywords likely to match Kidney Study specific content
#
##############################################################################

INCLUDE = {
    'MSICU', 'MS-ICU',
    'HLA', 'leukocyte', 'antigen',
    'match', 'kdigo', 'KDIGO',
    'med–surg', 'surgical', 'surgery', 'operative', 'operation',
    'kidney', 'renal',
    'nephrology', 'urology',
    'transplant', 'donor', 'recipient', 'graft',
    'biopsy', 'pathology', 'banff', 'specimen', 'tissue',
    'social work',
    'oncology', 'cancer', 'dermatology', 'dermatologist',
    'pharmacy',
    'infectious disease', 'ID CONSULT', 'infection', 'PCR',
}

def like(column:str, keyword :str) -> str:
    if keyword == keyword.lower():
        return f"lower({column}) like '%{keyword}%'"
    if keyword == keyword.upper():
        return f"upper({column}) like '%{keyword}%'"
    else:
        return f"{column} like '%{keyword}%'"

def like_list(column:str) -> list:
    return [like(column, include) for include in INCLUDE]

def match_bool(title:str, keyword :str) -> bool:
    if keyword == keyword.lower():
        return keyword in title.lower()
    if keyword == keyword.upper():
        return keyword in title.upper()
    else:
        return keyword in title

def match_list(title:str) -> list:
    matches = list()
    for include in INCLUDE:
        if match_bool(title, include):
            matches.append(include)
    return sorted(matches)


