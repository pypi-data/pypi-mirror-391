create or replace view irae__sample_select_for_review_index as
WITH
choose_sample_tables as
(
    select * from irae__sample_casedef_index
),
loinc as
(
    select  distinct
            CODE    as loinc_code,
            STR     as loinc_display
    from    umls.MRCONSO
    where   SAB='LNC'
    and     TTY='LC'
),
sample_casedef as
(
    select  distinct
            subject_ref,
            encounter_ref,
            documentreference_ref,
            (doc_type_system = 'http://loinc.org') as loinc_matched,
            loinc_display,
            doc_type_code,
            doc_type_system,
            group_name,
            case
	            when    doc_type_system='http://loinc.org'
		            then    loinc_display
	            else    doc_type_display
			end as  doc_type_display
    from    choose_sample_tables as choice
    left join
            loinc on choice.doc_type_code = loinc.loinc_code
),
general_keywords as
(
    SELECT  *
    FROM    sample_casedef
    WHERE
	    -- Exclusion criteria - ignore nursing notes for now
	    (       lower(doc_type_display) NOT like 'nursing'
			and lower(doc_type_display) NOT like 'nurse')
    AND
	    -- Inclusion criteria - the doc-type code looks like any of these
		(       upper(doc_type_display) like '%MSICU%'
			or  upper(doc_type_display) like '%MS-ICU%'
			or  upper(doc_type_display) like '%HLA%'
			or  lower(doc_type_display) like '%leukocyte%'
			or  lower(doc_type_display) like '%antigen%'
			or  lower(doc_type_display) like '%med–surg%'
			or  lower(doc_type_display) like '%surgical%'
			or  lower(doc_type_display) like '%surgery%'
			or  lower(doc_type_display) like '%kidney%'
			or  lower(doc_type_display) like '%renal%'
			or  lower(doc_type_display) like '%nephrology%'
			or  lower(doc_type_display) like '%urology%'
			or  lower(doc_type_display) like '%transplant%'
			or  lower(doc_type_display) like '%donor%'
			or  lower(doc_type_display) like '%recipient%'
			or  lower(doc_type_display) like '%match%'
			or  lower(doc_type_display) like '%graft%'
			or  lower(doc_type_display) like '%biopsy%'
			or  lower(doc_type_display) like '%pathology%'
			or  lower(doc_type_display) like '%banff%'
			or  lower(doc_type_display) like '%specimen%'
			or  lower(doc_type_display) like '%tissue%'
			or  lower(doc_type_display) like '%social work%'
			or  lower(doc_type_display) like '%oncology%'
			or  lower(doc_type_display) like '%cancer%'
			or  lower(doc_type_display) like '%pharmacy%'
			or  lower(doc_type_display) like '%infectious disease%'
			or  upper(doc_type_display) like '%ID CONSULT%'
		)
),
site_specific as (
    select *
	from    sample_casedef
	-- Inclusion criteria - specific doctypes we know in BCH that we are interested in
    where   doc_type_display in (
            'Nephrology Communication',
            'Nephrology Inpatient MD',
            'Nephrology Visit',
            'Phone Message/Call',
            'Discharge Summary',
            'Renal Transplant Clinic Note 028',
            'Nephrology Admission MD',
            'Urology Inpatient MD',
            'Urology Visit',
            'ED Clinical Depart',
            'Infectious Diseases Consultation',
            'MSICU Progress Attending MD',
            'Nephrology Consultation',
            'Social Work Assessment Outpatient',
            'Pharmacy Transplant Inpatient',
            'Oncology Inpatient MD',
            'Dialysis Comprehensive Progress Note',
            'AMB - Nephrology Uncategorized')
)
select distinct documentreference_ref,
    subject_ref,
    encounter_ref,
    doc_type_code,
    doc_type_display,
    doc_type_system,
    group_name
from general_keywords
UNION ALL
select distinct documentreference_ref,
    subject_ref,
    encounter_ref,
    doc_type_code,
    doc_type_display,
    doc_type_system,
    group_name
from site_specific;