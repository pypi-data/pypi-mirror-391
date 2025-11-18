create or replace view irae__lab_autoimmune_blood_esr as select * from (values
('http://loinc.org', '18184-2', 'Erythrocyte sedimentation rate by 2H Westergren method')
,('http://loinc.org', '30341-2', 'Erythrocyte sedimentation rate')
,('http://loinc.org', '43402-7', 'Erythrocyte sedimentation rate by 15 minute reading')
,('http://loinc.org', '4537-7', 'Erythrocyte sedimentation rate by Westergren method')
,('http://loinc.org', '4538-5', 'Erythrocyte sedimentation rate by Wintrobe method')
,('http://loinc.org', '82477-1', 'Erythrocyte sedimentation rate by Photometric method')
) AS t (system, code, display) ;