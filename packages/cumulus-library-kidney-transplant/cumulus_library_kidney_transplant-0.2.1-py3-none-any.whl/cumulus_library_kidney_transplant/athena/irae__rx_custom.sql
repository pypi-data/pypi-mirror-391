create or replace view irae__rx_custom as 
 select 'rx_alemtuzumab' as valueset, system, code, display from 
 irae__rx_alemtuzumab
 UNION ALL
select 'rx_atg' as valueset, system, code, display from 
 irae__rx_atg
 UNION ALL
select 'rx_azathioprine' as valueset, system, code, display from 
 irae__rx_azathioprine
 UNION ALL
select 'rx_basiliximab' as valueset, system, code, display from 
 irae__rx_basiliximab
 UNION ALL
select 'rx_belatacept' as valueset, system, code, display from 
 irae__rx_belatacept
 UNION ALL
select 'rx_cyclosporin' as valueset, system, code, display from 
 irae__rx_cyclosporin
 UNION ALL
select 'rx_cytogam' as valueset, system, code, display from 
 irae__rx_cytogam
 UNION ALL
select 'rx_everolimus' as valueset, system, code, display from 
 irae__rx_everolimus
 UNION ALL
select 'rx_ig' as valueset, system, code, display from 
 irae__rx_ig
 UNION ALL
select 'rx_ivig' as valueset, system, code, display from 
 irae__rx_ivig
 UNION ALL
select 'rx_methylprednisolone' as valueset, system, code, display from 
 irae__rx_methylprednisolone
 UNION ALL
select 'rx_mycophenolate' as valueset, system, code, display from 
 irae__rx_mycophenolate
 UNION ALL
select 'rx_prednisolone' as valueset, system, code, display from 
 irae__rx_prednisolone
 UNION ALL
select 'rx_prednisone' as valueset, system, code, display from 
 irae__rx_prednisone
 UNION ALL
select 'rx_rituximab' as valueset, system, code, display from 
 irae__rx_rituximab
 UNION ALL
select 'rx_sirolimus' as valueset, system, code, display from 
 irae__rx_sirolimus
 UNION ALL
select 'rx_tacrolimus' as valueset, system, code, display from 
 irae__rx_tacrolimus