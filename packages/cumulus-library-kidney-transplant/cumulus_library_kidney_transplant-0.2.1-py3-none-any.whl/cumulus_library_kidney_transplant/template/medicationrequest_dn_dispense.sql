CREATE TABLE $prefix__medicationrequest_dn_dispense  as
-- https://github.com/smart-on-fhir/cumulus/issues/66
with workaround as
(
  select    distinct
            cast(dispenseRequest.validityPeriod as json) as validityPeriod,
            dispenseRequest.numberOfRepeatsAllowed,
            dispenseRequest.expectedSupplyDuration,
            dispenseRequest.quantity,
            MR.id,
            SP.medicationrequest_ref
  from      medicationRequest as MR,
            $prefix__cohort_study_population_rx as SP
  where     SP.medicationrequest_ref = concat('MedicationRequest/', MR.id)
)
select  distinct
        date(from_iso8601_timestamp(json_extract_scalar(validityPeriod, '$.start')))    as validity_start_date,
        date(from_iso8601_timestamp(json_extract_scalar(validityPeriod, '$.end')))      as validity_end_date,
        numberOfRepeatsAllowed,
        expectedSupplyDuration."code"   as duration_code,
        expectedSupplyDuration."system" as duration_system,
        expectedSupplyDuration."unit"   as duration_unit,
        expectedSupplyDuration."value"  as duration_value,
        quantity."unit"                 as quantity_unit,
        quantity."value"                as quantity_value,
        expectedSupplyDuration,
        id,
        medicationrequest_ref
from workaround;
