create table irae__cohort_doc_biopsy as 
select * from 
 irae__cohort_study_population_doc , 
irae__doc_biopsy
WHERE
irae__cohort_study_population_doc.doc_type_code = irae__doc_biopsy.code and 
irae__cohort_study_population_doc.doc_type_system = irae__doc_biopsy.system