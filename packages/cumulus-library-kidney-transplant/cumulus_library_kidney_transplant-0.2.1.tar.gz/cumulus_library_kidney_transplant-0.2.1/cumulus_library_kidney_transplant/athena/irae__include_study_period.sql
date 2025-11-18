create or replace view irae__include_study_period as 
select * from (values
(date('2008-01-01'),date('2026-02-01'),True)
) AS t (period_start,period_end,include_history) ;