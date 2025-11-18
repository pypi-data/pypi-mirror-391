create or replace view irae__doc_biopsy_kidney as select * from (values
('http://loinc.org', '65757-7', 'Kidney Pathology biopsy report')
) AS t (system, code, display) ;