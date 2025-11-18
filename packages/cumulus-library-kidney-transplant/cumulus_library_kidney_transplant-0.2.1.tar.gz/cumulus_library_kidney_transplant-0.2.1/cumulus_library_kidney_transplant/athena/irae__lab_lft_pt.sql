create or replace view irae__lab_lft_pt as select * from (values
('http://loinc.org', '25742-8', 'Prothrombin Fragment 1.2 [Moles/volume] in Serum or Plasma')
,('http://loinc.org', '27824-2', 'Prothrombin Fragment 1.2 Ag [Moles/volume] in Serum or Plasma by Immunoassay')
,('http://loinc.org', '42638-7', 'Prothrombin time (PT) in Platelet poor plasma by Coagulation 1:1 saline')
,('http://loinc.org', '46417-2', 'Prothrombin time (PT) in Capillary blood by Coagulation assay')
,('http://loinc.org', '5900-6', 'Prothrombin Fragment 1.2 [Units/volume] in Serum or Plasma')
,('http://loinc.org', '5901-4', 'Prothrombin time (PT) in Control Platelet poor plasma by Coagulation assay')
,('http://loinc.org', '5902-2', 'Prothrombin time (PT)')
,('http://loinc.org', '5964-2', 'Prothrombin time (PT) in Blood by Coagulation assay')
) AS t (system, code, display) ;