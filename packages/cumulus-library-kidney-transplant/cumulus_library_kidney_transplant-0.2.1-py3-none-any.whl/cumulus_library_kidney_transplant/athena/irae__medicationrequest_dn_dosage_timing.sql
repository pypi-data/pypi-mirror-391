CREATE TABLE irae__medicationrequest_dn_dosage_timing as
select  distinct
        date(from_iso8601_timestamp(DI.timing.repeat.boundsperiod."start")) as timing_start_date,
        date(from_iso8601_timestamp(DI.timing.repeat.boundsperiod."end"))   as timing_end_date,
        DI.timing.code.text                     as timimg_text,
        DI.timing.repeat.duration               as repeat_duration,
        DI.timing.repeat.durationUnit           as repeat_durationunit,
        DI.timing.repeat."count"                as repeat_count,
        id, concat('MedicationRequest/', id)    as medicationrequest_ref
FROM    irae__cohort_study_population_rx        as SP,
        medicationRequest                       as mr,
        UNNEST(dosageInstruction)               AS t(DI)
WHERE   SP.medicationrequest_ref = concat('MedicationRequest/', MR.id)
;