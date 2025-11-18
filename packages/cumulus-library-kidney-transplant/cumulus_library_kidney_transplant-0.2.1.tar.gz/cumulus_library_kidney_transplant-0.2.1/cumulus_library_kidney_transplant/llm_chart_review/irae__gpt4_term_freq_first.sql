CREATE EXTERNAL TABLE irae__gpt4_term_freq_all
(
    fhir_ref    string,
    col         string,
    val         string,
    cnt         int
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION 's3://cumulus-analytics/andy/irae/gpt4/July17/term_freq_all/'
TBLPROPERTIES ("skip.header.line.count"="1");