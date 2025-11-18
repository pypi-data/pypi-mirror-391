create or replace view irae__include_race as select * from (values
('http://hl7.org/fhir/us/core/StructureDefinition/us-core-race', '2028-9', 'Asian')
,('http://hl7.org/fhir/us/core/StructureDefinition/us-core-race', '2054-5', 'Black or African American')
,('http://hl7.org/fhir/us/core/StructureDefinition/us-core-race', '1002-5', 'American Indian or Alaska Native')
,('http://hl7.org/fhir/us/core/StructureDefinition/us-core-race', '2076-8', 'Native Hawaiian or Other Pacific Islander')
,('http://hl7.org/fhir/us/core/StructureDefinition/us-core-race', '2106-3', 'White')
) AS t (system, code, display) ;