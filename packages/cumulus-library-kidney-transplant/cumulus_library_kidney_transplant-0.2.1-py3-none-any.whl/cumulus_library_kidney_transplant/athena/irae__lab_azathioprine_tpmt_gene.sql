create or replace view irae__lab_azathioprine_tpmt_gene as select * from (values

('http://loinc.org','100663-4','TPMT gene c.460G>A&c.719A>G, Blood'),
('http://loinc.org','21563-2','Thiopurine methyltransferase, Red blood cells'),
('http://loinc.org','36922-3','TPMT gene targeted mutation analysis, Blood or tissue specimen'),
('http://loinc.org','41048-0','TPMT gene targeted mutation analysis, Blood or tissue specimen'),
('http://loinc.org','43421-7','Thiopurine methyltransferase, Red blood cells'),
('http://loinc.org','49653-9','TPMT gene c.719A>G, Blood or tissue specimen'),
('http://loinc.org','49654-7','TPMT gene c.238G>C, Blood or tissue specimen'),
('http://loinc.org','49655-4','TPMT gene c.460G>A, Blood or tissue specimen'),
('http://loinc.org','53819-9','Thiopurine methyltransferase, Blood'),
('http://loinc.org','63454-3','TPMT gene variants tested for, Blood or tissue specimen'),
('http://loinc.org','71356-0','TPMT gene c.238G>C+460G>A+719A>G, Blood or tissue specimen'),
('http://loinc.org','79468-5','Thiopurine methyltransferase, Red blood cells'),
('http://loinc.org','79713-4','TPMT gene product metabolic activity interpretation, Blood or tissue specimen'),
('http://loinc.org','80738-8','TPMT gene targeted mutation analysis, Blood or tissue specimen'),
('http://loinc.org','91139-6','Thiopurine methyltransferase activity panel, Red blood cells'),
('http://loinc.org','91141-2','Thiopurine methyltransferase, Red blood cells'),
('http://loinc.org','91142-0','Thiopurine methyltransferase, Red blood cells'),
('http://loinc.org','91143-8','Thiopurine methyltransferase, Red blood cells'),
('http://loinc.org','93193-1','TPMT gene and NUDT15 gene targeted mutation analysis, Blood or tissue specimen')
) AS t (system,code,display) ;