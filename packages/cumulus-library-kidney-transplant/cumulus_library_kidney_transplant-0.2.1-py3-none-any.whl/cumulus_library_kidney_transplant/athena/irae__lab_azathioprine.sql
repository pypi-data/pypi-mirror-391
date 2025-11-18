create or replace view irae__lab_azathioprine as select * from (values

('http://loinc.org','16419-4','azaTHIOprine, Blood'),
('http://loinc.org','43924-0','azaTHIOprine, Blood')
) AS t (system,code,display) ;