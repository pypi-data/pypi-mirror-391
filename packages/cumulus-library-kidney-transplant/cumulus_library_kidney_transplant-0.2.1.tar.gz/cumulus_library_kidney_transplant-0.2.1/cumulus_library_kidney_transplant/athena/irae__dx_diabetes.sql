create or replace view irae__dx_diabetes as 
 select 'dx_diabetes_ckd' as valueset, system, code, display from 
 irae__dx_diabetes_ckd
 UNION ALL
select 'dx_diabetes_complications' as valueset, system, code, display from 
 irae__dx_diabetes_complications
 UNION ALL
select 'dx_diabetes_disorder' as valueset, system, code, display from 
 irae__dx_diabetes_disorder
 UNION ALL
select 'dx_diabetes_nafld' as valueset, system, code, display from 
 irae__dx_diabetes_nafld
 UNION ALL
select 'dx_diabetes_nephropathy' as valueset, system, code, display from 
 irae__dx_diabetes_nephropathy
 UNION ALL
select 'dx_diabetes_pre' as valueset, system, code, display from 
 irae__dx_diabetes_pre
 UNION ALL
select 'dx_diabetes_preexisting' as valueset, system, code, display from 
 irae__dx_diabetes_preexisting
 UNION ALL
select 'dx_diabetes_retinopathy' as valueset, system, code, display from 
 irae__dx_diabetes_retinopathy
 UNION ALL
select 'dx_diabetes_t1d' as valueset, system, code, display from 
 irae__dx_diabetes_t1d
 UNION ALL
select 'dx_diabetes_t2d' as valueset, system, code, display from 
 irae__dx_diabetes_t2d
 UNION ALL
select 'dx_diabetes_t2d_related_dx' as valueset, system, code, display from 
 irae__dx_diabetes_t2d_related_dx