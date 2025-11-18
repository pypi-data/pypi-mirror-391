create or replace view irae__lab_ketone_urine as select * from (values

('http://loinc.org','12448-7','Ketones after Fast, Urine'),
('http://loinc.org','12449-5','Ketones 1 hr after challenge, Urine'),
('http://loinc.org','12450-3','Ketones 2 hr after challenge, Urine'),
('http://loinc.org','12451-1','Ketones 3 hr after challenge, Urine'),
('http://loinc.org','13009-6','Methyl ethyl ketone, Urine'),
('http://loinc.org','17269-2','Methyl isobutyl ketone, Urine'),
('http://loinc.org','21236-5','Cyclohexanone, Urine'),
('http://loinc.org','21245-6','Diisobutylketone, Urine'),
('http://loinc.org','25706-3','Ketones 2 hr after glucose, Urine'),
('http://loinc.org','25707-1','Ketones 4 hr after glucose, Urine'),
('http://loinc.org','31165-4','Methyl butyl ketone, Urine'),
('http://loinc.org','31166-2','Methyl isoamyl ketone, Urine'),
('http://loinc.org','31167-0','Methyl propyl ketone, Urine'),
('http://loinc.org','31184-5','Methyl amyl ketone, Urine'),
('http://loinc.org','35665-9','Acetone, Urine'),
('http://loinc.org','49779-2','Ketones, Urine'),
('http://loinc.org','50557-8','Ketones, Urine'),
('http://loinc.org','5570-7','Acetone, Urine'),
('http://loinc.org','5797-6','Ketones, Urine')
) AS t (system,code,display) ;