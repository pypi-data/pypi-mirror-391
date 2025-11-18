create or replace view irae__doc_biopsy_skin as select * from (values
('http://loinc.org', '65754-4', 'Skin Pathology biopsy report')
) AS t (system, code, display) ;