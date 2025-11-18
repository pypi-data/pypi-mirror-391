create or replace view irae__gpt4_parsed as
with parsed as
(
select distinct
    concat('DocumentReference/', split_part(filename, '.', 2))  as documentreference_ref,
    concat('Patient/', split_part(filename, '.', 1))            as subject_ref,

    coalesce(donor_type_mentioned, False)           as donor_type_mentioned,
    case    when    donor_type = ''
            then    'NotMentioned'
            else    donor_type
            end as  donor_type,

    coalesce(donor_relationship_mentioned, False)   as donor_relationship_mentioned,
    case    when    donor_relationship = ''
            then    'NotMentioned'
            else    donor_relationship
            end as  donor_relationship,

    coalesce(donor_hla_quality_mentioned, False)  as donor_hla_quality_mentioned,
    case    when    donor_hla_quality = ''
            then    'NotMentioned'
            else    donor_hla_quality
            end as  donor_hla_quality,

    coalesce(donor_hla_mismatch_mentioned, False) as donor_hla_mismatch_mentioned,
    case    when    donor_hla_mismatch = ''
            then    'NotMentioned'
            else    donor_hla_mismatch
            end as  donor_hla_mismatch,

    coalesce(donor_date_mentioned, False)    as donor_date_mentioned,
    donor_date,

    coalesce(rx_therapeutic_mentioned, False)   as rx_therapeutic_mentioned,

    case    when rx_therapeutic_level = ''
            then    'NotMentioned'
            else    rx_therapeutic_level
            end as  rx_therapeutic_level,

    case    when    rx_therapeutic_sub = ''
            then    'NotMentioned'
            else    rx_therapeutic_sub
            end as  rx_therapeutic_sub,

    case    when    rx_therapeutic_supra = ''
            then    'NotMentioned'
            else    rx_therapeutic_supra
            end as  rx_therapeutic_supra,

    coalesce(rx_compliance_mentioned, False)    as rx_compliance_mentioned,
    case    when    rx_compliance_level = ''
            then    'NotMentioned'
            else    rx_compliance_level
            end as  rx_compliance_level,

    case    when    rx_compliance_partial = ''
            then    'NotMentioned'
            else    rx_compliance_partial
            end as  rx_compliance_partial,

    case    when    rx_compliance_non = ''
            then    'NotMentioned'
            else    rx_compliance_non
            end as  rx_compliance_non,

    coalesce(dsa_mentioned, False)	    as dsa_mentioned,
    coalesce(dsa_history, False)        as dsa_history,
    case    when    dsa_present = ''
            then    'NoneOfTheAbove'
            else    dsa_present
            end as  dsa_present,

    coalesce(infection_mentioned, False)    as infection_mentioned,
    coalesce(infection_history, False)      as infection_history,
    case    when    infection_present = ''
            then    'NoneOfTheAbove'
            else    infection_present
            end as  infection_present,

    coalesce(viral_mentioned, False)  as viral_mentioned,
    coalesce(viral_history, False)    as viral_history,
    case    when    viral_present = ''
            then    'NoneOfTheAbove'
            else    viral_present
            end as  viral_present,

    coalesce(bacterial_mentioned, False)      as bacterial_mentioned,
    coalesce(bacterial_history, False)        as bacterial_history,
    case    when    bacterial_present = ''
            then    'NoneOfTheAbove'
            else    bacterial_present
            end as  bacterial_present,

    coalesce(fungal_mentioned, False)         as fungal_mentioned,
    coalesce(fungal_history, False)           as fungal_history,
    case    when    fungal_present = ''
            then    'NoneOfTheAbove'
            else    fungal_present
            end as fungal_present,

    coalesce(rejection_mentioned, False)          as rejection_mentioned,
    coalesce(rejection_history, False)            as rejection_history,
    case    when    rejection_present = ''
            then    'NoneOfTheAbove'
            else    rejection_present
            end as  rejection_present,

    coalesce(failure_mentioned, False)            as failure_mentioned,
    coalesce(failure_history, False)              as failure_history,
    case    when    failure_present = ''
            then    'NoneOfTheAbove'
            else    failure_present
            end as  failure_present,

    coalesce(ptld_mentioned, False)             as ptld_mentioned,
    coalesce(ptld_history, False)               as ptld_history,
    case    when    ptld_present = ''
            then    'NoneOfTheAbove'
            else    ptld_present
            end as  ptld_present,

    coalesce(cancer_mentioned, False)           as cancer_mentioned,
    coalesce(cancer_history, False)             as cancer_history,
    case    when    cancer_present = ''
            then    'NoneOfTheAbove'
            else    cancer_present
            end as  cancer_present,
    "filename"
from    irae__gpt4_raw
where   error_found is NULL
)
select  distinct
        E.encounter_ref,
        parsed.*
from    parsed,
        core__documentreference as DOC,
        core__encounter         as E
where   DOC.documentreference_ref = parsed.documentreference_ref
and     DOC.encounter_ref = E.encounter_ref
order by parsed.subject_ref, E.encounter_ref, parsed.documentreference_ref
;
