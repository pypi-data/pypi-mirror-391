create or replace view irae__dx_cancer as 
 select 'dx_cancer_melanoma_malignant' as valueset, system, code, display from 
 irae__dx_cancer_melanoma_malignant