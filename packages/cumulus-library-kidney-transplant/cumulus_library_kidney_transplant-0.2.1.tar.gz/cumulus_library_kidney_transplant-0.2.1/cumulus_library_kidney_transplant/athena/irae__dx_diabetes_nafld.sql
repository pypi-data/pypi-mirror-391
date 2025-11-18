create or replace view irae__dx_diabetes_nafld as select * from (values
('http://snomed.info/sct', '197315008', 'Non-alcoholic fatty liver (disorder)')
,('http://snomed.info/sct', '442685003', 'Nonalcoholic steatohepatitis (disorder)')
,('http://snomed.info/sct', '716379000', 'Acute fatty liver of pregnancy (disorder)')
,('http://snomed.info/sct', '722866000', 'Non-alcoholic fatty liver disease without non-alcoholic steatohepatitis (disorder)')
,('http://hl7.org/fhir/sid/icd-10-cm', 'K75.81', 'Nonalcoholic steatohepatitis (NASH)')
,('http://hl7.org/fhir/sid/icd-10-cm', 'K76.0', 'Fatty (change of) liver, not elsewhere classified')
) AS t (system, code, display) ;