create or replace view irae__include_gender as select * from (values
('http://hl7.org/fhir/ValueSet/administrative-gender', 'female', 'female')
,('http://hl7.org/fhir/ValueSet/administrative-gender', 'male', 'male')
,('http://hl7.org/fhir/ValueSet/administrative-gender', 'other', 'other')
,('http://hl7.org/fhir/ValueSet/administrative-gender', 'unknown', 'unknown')
) AS t (system, code, display) ;