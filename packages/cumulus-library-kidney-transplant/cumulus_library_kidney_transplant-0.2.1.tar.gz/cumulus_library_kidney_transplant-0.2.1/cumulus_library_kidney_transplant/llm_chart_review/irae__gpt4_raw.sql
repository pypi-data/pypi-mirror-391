CREATE EXTERNAL TABLE irae__gpt4_raw
(
    filename	                    string,

    dsa_mentioned	                boolean,
    dsa_history	                    boolean,
    dsa_present	                    string,

    infection_mentioned	            boolean,
    infection_history	            boolean,
    infection_present	            string,

    viral_mentioned	                boolean,
    viral_history	                boolean,
    viral_present	                string,

    bacterial_mentioned	            boolean,
    bacterial_history	            boolean,
    bacterial_present	            string,

    fungal_mentioned	            boolean,
    fungal_history	                boolean,
    fungal_present	                string,

    rejection_mentioned	            boolean,
    rejection_history	            boolean,
    rejection_present	            string,

    failure_mentioned	            boolean,
    failure_history	                boolean,
    failure_present	                string,

    ptld_mentioned	                boolean,
    ptld_history	                boolean,
    ptld_present	                string,

    cancer_mentioned	            boolean,
    cancer_history	                boolean,
    cancer_present	                string,

    donor_date_mentioned	        boolean,
    donor_date	                    date,
    donor_type_mentioned	        boolean,
    donor_type	                    string,
    donor_relationship_mentioned    boolean,
    donor_relationship              string,
    donor_hla_quality_mentioned	    boolean,
    donor_hla_quality	            string,
    donor_hla_mismatch_mentioned	boolean,
    donor_hla_mismatch	            string,

    rx_therapeutic_mentioned	    boolean,
    rx_therapeutic_level	        string,
    rx_therapeutic_sub	            string,
    rx_therapeutic_supra	        string,

    rx_compliance_mentioned	        boolean,
    rx_compliance_level	            string,
    rx_compliance_partial	        string,
    rx_compliance_non	            string,

    error_found                     boolean
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION 's3://cumulus-analytics/andy/irae/gpt4/July17/'
TBLPROPERTIES ("skip.header.line.count"="1");

