from pathlib import Path
import shutil
import pandas as pd
from duckdb.experimental.spark import DataFrame

from cumulus_library_kidney_transplant import filetool, fhir2sql

##############################################################################
# LOINC 2.8.1 files
#
#   For simplicity, these CSV files have been processed into "valueset",
#   code, display, system='http://loinc.org'
#
##############################################################################
LOINC_CSV = filetool.path_spreadsheet('Loinc.csv')
LOINC_CONSUMER_CSV = filetool.path_spreadsheet('LoincConsumerName.csv')

def loinc2valueset(file_csv:Path = LOINC_CSV) -> DataFrame:
    """
    Get LOINC as {code,display,system}
    """
    entries = list()
    df = pd.read_csv(file_csv)
    code_col = set(list(df.columns)).intersection({'code', 'LOINC_NUM', 'LoincNumber'}).pop()
    display_col = set(list(df.columns)).intersection({'display', 'ConsumerName', 'LONG_COMMON_NAME'}).pop()

    for _, row in pd.read_csv(file_csv).iterrows():
        if '-' not in row[code_col]:
            raise Exception('invalid LOINC code ', row[code_col])

        if len(row[display_col]) < 3:
            raise Exception('invalid LOINC display ', row[display_col])

        entries.append({'system': 'http://loinc.org',
                        'code': row[code_col],
                        'display': row[display_col]})
    entries = sorted(entries, key=lambda x: x['code'])
    return pd.DataFrame.from_records(entries)

def hydrate(loinc_df:DataFrame, valueset_csv:Path) -> None:
    valueset_df = pd.read_csv(valueset_csv)
    valueset_col = set(list(valueset_df.columns)).intersection({'code', 'LOINC_NUM'}).pop()
    valueset_codes = set(valueset_df[valueset_col].dropna().unique())
    loinc_codes = set(loinc_df['code'].dropna().unique())

    if valueset_codes - loinc_codes:
        raise Exception('missing ', valueset_codes - loinc_codes)

    backup_csv = str(valueset_csv) + '.backup.csv'
    hydrate_csv = str(valueset_csv) + '.hydrate.csv'

    shutil.copy(valueset_csv, backup_csv)

    filtered = loinc_df[loinc_df['code'].isin(valueset_codes)].copy()
    filtered.to_csv(filetool.path_spreadsheet(hydrate_csv), index=False)

def clean():
    for lab_csv in filetool.list_spreadsheet_csv('lab_*.csv'):
        if '.hydrate.csv' in lab_csv.name or '.backup.csv' in lab_csv.name:
            print('clean() ', lab_csv)
            lab_csv.unlink()

def main():
    clean()
    loinc_df = loinc2valueset(LOINC_CONSUMER_CSV)
    for valueset_csv in filetool.list_spreadsheet_csv('lab_*.csv'):
        variable_name = valueset_csv.name.replace('.csv', '')
        print(variable_name)
        hydrate(loinc_df, valueset_csv)


if __name__ == "__main__":
    main()



