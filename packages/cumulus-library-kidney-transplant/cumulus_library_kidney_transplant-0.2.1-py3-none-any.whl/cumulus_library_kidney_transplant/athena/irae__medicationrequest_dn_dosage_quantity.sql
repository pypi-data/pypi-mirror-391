CREATE TABLE irae__medicationrequest_dn_dosage_quantity as
with workaround as
(
    SELECT  distinct
            json_extract(CAST(DAR AS json), '$.dosequantity') AS doseQuantity,
            json_extract(CAST(DAR AS json), '$.ratequantity') AS rateQuantity,
            MR.id,
            SP.medicationrequest_ref
    FROM    irae__cohort_study_population_rx as SP,
            medicationRequest as mr,
            UNNEST(dosageInstruction)   AS t(DI),
            UNNEST(DI.doseAndRate)      AS t(DAR)
    WHERE   SP.medicationrequest_ref = concat('MedicationRequest/', MR.id)
),
guard_schema as
(
    SELECT  TRY_CAST(doseQuantity AS ROW(code varchar, system varchar, unit varchar, value double)) as doseQuantity,
            TRY_CAST(rateQuantity AS ROW(code varchar, system varchar, unit varchar, value double)) as rateQuantity,
            id, medicationrequest_ref
    FROM    workaround
)
select  distinct
        doseQuantity."code"     as dose_code,
        doseQuantity."system"   as dose_system,
        doseQuantity."unit"     as dose_unit,
        doseQuantity."value"    as dose_value,
        doseQuantity,
        rateQuantity."code"     as rate_code,
        rateQuantity."system"   as rate_system,
        rateQuantity."unit"     as rate_unit,
        rateQuantity."value"    as rate_value,
        rateQuantity
        id, medicationrequest_ref
from    guard_schema; 

