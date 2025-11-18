CREATE TABLE irae__medicationrequest_dn_dosage_route as
select  distinct
        RC."code"       as route_code,
        RC."display"    as route_display,
        RC."system"     as route_system,
        DI.route,
        id, concat('MedicationRequest', id) as medicationrequest_ref
FROM    irae__cohort_study_population_rx as SP,
        medicationRequest as mr,
        UNNEST(dosageInstruction)   as t(DI),
        UNNEST(DI.route.coding)     AS t(RC)
WHERE   SP.medicationrequest_ref = concat('MedicationRequest/', MR.id);
