create or replace view irae__rx_belatacept as select * from (values

('http://www.nlm.nih.gov/research/umls/rxnorm','1112973','belatacept'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1112976','belatacept 250 MG Injection'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1112977','Nulojix'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1112980','Nulojix 250 MG Injection'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1155316','belatacept Injectable Product'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1178807','Nulojix Injectable Product'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1804970','belatacept 250 MG'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1804971','belatacept Injection'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1804973','belatacept 250 MG [Nulojix]'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1804974','belatacept Injection [Nulojix]')
) AS t (system,code,display) ;