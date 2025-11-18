create table irae__cohort_study_variables_wide as
with lookup as
(
    select  distinct variable, valueset, encounter_ref
    from    irae__cohort_study_variables
)
select distinct
    lookup.variable,
    	IF(lookup.variable='doc_biopsy', lookup.valueset) AS doc_biopsy,
	IF(lookup.variable='dx_autoimmune', lookup.valueset) AS dx_autoimmune,
	IF(lookup.variable='dx_cancer', lookup.valueset) AS dx_cancer,
	IF(lookup.variable='dx_immunocompromised', lookup.valueset) AS dx_immunocompromised,
	IF(lookup.variable='dx_infection', lookup.valueset) AS dx_infection,
	IF(lookup.variable='dx_kidney', lookup.valueset) AS dx_kidney,
	IF(lookup.variable='dx_transplant', lookup.valueset) AS dx_transplant,
	IF(lookup.variable='lab_autoimmune', lookup.valueset) AS lab_autoimmune,
	IF(lookup.variable='lab_cbc', lookup.valueset) AS lab_cbc,
	IF(lookup.variable='lab_cmp', lookup.valueset) AS lab_cmp,
	IF(lookup.variable='lab_creatinine', lookup.valueset) AS lab_creatinine,
	IF(lookup.variable='lab_diabetes', lookup.valueset) AS lab_diabetes,
	IF(lookup.variable='lab_gfr', lookup.valueset) AS lab_gfr,
	IF(lookup.variable='lab_lft', lookup.valueset) AS lab_lft,
	IF(lookup.variable='proc_dialysis', lookup.valueset) AS proc_dialysis,
	IF(lookup.variable='proc_nephrectomy', lookup.valueset) AS proc_nephrectomy,
	IF(lookup.variable='proc_transplant', lookup.valueset) AS proc_transplant,
	IF(lookup.variable='rx_antibiotics', lookup.valueset) AS rx_antibiotics,
	IF(lookup.variable='rx_cancer', lookup.valueset) AS rx_cancer,
	IF(lookup.variable='rx_diabetes', lookup.valueset) AS rx_diabetes,
	IF(lookup.variable='rx_diuretics', lookup.valueset) AS rx_diuretics,
	IF(lookup.variable='rx_htn', lookup.valueset) AS rx_htn,
	IF(lookup.variable='rx_immunosuppressive', lookup.valueset) AS rx_immunosuppressive,
	IF(lookup.variable='lab_custom', lookup.valueset) AS lab_custom,
	IF(lookup.variable='rx_custom', lookup.valueset) AS rx_custom,
    SP.status,
    SP.age_at_visit,
    SP.gender,
    SP.race_display,
    SP.ethnicity_display,
    SP.enc_class_code,
    SP.enc_period_start_day,
    SP.enc_period_start_month,
    SP.enc_period_start_year,
    SP.enc_period_end_day,
    SP.encounter_ref,
    SP.subject_ref
from irae__cohort_study_population as SP
left join lookup on SP.encounter_ref = lookup.encounter_ref
