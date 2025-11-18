create or replace view irae__doc_biopsy_bone as select * from (values
('http://loinc.org', '33721-2', 'Bone marrow Pathology biopsy report')
) AS t (system, code, display) ;