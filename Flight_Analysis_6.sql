CREATE DATABASE IF NOT EXISTS flight_analysis;

USE DATABASE flight_analysis;

CREATE SCHEMA IF NOT EXISTS staging;

USE SCHEMA staging;

CREATE  STORAGE INTEGRATION s3_integration
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = 'S3'
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::302174038176:role/snowflake_s3_role'
    STORAGE_ALLOWED_LOCATIONS = ('s3://airport-data-divyansh/gold/');

    DESC INTEGRATION s3_integration;
    
CREATE OR REPLACE FILE FORMAT flight_analysis.staging.parquet_format
    TYPE = 'PARQUET';

CREATE OR REPLACE STAGE flight_analysis.staging.gold_stage_s3
    STORAGE_INTEGRATION = s3_integration
    URL = 's3://airport-data-divyansh/gold/'
    FILE_FORMAT = flight_analysis.staging.parquet_format;

    LIST @flight_analysis.staging.gold_stage_s3;


   CREATE OR REPLACE TABLE flight_analysis.staging.monthly_airline_kpi (
    Year INTEGER,
    Month INTEGER,
    airline_code STRING,
    Reporting_airline STRING,
    total_number_of_flights NUMBER,
    delayed_flights NUMBER,
    total_flights_cancelled NUMBER,
    total_diverted_flights NUMBER,
    avg_arrival_delay_minutes DOUBLE,
    median_arrival_delay_minutes DOUBLE,
    on_time_flights NUMBER,
    cancelled_flight_percentage DOUBLE,
    on_time_flight_percentage DOUBLE,
    non_cancelled_flight_percentage DOUBLE,
    avg_carrier_delay DOUBLE,
    avg_weather_delay DOUBLE,
    avg_security_delay DOUBLE,
    avg_late_aircraft_delay DOUBLE,
    avg_distance_travelled DOUBLE,
    total_distance_travelled DOUBLE
);



ALTER TABLE flight_analysis.staging.monthly_airline_kpi
SET DATA_RETENTION_TIME_IN_DAYS = 10;

CREATE OR REPLACE TABLE flight_analysis.staging.annual_route_performance (
    Year                    INT,
    route                   VARCHAR,
    Origin                  VARCHAR,
    Dest                    VARCHAR,
    number_of_flights       BIGINT,
    avg_arrival_delay       FLOAT,
    avg_distance_travelled  FLOAT,
    total_delayed_flights   BIGINT,
    on_time_flights         BIGINT,
    on_time_percentage      FLOAT,
    number_of_airlines      BIGINT
)
DATA_RETENTION_TIME_IN_DAYS = 10;


SHOW TABLES LIKE 'annual_route_performance' IN SCHEMA flight_analysis.staging;


CREATE OR REPLACE TABLE flight_analysis.staging.gold_airport_departure_kpi (
    Year                            INT,
    Month                           INT,
    year_month                      VARCHAR,
    Origin                          VARCHAR,
    origin_airport_name             VARCHAR,
    OriginCityName                  VARCHAR,
    OriginState                     VARCHAR,
    origin_lon                      FLOAT,
    origin_lat                      FLOAT,
    total_departures                BIGINT,
    total_cancelled_departures      BIGINT,
    avg_delayed_departure           FLOAT,
    on_time_departures              BIGINT,
    avg_route_distance              FLOAT,
    number_of_flights_operating     BIGINT,
    avg_airtime                     FLOAT,
    departure_on_time_percentage    FLOAT
)
DATA_RETENTION_TIME_IN_DAYS = 10;

SHOW TABLES LIKE 'gold_airport_departure_kpi' IN SCHEMA flight_analysis.staging;

CREATE OR REPLACE TABLE flight_analysis.staging.delay_cause_table (
    Year                                INT,
    Month                               INT,
    airline_code                        VARCHAR,
    total_minutes_delayed               FLOAT,
    total_weather_delayed_minutes       FLOAT,
    carrier_delay_minutes               FLOAT,
    security_delay_minutes              FLOAT,
    total_late_aircraft_delay_minutes   FLOAT,
    weather_delay_percentage            FLOAT,
    carrier_delay_percentage            FLOAT,
    security_delay_percentage           FLOAT,
    late_aircraft_delay_percentage      FLOAT
)
DATA_RETENTION_TIME_IN_DAYS = 10;

SHOW TABLES IN SCHEMA flight_analysis.staging;

-- Pipe 1 — monthly_airline_kpi
CREATE OR REPLACE PIPE flight_analysis.staging.monthly_airline_pipe
    AUTO_INGEST = TRUE
AS
COPY INTO flight_analysis.staging.monthly_airline_kpi
FROM @flight_analysis.staging.gold_stage_s3/flight_aggregations/
FILE_FORMAT = (TYPE = 'PARQUET')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

-- Pipe 2 — annual_route_performance
CREATE OR REPLACE PIPE flight_analysis.staging.route_performance_pipe
    AUTO_INGEST = TRUE
AS
COPY INTO flight_analysis.staging.annual_route_performance
FROM @flight_analysis.staging.gold_stage_s3/gold_route_kpi/
FILE_FORMAT = (TYPE = 'PARQUET')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

-- Pipe 3 — gold_airport_departure_kpi
CREATE OR REPLACE PIPE flight_analysis.staging.airport_departure_pipe
    AUTO_INGEST = TRUE
AS
COPY INTO flight_analysis.staging.gold_airport_departure_kpi
FROM @flight_analysis.staging.gold_stage_s3/gold_airport_departure_kpi/
FILE_FORMAT = (TYPE = 'PARQUET')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

-- Pipe 4 — delay_cause_table
CREATE OR REPLACE PIPE flight_analysis.staging.delay_cause_pipe
    AUTO_INGEST = TRUE
AS
COPY INTO flight_analysis.staging.delay_cause_table
FROM @flight_analysis.staging.gold_stage_s3/delay_cause_table/
FILE_FORMAT = (TYPE = 'PARQUET')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;


-- Step 11 - Verify Data
ALTER PIPE flight_analysis.staging.monthly_airline_pipe REFRESH;
SELECT * FROM flight_analysis.staging.monthly_airline_kpi LIMIT 5;

ALTER PIPE flight_analysis.staging.route_performance_pipe REFRESH;
SELECT * FROM flight_analysis.staging.annual_route_performance LIMIT 5;

ALTER PIPE flight_analysis.staging.airport_departure_pipe REFRESH;
SELECT * FROM flight_analysis.staging.gold_airport_departure_kpi LIMIT 5;

ALTER PIPE flight_analysis.staging.delay_cause_pipe REFRESH;
SELECT * FROM flight_analysis.staging.delay_cause_table LIMIT 5;






