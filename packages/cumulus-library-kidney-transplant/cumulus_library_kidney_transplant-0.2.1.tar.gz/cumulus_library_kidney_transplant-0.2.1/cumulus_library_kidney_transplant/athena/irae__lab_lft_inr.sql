create or replace view irae__lab_lft_inr as select * from (values
('http://loinc.org', '34714-6', 'INR in Blood by Coagulation assay')
,('http://loinc.org', '38875-1', 'INR in Platelet poor plasma or blood by Coagulation assay')
,('http://loinc.org', '46418-0', 'INR in Capillary blood by Coagulation assay')
,('http://loinc.org', '52129-4', 'INR in Platelet poor plasma by Coagulation assay --post heparin neutralization')
,('http://loinc.org', '6301-6', 'INR in Platelet poor plasma by Coagulation assay')
) AS t (system, code, display) ;