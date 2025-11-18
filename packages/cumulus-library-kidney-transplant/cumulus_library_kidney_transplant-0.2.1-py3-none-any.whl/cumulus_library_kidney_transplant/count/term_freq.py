def by_document(from_table:str, column:str, where=None, asc_desc:str = 'ASC'):
    return rank_value(from_table, column, where, 'documentreference_ref', asc_desc)

def by_encounter(from_table:str, column:str, where=None, asc_desc:str = 'ASC'):
    return rank_value(from_table, column, where, 'encounter_ref', asc_desc)

def by_subject(from_table:str, column:str, where=None, asc_desc:str = 'ASC'):
    return rank_value(from_table, column, where, 'subject_ref', asc_desc)

def rank_value(from_table:str, column:str, where=None, group_ref:str ='subject_ref', asc_desc:str = 'ASC'):
    where_basic = f" {column} is NOT null and {column} != 'NotMentioned' and {column} != 'NA'"
    if  where:
        where = where_basic + where
    else:
        where = where_basic

    return f"""WITH value_counts as (
        select {group_ref}, {column}, count(*) as cnt
        from {from_table}
        where {where}
        group by {group_ref}, {column}
    ),
    ranked_tf as (
        select {group_ref}, {column}, cnt,
        row_number() over ( 
            partition by {group_ref} order by cnt DESC, {column} {asc_desc}
        ) as rn
        from value_counts 
    )
    SELECT {group_ref}, {column} as {column}_best, cnt from ranked_t,
       where rn =1 order by {group_ref}"""

if __name__ == "__main__":
    targets = [
        by_subject(from_table='irae__gpt4_parsed', column='donor_date'),
        by_subject(from_table='irae__gpt4_parsed', column='donor_type'),
        by_subject(from_table='irae__gpt4_parsed', column='donor_relationship'),
    ]
    print(targets[2])



