create or replace view irae__rx_alemtuzumab as select * from (values

('http://www.nlm.nih.gov/research/umls/rxnorm','1164265','alemtuzumab Injectable Product'),
('http://www.nlm.nih.gov/research/umls/rxnorm','117055','alemtuzumab'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1172298','Campath Injectable Product'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1594657','alemtuzumab 10 MG/ML'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1594658','1.2 ML alemtuzumab 10 MG/ML Injection'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1594659','Lemtrada'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1594660','alemtuzumab 10 MG/ML [Lemtrada]'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1594662','Lemtrada Injectable Product'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1594663','Lemtrada 12 MG in 1.2 ML Injection'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1656628','alemtuzumab 30 MG/ML'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1656629','alemtuzumab Injection'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1656631','alemtuzumab 30 MG/ML [Campath]'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1656632','alemtuzumab Injection [Campath]'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1656634','alemtuzumab 30 MG/ML Injection'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1656635','Campath 30 MG/ML Injection'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1656637','alemtuzumab Injection [Lemtrada]'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1656639','alemtuzumab 10 MG/ML Injection'),
('http://www.nlm.nih.gov/research/umls/rxnorm','1656640','Lemtrada 10 MG/ML Injection'),
('http://www.nlm.nih.gov/research/umls/rxnorm','284679','Campath'),
('http://www.nlm.nih.gov/research/umls/rxnorm','828265','1 ML alemtuzumab 30 MG/ML Injection'),
('http://www.nlm.nih.gov/research/umls/rxnorm','828267','Campath 30 MG in 1 ML Injection')
) AS t (system,code,display) ;