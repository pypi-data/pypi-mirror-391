create or replace view irae__lab_hemoglobin_a1c as select * from (values

('http://loinc.org','17855-8','HbA1c/Total Hgb, Blood'),
('http://loinc.org','17856-6','HbA1c/Total Hgb, Blood'),
('http://loinc.org','41995-2','HbA1c, Blood'),
('http://loinc.org','4548-4','HbA1c/Total Hgb, Blood'),
('http://loinc.org','4549-2','HbA1c/Total Hgb, Blood'),
('http://loinc.org','55454-3','HbA1c, Blood'),
('http://loinc.org','59261-8','HbA1c/Total Hgb Standardized per IFCC-RMP for CDT, Blood'),
('http://loinc.org','62388-4','HbA1c/Total Hgb, Blood'),
('http://loinc.org','71875-9','HbA1c/Total Hgb, Blood'),
('http://loinc.org','86910-7','HbA1c'),
('http://loinc.org','96595-4','HbA1c/Total Hgb, Dried blood spot')
) AS t (system,code,display) ;