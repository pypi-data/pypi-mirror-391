create TABLE irae__gpt4_compliance_rank as
with comparable as
(
    SELECT  distinct
            documentreference_ref               ,
            subject_ref                         ,
            encounter_ref                       ,
            age_at_visit                        ,
            enc_start_date                      ,
            enc_end_date                        ,
            doc_date                            ,
            rank_rx_therapy.ranking             as rx_therapeutic_level,
            rank_rx_therapy_sub.ranking         as rx_therapeutic_sub,
            rank_rx_therapy_supra.ranking       as rx_therapeutic_supra,
            rank_rx_compliance.ranking          as rx_compliance_level,
            rank_rx_compliance_partial.ranking  as rx_compliance_partial,
            rank_rx_compliance_non.ranking      as rx_compliance_non
    FROM    irae__gpt4_fhir     as LLM,
            irae__ranking       as rank_rx_therapy,
            irae__ranking       as rank_rx_therapy_sub,
            irae__ranking       as rank_rx_therapy_supra,
            irae__ranking       as rank_rx_compliance,
            irae__ranking       as rank_rx_compliance_partial,
            irae__ranking       as rank_rx_compliance_non
    WHERE   rank_rx_therapy.code = LLM.rx_therapeutic_level
    and     rank_rx_therapy_sub.code = LLM.rx_therapeutic_sub
    and     rank_rx_therapy_supra.code = LLM.rx_therapeutic_supra
    and     rank_rx_compliance.code = LLM.rx_compliance_level
    and     rank_rx_compliance_partial.code = LLM.rx_compliance_partial
    and     rank_rx_compliance_non.code = LLM.rx_compliance_non
),
note_score as
(
    select  distinct
            (rx_therapeutic_level + rx_compliance_level)    as compliant,
            (rx_therapeutic_sub + rx_compliance_partial)    as compliant_partial,
            (rx_therapeutic_sub + rx_compliance_non)        as compliant_non,
            comparable.*
    from    comparable
)
select * from note_score;


create or replace view irae__gpt4_compliance_status as
with visit as
(
    select  encounter_ref,
            sum(compliant)          as compliant,
            sum(compliant_partial)  as compliant_partial,
            sum(compliant_non)      as compliant_non
    from irae__gpt4_compliance_rank
    group by encounter_ref
)
SELECT  distinct encounter_ref,
        case    WHEN    compliant=0 and compliant_partial=0 and compliant_non=0 then 'NotMentioned'

                WHEN    compliant > compliant_non       and
                        compliant > compliant_partial   then 'compliant'

                WHEN    compliant = compliant_non       or
                        compliant = compliant_partial   then 'partial'

                WHEN    compliant < compliant_non       or
                        compliant < compliant_partial   then 'noncompliant'

                ELSE    'unknown'
                END AS  rx_compliance_status
FROM    visit;

create or replace view irae__gpt4_compliance as
select  distinct
        status.rx_compliance_status,
        rank.*
from    irae__gpt4_compliance_rank   as rank,
        irae__gpt4_compliance_status as status
where   rank.encounter_ref = status.encounter_ref;
