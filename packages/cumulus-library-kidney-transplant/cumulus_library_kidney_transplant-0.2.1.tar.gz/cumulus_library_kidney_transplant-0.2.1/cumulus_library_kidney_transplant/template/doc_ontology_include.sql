create or replace VIEW $prefix__doc_ontology_include as
select  system,
        code,
        display,
        keyword,
        'kind' as include_reason
from    $prefix__doc_ontology_kind
UNION ALL
select  system,
        code,
        display,
        keyword,
        'role' as include_reason
from    $prefix__doc_ontology_role
UNION ALL
select  system,
        code,
        display,
        keyword,
        'service' as include_reason
from    $prefix__doc_ontology_service
UNION ALL
select  system,
        code,
        display,
        keyword,
        'domain' as include_reason
from    $prefix__doc_ontology_domain

