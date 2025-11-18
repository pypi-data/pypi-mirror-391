create or replace view irae__lab_autoimmune_serum_rf as select * from (values
('http://loinc.org', '11572-5', 'Rheumatoid factor [Units/volume] in Serum or Plasma')
,('http://loinc.org', '15204-1', 'Rheumatoid factor [Titer] in Serum by Nephelometry')
,('http://loinc.org', '15205-8', 'Rheumatoid factor [Units/volume] in Serum by Nephelometry')
,('http://loinc.org', '17857-4', 'Rheumatoid factor [Titer] in Serum')
,('http://loinc.org', '5299-3', 'Rheumatoid factor [Titer] in Serum by Latex agglutination')
,('http://loinc.org', '5300-9', 'Rheumatoid factor [Titer] in Serum by Sheep Cell Agglutination')
,('http://loinc.org', '6928-6', 'Rheumatoid factor [Units/volume] in Serum by Immunoassay')
) AS t (system, code, display) ;