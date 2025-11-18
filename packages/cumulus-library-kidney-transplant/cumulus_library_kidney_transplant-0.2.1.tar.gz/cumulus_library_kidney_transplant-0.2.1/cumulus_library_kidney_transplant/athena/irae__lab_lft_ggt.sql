create or replace view irae__lab_lft_ggt as select * from (values
('http://loinc.org', '2324-2', 'Gamma glutamyl transferase [Enzymatic activity/volume] in Serum or Plasma')
,('http://loinc.org', '2325-9', 'Gamma glutamyl transferase/Aspartate aminotransferase [Enzymatic activity ratio] in Serum or Plasma')
,('http://loinc.org', '96593-9', 'Gamma glutamyl transferase [Enzymatic activity/volume] in DBS')
) AS t (system, code, display) ;