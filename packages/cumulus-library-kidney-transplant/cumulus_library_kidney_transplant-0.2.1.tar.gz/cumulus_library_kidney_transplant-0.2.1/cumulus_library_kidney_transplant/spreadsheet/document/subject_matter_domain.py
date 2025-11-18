##############################################################################
#
# Document.SubjectMatterDomain
#
# INCLUDE contains clinical specialties selected for relevance to :
#   transplants / surgery
#   pharmacology
#   kidney / urology
#   cancer / oncology / dermatology (skin cancers)
#   pathology / laboratory / biopsy
#   infectious disease(s)
#   dialysis (return to) --> graft failure
#   dying / pastoral visits --> death
#
##############################################################################
INCLUDE = {
# 'Mental health', 	# 87
# 'Cardiovascular disease', 	# 77
'Surgery', 	# 64
'Hematology', 	# 57
# 'Pulmonary disease', 	# 52
# 'Geriatric medicine', 	# 50
# 'Psychiatry', 	# 49
# 'Primary care', 	# 47
# 'Ophthalmology', 	# 46
# 'Physical medicine and rehab', 	# 45
# 'Obstetrics', 	# 42
'Pharmacology', 	# 41
# 'Physical therapy', 	# 40
'Urology', 	# 39
'Immunology', 	# 39
# 'Palliative care', 	# 39
'Medical Oncology', 	# 38
# 'Gynecology', 	# 37
# 'Nutrition and dietetics', 	# 37
# 'Orthopaedic surgery', 	# 37
# 'Allergy', 	# 37
'Vascular surgery', 	# 37
# 'Plastic surgery', 	# 36
# 'Pain medicine', 	# 36
# 'Internal medicine', 	# 35
# 'Gastroenterology', 	# 35
# 'Neurology', 	# 35
# 'Neurological surgery', 	# 35
'Nephrology', 	# 35
# 'Obstetrics and gynecology', 	# 34
# 'Thoracic and cardiac surgery', 	# 33
# 'General medicine', 	# 33
'Dermatology', 	# 33
# 'Dentistry', 	# 32
# 'Otolaryngology', 	# 32
# 'Podiatry', 	# 31
# 'Psychology', 	# 30
'Infectious disease', 	# 30
# 'Occupational therapy', 	# 30
# 'Pediatrics', 	# 30
# 'Multi-specialty program', 	# 29
# 'Spinal cord injury medicine', 	# 29
# 'Speech-language pathology', 	# 28
'Anesthesiology', 	# 28
# 'Addiction medicine', 	# 27
# 'Critical care medicine', 	# 27
'Radiation oncology', 	# 27
# 'Endocrinology', 	# 27
# 'Rheumatology', 	# 26
'Oncology', 	# 26
'Transplant surgery', 	# 25
# 'Recreational therapy', 	# 25
# 'Colon and rectal surgery', 	# 24
# 'Cardiac surgery', 	# 24
# 'Diabetology', 	# 24
# 'Oral and maxillofacial surgery', 	# 24
# 'Neonatal perinatal medicine', 	# 24
# 'Respiratory therapy', 	# 24
# 'Radiology', 	# 23
# 'Audiology', 	# 23
'Emergency medicine', 	# 23
# 'Heart failure', 	# 22
# 'Clinical genetics', 	# 22
'Pediatric surgery', 	# 21
'Pastoral care', 	# 21
# 'Hepatology', 	# 19
# 'Community health care', 	# 18
# 'Family medicine', 	# 17
# 'Child and adolescent psychiatry', 	# 17
# 'Optometry', 	# 17
# 'Wound care management', 	# 16
# 'Womens health', 	# 16
# 'Trauma', 	# 16
'Surgical oncology', 	# 16
# 'Interventional radiology', 	# 16
'Dialysis', 	# 16
# 'Maternal and fetal medicine', 	# 15
# 'Sports medicine', 	# 15
# 'Gynecologic oncology', 	# 14
# 'Developmental-behavioral pediatrics', 	# 14
# 'Sleep medicine', 	# 14
# 'Adolescent medicine', 	# 14
# 'Reproductive endocrinology and infertility', 	# 14
# 'Kinesiotherapy', 	# 14
# 'Surgery of the hand', 	# 13
# 'Nuclear medicine', 	# 13
# 'Neurology w special qualifications in child neuro', 	# 13
# 'Research', 	# 13
# 'Medical aid in dying', 	# 13 TODO ??
# 'Pediatric pulmonology', 	# 13
'Clinical pathology', 	# 12
# 'Orthotics prosthetics', 	# 12
# 'Interventional cardiology', 	# 12
# 'Bariatric surgery', 	# 12
# 'Pediatric cardiology', 	# 12
# 'Wound, Ostomy, and Continence Care', 	# 12
'Pediatric hematology-oncology', 	# 12
'Pediatric transplant hepatology', 	# 12
# 'Pediatric gastroenterology', 	# 11
# 'Pediatric endocrinology', 	# 11
# 'Pediatric otolaryngology', 	# 11
'Pediatric urology', 	# 11
# 'Hospitalist', 	# 11
'Transplant cardiology', 	# 11
# 'Vocational rehabilitation', 	# 11
# 'Preventive medicine', 	# 10
# 'Occupational medicine', 	# 10
'Pediatric nephrology', 	# 10
# 'Burn management', 	# 10
# 'Pediatric rheumatology', 	# 10
# 'Rapid response', 	# 9
# 'Thromboembolism', 	# 9
'Blood banking and transfusion medicine', 	# 9
# 'Breastfeeding', 	# 9
# 'Clinical cardiac electrophysiology', 	# 9
'Pediatric dermatology', 	# 9
'Pediatric infectious diseases', 	# 9
'Solid organ transplant', 	# 9
# 'Integrative medicine', 	# 9
# 'Chiropractic medicine', 	# 8
# 'Clinical neurophysiology', 	# 8
# 'Obesity medicine', 	# 7
'Pathology', 	# 7
# 'Polytrauma', 	# 7
# 'Hospice care', 	# 7
# 'Eating disorders', 	# 7
# 'Vascular neurology', 	# 7
'Bone marrow transplant', 	# 7
# 'Pharmacogenomics', 	# 7
# 'Neuropsychology', 	# 6
# 'Public health', 	# 6
# 'Chiropody', 	# 6
'Therapeutic apheresis', 	# 6
# 'Ethics', 	# 5
# 'Osteopathic medicine', 	# 5
# 'Child and adolescent psychology', 	# 5
# 'Aerospace medicine', 	# 4
# 'Vascular Access', 	# 4
# 'Undersea and hyperbaric medicine', 	# 4
# 'Spinal surgery', 	# 4
# 'Brain injury', 	# 4
# 'Acupuncture', 	# 3
# 'Environmental health', 	# 3
'Medical toxicology', 	# 3
# 'Cleft and Craniofacial', 	# 2
'Tumor board', 	# 2
# 'Aerodigestive medicine', 	# 2
'HIV', 	# 2
# 'Addiction psychiatry', 	# 2
# 'Clinical biochemical genetics', 	# 2
# 'Birth defects', 	# 2
'Surgical critical care', 	# 2
# 'Child life', 	# 2
'Clinical pharmacology', 	# 2
# 'Epilepsy', 	# 2
# 'Orthopaedic', 	# 1
# 'Trauma Surgery', 	# 1
# 'Pediatric critical care medicine', 	# 1
# 'Medical genetics', 	# 1
# 'Social Care', 	# 1
# 'Multidisciplinary', 	# 1
'Chemical pathology', 	# 1
# 'Forensic medicine', 	# 1
# 'Pediatric rehabilitation medicine', 	# 1
'Medical microbiology - pathology', 	# 1
}