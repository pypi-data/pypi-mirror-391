create or replace view irae__include_enc_class as select * from (values
('http://terminology.hl7.org/ValueSet/v3-ActEncounterCode', 'AMB', 'ambulatory')
,('http://terminology.hl7.org/ValueSet/v3-ActEncounterCode', 'EMER', 'emergency')
,('http://terminology.hl7.org/ValueSet/v3-ActEncounterCode', 'FLD', 'field')
,('http://terminology.hl7.org/ValueSet/v3-ActEncounterCode', 'HH', 'home health')
,('http://terminology.hl7.org/ValueSet/v3-ActEncounterCode', 'IMP', 'inpatient encounter')
,('http://terminology.hl7.org/ValueSet/v3-ActEncounterCode', 'ACUTE', 'inpatient acute')
,('http://terminology.hl7.org/ValueSet/v3-ActEncounterCode', 'NONAC', 'inpatient non-acute')
,('http://terminology.hl7.org/ValueSet/v3-ActEncounterCode', 'OBSENC', 'observation encounter')
,('http://terminology.hl7.org/ValueSet/v3-ActEncounterCode', 'PRENC', 'pre-admission')
,('http://terminology.hl7.org/ValueSet/v3-ActEncounterCode', 'SS', 'short stay')
,('http://terminology.hl7.org/ValueSet/v3-ActEncounterCode', 'VR', 'virtual')
) AS t (system, code, display) ;