1. Load GPT4 results from S3
  * [irae__gpt4_raw.sql](irae__gpt4_raw.sql)

2. Parse GPT4 output to ensure proper not null NotMentioned, NoneOfTheAbove
  * [irae__gpt4_parsed.sql](irae__gpt4_parsed.sql)

3. Download parsed CSV from athena 

 `select * from irae__gpt4_parsed` 

4. Term Frequency for each column at the subject/encounter level
* [rank_llm.py](../count/rank_llm.py) main() outputs  
  * athena-no-spans-july-17.csv.all.cnt.tsv 
  * athena-no-spans-july-17.csv.first.cnt.tsv
* [irae__gpt4_term_freq_all.sql](irae__gpt4_term_freq_all.sql)
* [irae__gpt4_term_freq_first.sql](irae__gpt4_term_freq_first.sql)

5. Link to FHIR Encounter data 
  * [irae__gpt4_fhir.sql](irae__gpt4_fhir.sql)

6. Immunosuppression compliance : computable phenotype aggregate per encounter 
* [irae__gpt4_compliance.sql](irae__gpt4_compliance.sql)
