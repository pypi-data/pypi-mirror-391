create or replace view irae__lab_creatinine_urine_protein_cr_ratio as select * from (values
('http://loinc.org', '13801-6', 'Protein/Creatinine [Mass Ratio] in 24 hour Urine')
,('http://loinc.org', '2890-2', 'Protein/Creatinine [Mass Ratio] in Urine')
,('http://loinc.org', '34366-5', 'Protein/Creatinine [Ratio] in Urine')
,('http://loinc.org', '40486-3', 'Protein/Creatinine [Ratio] in 24 hour Urine')
,('http://loinc.org', '60678-0', 'Protein/Creatinine [Mass Ratio] in 12 hour Urine')
) AS t (system, code, display) ;