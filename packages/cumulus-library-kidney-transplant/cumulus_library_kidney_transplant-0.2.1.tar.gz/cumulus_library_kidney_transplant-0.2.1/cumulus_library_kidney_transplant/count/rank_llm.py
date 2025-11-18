import pandas as pd

from cumulus_library_kidney_transplant import filetool

PARSED_CSV = 'athena-no-spans-july-17.csv'
SUBJECT_REF = 'subject_ref'
ENCOUNTER_REF = 'encounter_ref'
EXCLUDE_COLS = ['documentreference_ref', 'filename'] + [SUBJECT_REF, ENCOUNTER_REF]
EXCLUDE_VALS = ['NoneOfTheAbove', 'NotMentioned']

def count_tf(parsed_csv:str, stratifier:str = SUBJECT_REF, first=False) -> str:
    """
    From irae__gpt4_parsed downloaded from Athena, count the number of times (term frequency) of each column:value pair.
    Stratify (group by) either SUBJECT_REF or ENCOUNTER_REF.

    :param parsed_csv: LLM output parsed by irae__gpt4_parsed.sql
    :param stratifier: by subject_ref or encounter_ref
    :param first: only get the first hit
    :return: string output tsv
    """
    df = pd.read_csv(parsed_csv)
    out = list()

    for col in df.columns:
        if col in EXCLUDE_COLS:
            print(f'Skipping {col}')
        else:
            df_filtered = df[df[col].notna() & ~df[col].isin(EXCLUDE_VALS)]

            if first:
                term_freq = (df_filtered
                             .groupby([stratifier, col])
                             .size()
                             .reset_index(name='cnt')
                             .sort_values(by=[stratifier, 'cnt'], ascending=[True, False])
                             .groupby(stratifier, as_index=False)
                             .first())
            else:
                term_freq = (df_filtered.groupby([stratifier, col])
                             .size()
                             .reset_index(name='cnt')
                             .sort_values(by=[stratifier, 'cnt'], ascending=[True, False]))

            for index, row in term_freq.iterrows():
                cnt = row['cnt']
                ref = row[stratifier]
                val = row[col]

                out.append(f"{ref}\t{col}\t{val}\t{cnt}")
    return '\n'.join(out)


if __name__ == '__main__':

    parsed_csv= PARSED_CSV

    for first in [True, False]:
        by_pat = count_tf(parsed_csv=parsed_csv, stratifier=SUBJECT_REF, first=first)
        by_enc = count_tf(parsed_csv=parsed_csv, stratifier=ENCOUNTER_REF, first=first)
        label = 'first' if first else 'all'
        filetool.write_text(by_pat + by_enc, f'{parsed_csv}.{label}.cnt.tsv')
