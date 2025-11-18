create or replace view irae__lab_mycophenolate as select * from (values

('http://loinc.org','23905-3','Mycophenolate, Blood'),
('http://loinc.org','23906-1','Mycophenolate glucuronide, Blood'),
('http://loinc.org','55806-4','Mycophenolate, Blood'),
('http://loinc.org','55807-2','Mycophenolate glucuronide, Blood'),
('http://loinc.org','70211-8','Mycophenolate, Blood'),
('http://loinc.org','72667-9','Mycophenolate trough, Blood'),
('http://loinc.org','72985-5','Mycophenolate induced neutrophil IgM, Blood'),
('http://loinc.org','72986-3','Mycophenolate induced neutrophil IgG, Blood'),
('http://loinc.org','73252-9','Mycophenolate induced platelet IgM, Blood'),
('http://loinc.org','73253-7','Mycophenolate induced platelet IgG, Blood'),
('http://loinc.org','73680-1','Mycophenolate Peak, Blood'),
('http://loinc.org','80697-6','Mycophenolate acyl-glucuronide, Blood'),
('http://loinc.org','87432-1','Mycophenolate and Mycophenolate glucuronide panel, Blood')
) AS t (system,code,display) ;