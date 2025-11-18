create or replace view irae__doc_biopsy_muscle as select * from (values
('http://loinc.org', '34681-7', 'Biopsy [Interpretation] in Muscle Narrative')
,('http://loinc.org', '65751-0', 'Muscle Pathology biopsy report')
) AS t (system, code, display) ;