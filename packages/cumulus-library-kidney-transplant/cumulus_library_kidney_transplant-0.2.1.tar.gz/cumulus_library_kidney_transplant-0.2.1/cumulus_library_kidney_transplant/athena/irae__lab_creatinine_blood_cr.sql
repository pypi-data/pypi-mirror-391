create or replace view irae__lab_creatinine_blood_cr as select * from (values
('http://loinc.org', '11041-1', 'Creatinine [Mass/volume] in Serum or Plasma --post dialysis')
,('http://loinc.org', '11042-9', 'Creatinine [Mass/volume] in Serum or Plasma --pre dialysis')
,('http://loinc.org', '14682-9', 'Creatinine [Moles/volume] in Serum or Plasma')
,('http://loinc.org', '2160-0', 'Creatinine [Mass/volume] in Serum or Plasma')
,('http://loinc.org', '38483-4', 'Creatinine [Mass/volume] in Blood')
,('http://loinc.org', '40123-2', 'Creatinine [Moles/volume] in Serum or Plasma --12 hours post XXX challenge')
,('http://loinc.org', '40248-7', 'Creatinine [Mass/volume] in Serum or Plasma --baseline')
,('http://loinc.org', '40264-4', 'Creatinine [Moles/volume] in Serum or Plasma --baseline')
,('http://loinc.org', '51619-5', 'Creatinine [Moles/volume] in Serum or Plasma --pre dialysis')
,('http://loinc.org', '51620-3', 'Creatinine [Moles/volume] in Serum or Plasma --post dialysis')
,('http://loinc.org', '59826-8', 'Creatinine [Moles/volume] in Blood')
,('http://loinc.org', '77140-2', 'Creatinine [Moles/volume] in Serum, Plasma or Blood')
) AS t (system, code, display) ;