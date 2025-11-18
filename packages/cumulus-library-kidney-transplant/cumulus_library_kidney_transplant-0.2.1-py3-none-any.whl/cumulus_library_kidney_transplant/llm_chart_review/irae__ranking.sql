create TABLE irae__ranking as select * from (values

-- DocumentedStatus
 ('documented', 'DocumentedTrue', 1)
,('documented', 'DocumentedFalse', -1)
,('documented', 'NotMentioned', 0)
        
-- Evidence Ranking 
,('evidence', 'BiopsyProven', 4)
,('evidence', 'Confirmed', 3)
,('evidence', 'Treatment', 2)
,('evidence', 'Suspected', 1)
,('evidence', 'NoneOfTheAbove', 0)
    
-- Donor Characteristics
,('donor', 'Living', 1)
,('donor', 'Deceased', -1)
,('donor', 'NotMentioned', 0)

,('donor', 'Related', 1)
,('donor', 'Unrelated', -1)
,('donor', 'NotMentioned', 0)

-- HLA Match Quality
,('hla', 'Well', 6-1)
,('hla', 'Moderate', 6-3)
,('hla', 'Poor', 6-5)
,('hla', 'NotMentioned', 0)

-- HLA Mismatches (6 minus #mismatched)
,('hla', 'Zero', 6)
,('hla', 'One', 6-1)
,('hla', 'Two', 6-2)
,('hla', 'Three', 6-3)
,('hla', 'Four', 6-4)
,('hla', 'Five', 6-5)
,('hla', 'Six', 6-6)
,('hla', 'NotMentioned', 0)

) AS t (topic, code, ranking) ;