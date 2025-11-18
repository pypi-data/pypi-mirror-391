create or replace view irae__lab_cbc_with_diff as select * from (values
('http://loinc.org', '57021-8', 'CBC W Auto Differential panel - Blood')
,('http://loinc.org', '57022-6', 'CBC W Reflex Manual Differential panel - Blood')
,('http://loinc.org', '57782-5', 'CBC W Ordered Manual Differential panel - Blood')
,('http://loinc.org', '58410-2', 'CBC panel - Blood by Automated count')
,('http://loinc.org', '69738-3', 'Differential panel, method unspecified - Blood')
,('http://loinc.org', '69742-5', 'CBC W Differential panel, method unspecified - Blood')
,('http://loinc.org', '74412-8', 'CBC W Differential panel - Cord blood')
) AS t (system, code, display) ;