import json
import base64
from botocore.exceptions import ClientError
import boto3
import logging
import traceback
from psycopg2.extras import RealDictCursor
import psycopg2
import os


def enable_logging():
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)


enable_logging()


def get_secret():
    secret_name = os.environ["SECRET_NAME"]
    region_name = os.environ["REGION"]
    secret = None
    # Create a Secrets Manager client
    session = boto3.session.Session()
    print("before secret")
    endpoint_url = f"https://secretsmanager.{region_name}.amazonaws.com"
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
        endpoint_url=endpoint_url
    )

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    except Exception as e:
        raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
    print("after secret")
    return json.loads(secret)  # returns the secret as dictionary


def cors_headers():
    return {
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,HEAD,PUT,DELETE,PATCH'
    }


def get_db_connection():

    connection = None
    secret_result = get_secret()
    username = secret_result['username']
    password = secret_result['password']
    dbname = secret_result['dbname']
    host = secret_result['host']
    port = secret_result['port']

    try:
        print("Connecting to DB and Push statements")
        connection = psycopg2.connect(
            host=host,
            database=dbname,
            user=username,
            password=password,
            port=port)
    except (Exception, psycopg2.Error) as error:
        print("Failed to init DB connection", error)

    return connection




def revenue_codes(event, context):

    result = ''
    status_code = 500
    try:
        db_connection = get_db_connection()
        query = """
        CREATE SCHEMA IF NOT EXISTS "dbo";
        CREATE USER dev_iam_ticket; 
        GRANT rds_iam TO dev_iam_ticket;
        GRANT SELECT ON ALL TABLES IN SCHEMA dbo TO dev_iam_ticket;
        GRANT USAGE ON SCHEMA dbo TO dev_iam_ticket;
        CREATE USER dev_iam_trex; 
        GRANT rds_iam TO dev_iam_trex;
        GRANT ALL PRIVILEGES ON DATABASE trex TO dev_iam_trex;
        GRANT ALL PRIVILEGES ON DATABASE trex TO t360;
        GRANT rds_iam TO dev_iam_trex;
        GRANT SELECT ON ALL TABLES IN SCHEMA dbo TO dev_iam_trex;
        GRANT USAGE ON SCHEMA dbo TO dev_iam_trex;


CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
 

SELECT relname, n_live_tup FROM pg_stat_user_tables WHERE n_live_tup <> 0 AND schemaname = 'dbo' ORDER BY n_live_tup DESC;


drop table if exists dbo.order_payments;
drop table if exists dbo.transaction_step_traffic_counts;
drop table if exists dbo.transaction_step_payments;
drop table if exists dbo.transaction_step_activities;
drop table if exists dbo.order_details;
drop table if exists dbo.ticket_status_attributes;
drop table if exists dbo.ticket_usages;
drop table if exists dbo.transaction_step_redemptions;
drop table if exists dbo.ticket_locations;
drop table if exists dbo.ticket_venues;
drop table if exists dbo.transaction_step_sales;
drop table if exists dbo.ticket_details;
drop table if exists dbo.orders;
drop table if exists dbo.ticket_barcodes;
drop table if exists dbo.transactions;
drop table if exists dbo.tickets;
drop table if exists dbo.product_variant_locations;
drop table if exists dbo.product_variant_venues;
drop table if exists dbo.product_variant_details;
drop table if exists dbo.product_variant_tiers;
drop table if exists dbo.product_variants;
drop table if exists dbo.product_group_mappings;
drop table if exists dbo.product_groups;
drop table if exists dbo.products;
drop table if exists dbo.site_venues;
drop table if exists dbo.calendar_events;
drop table if exists dbo.ticket_statuses;
drop table if exists dbo.external_systems;
drop table if exists dbo.failure_codes;
drop table if exists dbo.sales_sources;
drop table if exists dbo.payment_methods;
drop table if exists dbo.currencies;
drop table if exists dbo.operators;
drop table if exists dbo.events;
drop table if exists dbo.event_types;
drop table if exists dbo.business_dates;
drop table if exists dbo.calendars;
drop table if exists dbo.terminals;
drop table if exists dbo.locations;
drop table if exists dbo.sites;
drop table if exists dbo.payment_types;
drop table if exists dbo.venues;
drop table if exists dbo.venue_types; 
drop table if exists dbo.pass_types;
drop table if exists dbo.seasons;
drop table if exists dbo.product_types;
drop table if exists dbo.validity_types;
drop table if exists dbo.report_types;
drop table if exists dbo.revenue_codes;
drop table if exists dbo.accounting_codes;
drop table if exists dbo.attendance_group_sub_categories;
drop table if exists dbo.sections;
drop table if exists dbo.pay_types;
drop table if exists dbo.validity_calendars;
drop table if exists dbo.reason_codes;
drop table if exists dbo.transaction_activity_types;
drop table if exists dbo.usage_types;
drop table if exists dbo.descriptor_categories;
drop table if exists dbo.redemption_categories;
drop table if exists dbo.ticket_attributes;
drop table if exists dbo.ticket_attribute_types;
drop table if exists dbo.price_calc_types;
drop table if exists dbo.redemption_category_groups;
drop table if exists dbo.ticket_attribute_object_types;
drop table if exists dbo.internal_validation_types;	
drop table if exists dbo.guest_types;
 
			 			 
create table dbo.site_systems
(
	site_system_id int generated always as identity primary key,
  site_system_uid UUID not null default uuid_generate_v4(),
  site_system_code varchar(50) not null,
  site_system_name varchar(100) not null 
);
 
create unique index system_uid_idx on dbo.site_systems (site_system_uid);
create unique index system_code_idx on dbo.site_systems (site_system_code);
 
truncate table dbo.site_systems restart identity;

		 
--enum	 
create table dbo.guest_types
(
	guest_type_id int primary key,
	guest_type_name varchar(50) not null
);


create table dbo.internal_validation_types
(
	internal_validation_type_id int generated always as identity primary key,
  internal_validation_type_uid UUID not null default uuid_generate_v4(),
  internal_validation_type_code varchar(50) not null,
  internal_validation_type_name varchar(100) not null 
);
 
create unique index internal_validation_types_uid_idx on dbo.internal_validation_types (internal_validation_type_uid);
create unique index internal_validation_types_code_idx on dbo.internal_validation_types (internal_validation_type_code);
 
truncate table dbo.internal_validation_types restart identity;
  
	
create table dbo.validity_calendars
(
	validity_calendar_id bigint generated always as identity primary key,
  validity_calendar_uid UUID not null default uuid_generate_v4(),
  validity_calendar_code varchar(50) not null,
  validity_calendar_name varchar(100) not null 
);
 
create unique index validity_calendars_uid_idx on dbo.validity_calendars (validity_calendar_uid);
create unique index validity_calendars_code_idx on dbo.validity_calendars (validity_calendar_code);
 
truncate table dbo.validity_calendars restart identity;
   
	 
create table dbo.pay_types
(
	pay_type_id bigint generated always as identity primary key,
  pay_type_uid UUID not null default uuid_generate_v4(),
  pay_type_code varchar(50) not null,
  pay_type_name varchar(100) not null 
);
 
create unique index pay_types_uid_idx on dbo.pay_types (pay_type_uid);
create unique index pay_types_code_idx on dbo.pay_types (pay_type_code);
 
truncate table dbo.pay_types restart identity;
   

create table dbo.sections
(
	section_id bigint generated always as identity primary key,
  section_uid UUID not null default uuid_generate_v4(),
  section_code varchar(50) not null,
  section_name varchar(100) not null 
);
 
create unique index sections_uid_idx on dbo.sections (section_uid);
create unique index sections_code_idx on dbo.sections (section_code);
 
truncate table dbo.sections restart identity;
   

create table dbo.attendance_group_sub_categories
(
	attendance_group_sub_category_id bigint generated always as identity primary key,
  attendance_group_sub_category_uid UUID not null default uuid_generate_v4(),
  attendance_group_sub_category_code varchar(50) not null,
  attendance_group_sub_category_name varchar(100) not null 
);
 
create unique index attendance_group_sub_categories_uid_idx on dbo.attendance_group_sub_categories (attendance_group_sub_category_uid);
create unique index attendance_group_sub_categories_code_idx on dbo.attendance_group_sub_categories (attendance_group_sub_category_code);
 
truncate table dbo.attendance_group_sub_categories restart identity;
  
	
create table dbo.accounting_codes
(
	accounting_code_id bigint generated always as identity primary key,
  accounting_code_uid UUID not null default uuid_generate_v4(),
  accounting_code_code varchar(50) not null,
  accounting_code_name varchar(100) not null 
);
 
create unique index accounting_codes_uid_idx on dbo.accounting_codes (accounting_code_uid);
create unique index accounting_codes_code_idx on dbo.accounting_codes (accounting_code_code);
 
truncate table dbo.accounting_codes restart identity;
   

create table dbo.revenue_codes
(
	revenue_code_id bigint generated always as identity primary key,
  revenue_code_uid UUID not null default uuid_generate_v4(),
  revenue_code_code varchar(50) not null,
  revenue_code_name varchar(100) not null 
);
 
create unique index revenue_codes_uid_idx on dbo.revenue_codes (revenue_code_uid);
create unique index revenue_codes_code_idx on dbo.revenue_codes (revenue_code_code);
 
truncate table dbo.revenue_codes restart identity;
   
	 
create table dbo.report_types
(
	report_type_id bigint generated always as identity primary key,
  report_type_uid UUID not null default uuid_generate_v4(),
  report_type_code varchar(50) not null,
  report_type_name varchar(100) not null 
);
 
create unique index report_types_uid_idx on dbo.report_types (report_type_uid);
create unique index report_types_code_idx on dbo.report_types (report_type_code);
 
truncate table dbo.report_types restart identity;
  

--enum	 
create table dbo.validity_types
(
	validity_type_id int primary key,
	validity_type_name varchar(50) not null
);


create table dbo.venue_types
(
	venue_type_id int generated always as identity primary key,
	venue_type_name varchar(50) not null
);

truncate table dbo.venue_types restart identity;


create table dbo.payment_types
(
	payment_type_id int generated always as identity primary key,
	payment_type_name varchar(50) not null
);

truncate table dbo.payment_types restart identity;
 

create table dbo.failure_codes
(
	failure_code_id int generated always as identity primary key,
	failure_code_name varchar(50) not null
);

truncate table dbo.failure_codes restart identity;

 
create table dbo.ticket_attribute_types
(
	ticket_attribute_type_id int generated always as identity primary key,
	ticket_attribute_type_name varchar(50) not null
);

truncate table dbo.ticket_attribute_types restart identity;
 
 
create table dbo.ticket_attribute_object_types
(
	ticket_attribute_object_type_id int generated always as identity primary key,
	ticket_attribute_object_type_name varchar(50) not null
);

truncate table dbo.ticket_attribute_object_types restart identity;
  
	
create table dbo.ticket_attributes
(
	ticket_attribute_id bigint generated always as identity primary key,
  ticket_attribute_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  ticket_attribute_type_id int not null,
  ticket_attribute_object_type_id int not null,
  object_id bigint not null,
  data jsonb null,
  
  foreign key (ticket_attribute_type_id) references dbo.ticket_attribute_types(ticket_attribute_type_id), 
  foreign key (ticket_attribute_object_type_id) references dbo.ticket_attribute_object_types(ticket_attribute_object_type_id)
);
 
create unique index ticket_attributes_ticket_attribute_uid_idx on dbo.ticket_attributes (ticket_attribute_uid);
 
truncate table dbo.ticket_attributes restart identity;

--enum
create table dbo.usage_types
(
	usage_type_id int primary key,
	usage_type_name varchar(50) not null
);
 

create table dbo.ticket_statuses
(
	ticket_status_id int generated always as identity primary key,
  ticket_status_uid UUID not null default uuid_generate_v4(),
	ticket_status_code varchar(50) not null,
	ticket_status_name varchar(50) not null
);

create unique index ticket_statuses_uid_idx on dbo.ticket_statuses (ticket_status_uid);
create unique index ticket_statuses_code_idx on dbo.ticket_statuses (ticket_status_code);

truncate table dbo.ticket_statuses restart identity;
 

create table dbo.transaction_activity_types
(
	transaction_activity_type_id int generated always as identity primary key,
	transaction_activity_type_name varchar(50) not null
);

truncate table dbo.transaction_activity_types restart identity;
 

create table dbo.reason_codes
(
	reason_code_id int generated always as identity primary key,
	reason_code_name varchar(50) not null
);

truncate table dbo.reason_codes restart identity;

 
create table dbo.price_calc_types
(
	price_calc_type_id int generated always as identity primary key,
	price_calc_type_name varchar(50) not null
);

truncate table dbo.price_calc_types restart identity;

--enum
create table dbo.product_types
(
	product_type_id int primary key,
	product_type_name varchar(50) not null
);
 
   
create table dbo.sites
(
	site_id int generated always as identity primary key,
  site_uid UUID not null default uuid_generate_v4(),
  site_code varchar(50) not null,
  site_name varchar(100) not null,
  internal_system_site_id int not null,
  internal_system_site_code varchar(10) null,
	site_system_id int not null, 
	
	foreign key (site_system_id) references dbo.site_systems(site_system_id) 
);
 
create unique index sites_site_uid_idx on dbo.sites (site_uid);
create unique index sites_site_code_idx on dbo.sites (site_code);
create index sites_site_number_idx on dbo.sites (internal_system_site_id);
 
truncate table dbo.sites restart identity;

 
create table dbo.venues
(
	venue_id int generated always as identity primary key,
  venue_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  venue_code varchar(50) not null,
  venue_name varchar(100) not null,
  venue_type_id int null,
  
  foreign key (venue_type_id) references dbo.venue_types(venue_type_id) 
);
 
create unique index venues_venue_uid_idx on dbo.venues (venue_uid);
create unique index venues_venue_code_idx on dbo.venues (venue_code);
 
truncate table dbo.venues restart identity;
 

create table dbo.site_venues
(
	site_venue_id bigint generated always as identity primary key,
  site_venue_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  site_id int not null,
  venue_id int not null,
  
  foreign key (site_id) references dbo.sites(site_id),
	foreign key (venue_id) references dbo.venues(venue_id)
);
 
create unique index site_venues_site_venue_uid_idx on dbo.site_venues (site_venue_uid);
create index site_venues_site_id_idx on dbo.site_venues (site_id);
create index site_venues_venue_id_idx on dbo.site_venues (venue_id);
 
truncate table dbo.site_venues restart identity;
  

create table dbo.locations
(
	location_id int generated always as identity primary key,
  location_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  location_code varchar(50) not null,
  location_name varchar(100) not null,
  site_id int not null,
  venue_id int not null,
  
  foreign key (site_id) references dbo.sites(site_id),
	foreign key (venue_id) references dbo.venues(venue_id) 
);
 
create unique index locations_location_uid_idx on dbo.locations (location_uid);
create unique index locations_location_code_idx on dbo.locations (location_code);
create index locations_site_id_idx on dbo.locations (site_id);
create index locations_venue_id_idx on dbo.locations (venue_id);
 
truncate table dbo.locations restart identity;
 

create table dbo.terminals
(
	terminal_id bigint generated always as identity primary key,
  terminal_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  terminal_code varchar(50) not null,
  terminal_name varchar(100) not null,
  location_id int not null,
  
  foreign key (location_id) references dbo.locations(location_id) 
);
 
create unique index terminals_terminal_uid_idx on dbo.terminals (terminal_uid);
create unique index terminals_terminal_code_idx on dbo.terminals (terminal_code);
create index terminals_location_id_idx on dbo.terminals (location_id);
 
truncate table dbo.terminals restart identity;

  
create table dbo.seasons
(
	season_id int generated always as identity primary key,
  season_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  season_code varchar(50) not null,
  season_name varchar(100) not null,
  season_year int not null,
  start_date_time timestamp null,
  end_date_time timestamp null, 
  season_pass_start_date_time timestamp null,
  season_pass_end_date_time timestamp null  
);
 
create unique index seasons_season_uid_idx on dbo.seasons (season_uid);
create unique index seasons_season_code_idx on dbo.seasons (season_code);
create index seasons_season_year_idx on dbo.seasons (season_year);
 
truncate table dbo.seasons restart identity;

  
create table dbo.calendars
(
	calendar_id int generated always as identity primary key,
  calendar_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  calendar_code varchar(50) not null,
  calendar_name varchar(100) not null 
);
 
create unique index calendars_calendar_uid_idx on dbo.calendars (calendar_uid);
create unique index calendars_calendar_code_idx on dbo.calendars (calendar_code);
 
truncate table dbo.calendars restart identity;
 

create table dbo.business_dates
(
	business_date_id bigint generated always as identity primary key,
  business_date_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  business_date_code varchar(50) not null,
  business_date_name varchar(100) not null,
  date date not null  
);
 
create unique index business_dates_uid_idx on dbo.business_dates (business_date_uid);
create unique index business_dates_business_date_code_idx on dbo.business_dates (business_date_code);
create index business_dates_date_idx on dbo.business_dates (date);

truncate table dbo.business_dates restart identity;
 

create table dbo.event_types
(
	event_type_id int generated always as identity primary key,
  event_type_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  event_type_code varchar(50) not null,
  event_type_name varchar(100) not null,
  priority int null  
);
 
create unique index event_types_event_type_uid_idx on dbo.event_types (event_type_uid);
create unique index event_types_event_type_code_idx on dbo.event_types (event_type_code);
 
truncate table dbo.event_types restart identity;

 
create table dbo.events
(
	event_id int generated always as identity primary key,
  event_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  event_code varchar(50) not null,
  event_name varchar(100) not null,
  event_type_id int null,
  business_date_id int null,
  start_date_time timestamp null,
  end_date_time timestamp null,
  
  foreign key (event_type_id) references dbo.event_types(event_type_id),
	foreign key (business_date_id) references dbo.business_dates(business_date_id)
);
 
create unique index events_event_uid_idx on dbo.events (event_uid);
create unique index events_event_code_idx on dbo.events (event_code);
 
truncate table dbo.events restart identity;
  
	
create table dbo.calendar_events
(
	calendar_event_id bigint generated always as identity primary key,
  calendar_event_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  site_id int not null,
  calendar_id int not null,
  event_id int not null,
  
  foreign key (site_id) references dbo.sites(site_id),
	foreign key (calendar_id) references dbo.calendars(calendar_id),
	foreign key (event_id) references dbo.events(event_id) 
);
 
create unique index calendar_events_uid_idx on dbo.calendar_events (calendar_event_uid);
create index calendar_events_site_id_idx on dbo.calendar_events (site_id);
create index calendar_events_calendar_id_idx on dbo.calendar_events (calendar_id);
create index calendar_events_event_id_idx on dbo.calendar_events (event_id);
 
truncate table dbo.calendar_events restart identity;
 

create table dbo.pass_types
(
	pass_type_id int generated always as identity primary key,
  pass_type_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  pass_type_code varchar(50) not null,
  pass_type_name varchar(100) not null,
  is_season_pass bit not null  
);
 
create unique index pass_types_pass_type_uid_idx on dbo.pass_types (pass_type_uid);
create unique index pass_types_pass_type_code_idx on dbo.pass_types (pass_type_code);
 
truncate table dbo.pass_types restart identity;
  
	
create table dbo.currencies
(
	currency_id int generated always as identity primary key,
  currency_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  currency_code varchar(50) not null,
  currency_name varchar(100) not null,
  currency_symbol varchar(10) not null,
  conversion_rate numeric(15, 2) null  
);
 
create unique index currencies_currency_uid_idx on dbo.currencies (currency_uid);
create unique index currencies_currency_code_idx on dbo.currencies (currency_code);
 
truncate table dbo.currencies restart identity;
  

create table dbo.payment_methods
(
	payment_method_id int generated always as identity primary key,
  payment_method_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  payment_method_code varchar(50) not null,
  payment_method_name varchar(100) not null,
  payment_type_id int null,
  
  foreign key (payment_type_id) references dbo.payment_types(payment_type_id) 
);
 
create unique index payment_methods_payment_method_uid_idx on dbo.payment_methods (payment_method_uid);
create unique index payment_methods_payment_method_code_idx on dbo.payment_methods (payment_method_code);
 
truncate table dbo.payment_methods restart identity;
   

create table dbo.redemption_category_groups
(
	redemption_category_group_id int generated always as identity primary key,
  redemption_category_group_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  redemption_category_group_code varchar(50) not null,
  redemption_category_group_name varchar(100) not null,
  is_multiples_allowed bit not null 
);
 
create unique index redemption_category_groups_uid_idx on dbo.redemption_category_groups (redemption_category_group_uid);
create unique index redemption_category_groups_code_idx on dbo.redemption_category_groups (redemption_category_group_code);
 
truncate table dbo.redemption_category_groups restart identity;
   

create table dbo.redemption_categories
(
	redemption_category_id int generated always as identity primary key,
  redemption_category_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  redemption_category_code varchar(50) not null,
  redemption_category_name varchar(100) not null,
  redemption_category_group_id int null,
  
  foreign key (redemption_category_group_id) references dbo.redemption_category_groups(redemption_category_group_id) 
);
 
create unique index redemption_categories_uid_idx on dbo.redemption_categories (redemption_category_uid);
create unique index redemption_categories_code_idx on dbo.redemption_categories (redemption_category_code);
 
truncate table dbo.redemption_categories restart identity;
 

create table dbo.descriptor_categories
(
	descriptor_category_id int generated always as identity primary key,
  descriptor_category_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  descriptor_category_code varchar(50) not null,
  descriptor_category_name varchar(100) not null 
);
 
create unique index descriptor_categories_uid_idx on dbo.descriptor_categories (descriptor_category_uid);
create unique index descriptor_categories_code_idx on dbo.descriptor_categories (descriptor_category_code);
 
truncate table dbo.descriptor_categories restart identity;
 

create table dbo.operators
(
	operator_id int generated always as identity primary key,
  operator_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  first_name varchar(50) not null,
  last_name varchar(50) not null,
  pin int null,
  id varchar(50) not null,
  card_swipe_id varchar(50) not null,
  network_username varchar(50) not null,
  is_active bit not null 
);
 
create unique index operators_operator_uid_idx on dbo.operators (operator_uid);
create index operators_pin_idx on dbo.operators (pin);
create index operators_id_idx on dbo.operators (id);
create index operators_network_username_idx on dbo.operators (network_username);

truncate table dbo.operators restart identity;
  

create table dbo.external_systems
(
	external_system_id int generated always as identity primary key,
  external_system_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  external_system_code varchar(50) not null,
  external_system_name varchar(100) not null,
  data JSONB null
);
 
create unique index external_systems_uid_idx on dbo.external_systems (external_system_uid);
create unique index external_systems_code_idx on dbo.external_systems (external_system_code);
 
truncate table dbo.external_systems restart identity;
 

create table dbo.sales_sources
(
	sales_source_id int generated always as identity primary key,
  sales_source_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  sales_source_code varchar(50) not null,
  sales_source_name varchar(100) not null 
);
 
create unique index sales_sources_uid_idx on dbo.sales_sources (sales_source_uid);
create unique index sales_sources_code_idx on dbo.sales_sources (sales_source_code);
 
truncate table dbo.sales_sources restart identity;
 
 
create table dbo.products
(
	product_id bigint generated always as identity primary key,
  product_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  product_code varchar(50) not null,
  product_name varchar(100) not null,
  external_product_id varchar(50) null,
  season_id int not null,
  product_type_id int not null,
  pass_type_id int not null,
	
  foreign key (product_type_id) references dbo.product_types(product_type_id),
  foreign key (season_id) references dbo.seasons(season_id),
  foreign key (pass_type_id) references dbo.pass_types(pass_type_id)
);
 
create unique index products_uid_idx on dbo.products (product_uid);
create unique index products_product_code_idx on dbo.products (product_code);
create index products_season_id_idx on dbo.products (season_id);
 
truncate table dbo.products restart identity;
 

create table dbo.product_groups
(
	product_group_id int generated always as identity primary key,
  product_group_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  product_group_code varchar(50) not null,
  product_group_name varchar(100) not null 
);
 
create unique index product_groups_uid_idx on dbo.product_groups (product_group_uid);
create unique index product_groups_code_idx on dbo.product_groups (product_group_code);
 
truncate table dbo.product_groups restart identity;


create table dbo.product_group_mappings
(
	product_group_mapping_id bigint generated always as identity primary key,
  product_group_mapping_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  product_group_id int not null,
  product_id bigint not null,
  
  foreign key (product_group_id) references dbo.product_groups(product_group_id), 
	foreign key (product_id) references dbo.products(product_id) 
);
 
create unique index product_group_mappings_uid_idx on dbo.product_group_mappings (product_group_mapping_uid);
create index product_group_mappings_group_id_idx on dbo.product_group_mappings (product_group_id);
create index product_group_mappings_product_id_idx on dbo.product_group_mappings (product_id);
 
truncate table dbo.product_group_mappings restart identity;
 

create table dbo.product_variants
(
	product_variant_id bigint generated always as identity primary key,
  product_variant_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  product_variant_code varchar(50) not null,
  product_variant_name varchar(100) not null,
  external_product_variant_id varchar(50) null,
  site_id int not null,
 
  foreign key (site_id) references dbo.sites(site_id) 
);
 
create unique index product_variants_uid_idx on dbo.product_variants (product_variant_uid);
create unique index product_variants_code_idx on dbo.product_variants (product_variant_code);
create index product_variants_site_id_idx on dbo.product_variants (site_id);
  
truncate table dbo.product_variants restart identity;
 

create table dbo.product_variant_tiers
(
	product_variant_tier_id bigint generated always as identity primary key,
  product_variant_tier_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  product_variant_tier_code varchar(50) not null,
  product_variant_tier_name varchar(100) not null,
  product_variant_id bigint not null,
   
  foreign key (product_variant_id) references dbo.product_variants(product_variant_id) 
);
 
create unique index product_variant_tiers_uid_idx on dbo.product_variant_tiers (product_variant_tier_uid);
create index product_variant_tiers_variant_id_idx on dbo.product_variant_tiers (product_variant_id);
  
truncate table dbo.product_variant_tiers restart identity;
  
 
create table dbo.product_variant_details
(
	product_variant_detail_id bigint generated always as identity primary key,
  product_variant_detail_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  product_variant_tier_id bigint not null,
  product_id bigint not null,
  price_value numeric(15,2) null,
   
  foreign key (product_variant_tier_id) references dbo.product_variant_tiers(product_variant_tier_id),
  foreign key (product_id) references dbo.products(product_id)
);
 
create unique index product_variant_details_uid_idx on dbo.product_variant_details (product_variant_detail_uid);
create index product_variant_details_product_variant_tier_id_idx on dbo.product_variant_details (product_variant_tier_id);
create index product_variant_details_product_id_idx on dbo.product_variant_details (product_id);
  
truncate table dbo.product_variant_details restart identity;
  
	
create table dbo.product_variant_venues
(
	product_variant_venue_id bigint generated always as identity primary key,
  product_variant_venue_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  product_variant_detail_id bigint not null,
  venue_id int not null,
  redemption_product_id bigint null,
  subredemption_product_id bigint null,
  redemption_category_id int null,
  descriptor_category_id int null,
  usage_type_id int null,
  usage_type_data text null,
  calendar_id int null,
  start_date date null,
  end_date date null,
  start_time timestamp null,
  end_time timestamp null,
  dow_validity int null,
  reentry_allowed bit not null,
  reentry_interval int null,
  reentry_max_count int null,
   
  foreign key (product_variant_detail_id) references dbo.product_variant_details(product_variant_detail_id),
  foreign key (venue_id) references dbo.venues(venue_id),
  foreign key (redemption_product_id) references dbo.products(product_id),
  foreign key (subredemption_product_id) references dbo.products(product_id),
  foreign key (redemption_category_id) references dbo.redemption_categories(redemption_category_id),
  foreign key (descriptor_category_id) references dbo.descriptor_categories(descriptor_category_id),
  foreign key (usage_type_id) references dbo.usage_types(usage_type_id),
  foreign key (calendar_id) references dbo.calendars(calendar_id) 
);
 
create unique index product_variant_venues_uid_idx on dbo.product_variant_venues (product_variant_venue_uid);
create index product_variant_venues_detail_id_idx on dbo.product_variant_venues (product_variant_detail_id);
create index product_variant_venues_venue_id_idx on dbo.product_variant_venues (venue_id);
  
truncate table dbo.product_variant_venues restart identity;
 

create table dbo.product_variant_locations
(
	product_variant_location_id bigint generated always as identity primary key,
  product_variant_location_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  product_variant_venue_id bigint not null,
  location_id int not null,
  usage_type_id int null,
  usage_type_data jsonb null,
  calendar_id int null,
  start_date date null,
  end_date date null,
  start_time timestamp null,
  end_time timestamp null,
  dow_validity int null,
  reentry_allowed bit not null,
  reentry_interval int null,
  reentry_max_count int null,
   
  foreign key (product_variant_venue_id) references dbo.product_variant_venues(product_variant_venue_id),
  foreign key (location_id) references dbo.locations(location_id),
  foreign key (usage_type_id) references dbo.usage_types(usage_type_id),
  foreign key (calendar_id) references dbo.calendars(calendar_id) 
);
 
create unique index product_variant_locations_uid_idx on dbo.product_variant_locations (product_variant_location_uid);
create index product_variant_locations_venue_id_idx on dbo.product_variant_locations (product_variant_venue_id);
create index product_variant_locations_location_id_idx on dbo.product_variant_locations (location_id);
  
truncate table dbo.product_variant_locations restart identity;
 

create table dbo.tickets
(
	ticket_id bigint generated always as identity primary key,
  ticket_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  created_at_site_id int not null,
  external_guest_id varchar(50) null,
  guest_external_system_id int null,
   
  foreign key (created_at_site_id) references dbo.sites(site_id),
  foreign key (guest_external_system_id) references dbo.external_systems(external_system_id)
);
 
create unique index tickets_ticket_uid_idx on dbo.tickets (ticket_uid);
create index tickets_created_at_site_id_idx on dbo.tickets (created_at_site_id);

truncate table dbo.tickets restart identity;
   

create table dbo.transactions
(
	transaction_id bigint generated always as identity primary key,
  transaction_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
	start_date_time timestamp null,
  end_date_time timestamp null, 
  site_id int not null,
  venue_id int not null,
  location_id int not null,
  terminal_id bigint not null,
  season_id int not null,
  business_date_id bigint not null,
  event_id int not null,
  operator_id int not null,
 
  foreign key (site_id) references dbo.sites(site_id),
	foreign key (venue_id) references dbo.venues(venue_id),
	foreign key (location_id) references dbo.locations(location_id),
	foreign key (terminal_id) references dbo.terminals(terminal_id),
	foreign key (season_id) references dbo.seasons(season_id),
  foreign key (business_date_id) references dbo.business_dates(business_date_id),
  foreign key (event_id) references dbo.events(event_id),
  foreign key (operator_id) references dbo.operators(operator_id)  
);
 
create unique index transactions_uid_idx on dbo.transactions (transaction_uid);
create index transactions_site_id_idx on dbo.transactions (site_id);
create index transactions_venue_id_idx on dbo.transactions (venue_id);
 
truncate table dbo.transactions restart identity;
  
 
create table dbo.ticket_barcodes
(
	ticket_barcode_id bigint generated always as identity primary key,
  ticket_barcode_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  barcode varchar(100) not null,
  ticket_id bigint not null,
  is_primary bit not null,
  is_active bit not null,
 
  foreign key (ticket_id) references dbo.tickets(ticket_id) 
);
 
create unique index ticket_barcodes_ticket_barcode_uid_idx on dbo.ticket_barcodes (ticket_barcode_uid);
create index ticket_barcodes_barcode_idx on dbo.ticket_barcodes (barcode);
create index ticket_barcodes_ticket_id_idx on dbo.ticket_barcodes (ticket_id);

truncate table dbo.ticket_barcodes restart identity;
    

create table dbo.orders
(
	order_id bigint generated always as identity primary key,
  order_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
	order_code varchar(50) not null,
  order_name varchar(100) not null,
	site_id int not null,
	terminal_id bigint not null,
	operator_id int not null,
	external_customer_id varchar(50) null,
  customer_external_system_id int null, 
  external_order_id varchar(50) null,
  order_external_system_id int null, 
  sales_source_id int not null,
  business_date_id bigint not null,
  season_id int not null,
  transaction_id bigint not null,
	amount numeric(15,2) not null,
  payment_method_id int not null,
  currency_id int not null,
 
  foreign key (site_id) references dbo.sites(site_id),
	foreign key (terminal_id) references dbo.terminals(terminal_id),
	foreign key (operator_id) references dbo.operators(operator_id),
	foreign key (customer_external_system_id) references dbo.external_systems(external_system_id),
	foreign key (sales_source_id) references dbo.sales_sources(sales_source_id),
	foreign key (business_date_id) references dbo.business_dates(business_date_id),
	foreign key (season_id) references dbo.seasons(season_id) ,
	foreign key (transaction_id) references dbo.transactions(transaction_id) ,
	foreign key (payment_method_id) references dbo.payment_methods(payment_method_id),
	foreign key (currency_id) references dbo.currencies(currency_id) 
);
 
create unique index orders_uid_idx on dbo.orders (order_uid);
create unique index orders_order_code_idx on dbo.orders (order_code);
create index orders_site_id_idx on dbo.orders (site_id);
create index orders_terminal_id_idx on dbo.orders (terminal_id);
create index orders_operator_id_idx on dbo.orders (operator_id);
create index orders_transaction_id_idx on dbo.orders (transaction_id);
 
truncate table dbo.orders restart identity;
    
 
create table dbo.ticket_details
(
	ticket_detail_id bigint generated always as identity primary key,
  ticket_detail_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  site_id int not null,
  ticket_id bigint not null,
	product_id bigint not null,
  product_variant_id bigint not null,
  order_id bigint not null,
  transaction_id bigint not null,
  season_id int not null,
  value numeric(15,2) not null,
 
  foreign key (site_id) references dbo.sites(site_id),
  foreign key (ticket_id) references dbo.tickets(ticket_id),
  foreign key (product_id) references dbo.products(product_id),
  foreign key (product_variant_id) references dbo.product_variants(product_variant_id),
  foreign key (order_id) references dbo.orders(order_id),
  foreign key (transaction_id) references dbo.transactions(transaction_id),
  foreign key (season_id) references dbo.seasons(season_id)    
);
 
create unique index ticket_details_uid_idx on dbo.ticket_details (ticket_detail_uid);
create index ticket_details_site_id_idx on dbo.ticket_details (site_id);
create index ticket_details_product_id_idx on dbo.ticket_details (product_id);
create index ticket_details_order_id_idx on dbo.ticket_details (order_id);

truncate table dbo.ticket_details restart identity;
  
 
create table dbo.transaction_step_sales
(
	transaction_step_sale_id bigint generated always as identity primary key,
  transaction_step_sale_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  transaction_id bigint not null,
	step_index int not null,
	step_date_time timestamp null,
	price numeric(15,2) not null,
	original_price numeric(15,2) not null,
	is_price_override bit not null,
	price_override_reason_code_id int not null,
	price_override_operator_id int not null,
	product_id bigint not null,
	product_variant_id bigint not null,
	bundle_id bigint not null,
	season_id int not null,
	ticket_id bigint not null,
	ticket_barcode_id bigint not null,
	barcode varchar(100) not null,
	ticket_detail_id bigint not null,
 
  foreign key (transaction_id) references dbo.transactions(transaction_id),
	foreign key (price_override_reason_code_id) references dbo.reason_codes(reason_code_id),
	foreign key (price_override_operator_id) references dbo.operators(operator_id),
	foreign key (product_id) references dbo.products(product_id) ,
	foreign key (product_variant_id) references dbo.product_variants(product_variant_id),
	foreign key (season_id) references dbo.seasons(season_id),
	foreign key (ticket_id) references dbo.tickets(ticket_id),
	foreign key (ticket_barcode_id) references dbo.ticket_barcodes(ticket_barcode_id),
	foreign key (ticket_detail_id) references dbo.ticket_details(ticket_detail_id) 
);
 
create unique index transaction_step_sale_uid_idx on dbo.transaction_step_sales (transaction_step_sale_uid);
create index transaction_step_sale_transaction_id_idx on dbo.transaction_step_sales (transaction_id);
create index transaction_step_sale_product_id_idx on dbo.transaction_step_sales (product_id);
create index transaction_step_sale_product_variant_id_idx on dbo.transaction_step_sales (product_variant_id);
create index transaction_step_sale_ticket_id_idx on dbo.transaction_step_sales (ticket_id);
create index transaction_step_sale_ticket_barcode_id_idx on dbo.transaction_step_sales (ticket_barcode_id);
create index transaction_step_sale_barcode_idx on dbo.transaction_step_sales (barcode);
 
truncate table dbo.transaction_step_sales restart identity;
  
 
create table dbo.ticket_venues
(
	ticket_venue_id bigint generated always as identity primary key,
  ticket_venue_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  ticket_detail_id bigint not null,
  venue_id int not null,
  ticket_status_id int not null,
  usage_type_id int not null,
  usage_type_data jsonb null,
  calendar_id int not null,
  start_date date null,
  end_date date null,
  start_time timestamp null,
  end_time timestamp null,
  dow_validity int null,
  reentry_allowed bit not null,
  reentry_interval int null,
  reentry_max_count int null,
 
  foreign key (ticket_detail_id) references dbo.ticket_details(ticket_detail_id),
  foreign key (venue_id) references dbo.venues(venue_id),
  foreign key (ticket_status_id) references dbo.ticket_statuses(ticket_status_id),
  foreign key (usage_type_id) references dbo.usage_types(usage_type_id),
  foreign key (calendar_id) references dbo.calendars(calendar_id) 
);
 
create unique index ticket_venues_ticket_venue_uid_idx on dbo.ticket_venues (ticket_venue_uid);
create index ticket_venues_ticket_detail_id_idx on dbo.ticket_venues (ticket_detail_id);
create index ticket_venues_venue_id_idx on dbo.ticket_venues (venue_id);
 
truncate table dbo.ticket_venues restart identity;
 

create table dbo.ticket_locations
(
	ticket_location_id bigint generated always as identity primary key,
  ticket_location_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  ticket_venue_id bigint not null,
  location_id int not null,
  ticket_status_id int not null,
  usage_type_id int not null,
  usage_type_data jsonb null,
  calendar_id int not null,
  start_date date null,
  end_date date null,
  start_time timestamp null,
  end_time timestamp null,
  dow_validity int null,
  reentry_allowed bit not null,
  reentry_interval int null,
  reentry_max_count int null,
 
  foreign key (ticket_venue_id) references dbo.ticket_venues(ticket_venue_id),
  foreign key (location_id) references dbo.locations(location_id),
  foreign key (ticket_status_id) references dbo.ticket_statuses(ticket_status_id),
  foreign key (usage_type_id) references dbo.usage_types(usage_type_id),
  foreign key (calendar_id) references dbo.calendars(calendar_id)  
);
 
create unique index ticket_locations_ticket_location_uid_idx on dbo.ticket_locations (ticket_location_uid);
create index ticket_locations_ticket_venue_id_idx on dbo.ticket_locations (ticket_venue_id);
create index ticket_locations_location_id_idx on dbo.ticket_locations (location_id);
 
truncate table dbo.ticket_locations restart identity;
  

create table dbo.transaction_step_redemptions
(
	transaction_step_redemption_id bigint generated always as identity primary key,
  transaction_step_redemption_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  transaction_id bigint not null,
	step_index int not null,
	step_date_time timestamp null,
	ticket_id bigint not null,
	ticket_barcode_id bigint not null,
	barcode varchar(100) not null,
	ticket_detail_id bigint not null ,
	ticket_venue_id bigint not null,
	ticket_location_id bigint not null,
	product_id bigint not null,
	sales_product_id bigint not null,
	redemption_category_id int not null,
	is_scanned bit not null,
	is_accepted bit not null,
	is_reentry bit not null,
	failure_code_id int not null,
	before_ticket_status_id int not null,
	after_ticket_status_id int not null,
	ticket_detail_value numeric(15,2) not null,
 
  foreign key (transaction_id) references dbo.transactions(transaction_id),
	foreign key (ticket_id) references dbo.tickets(ticket_id),
	foreign key (ticket_barcode_id) references dbo.ticket_barcodes(ticket_barcode_id),
	foreign key (ticket_detail_id) references dbo.ticket_details(ticket_detail_id),
	foreign key (ticket_venue_id) references dbo.ticket_venues(ticket_venue_id),
	foreign key (ticket_location_id) references dbo.ticket_locations(ticket_location_id),
	foreign key (product_id) references dbo.products(product_id) ,
	foreign key (sales_product_id) references dbo.products(product_id) ,
	foreign key (redemption_category_id) references dbo.redemption_categories(redemption_category_id),
	foreign key (failure_code_id) references dbo.failure_codes(failure_code_id),
	foreign key (before_ticket_status_id) references dbo.ticket_statuses(ticket_status_id),
	foreign key (after_ticket_status_id) references dbo.ticket_statuses(ticket_status_id)
);
 
create unique index transaction_step_redemptions_uid_idx on dbo.transaction_step_redemptions (transaction_step_redemption_uid);
create index transaction_step_redemptions_transaction_id_idx on dbo.transaction_step_redemptions (transaction_id);
create index transaction_step_redemptions_ticket_id_idx on dbo.transaction_step_redemptions (ticket_id);
create index transaction_step_redemptions_ticket_barcode_id_idx on dbo.transaction_step_redemptions (ticket_barcode_id);
create index transaction_step_redemptions_barcode_idx on dbo.transaction_step_redemptions (barcode);
create index transaction_step_redemptions_ticket_detail_id_idx on dbo.transaction_step_redemptions (ticket_detail_id);
create index transaction_step_redemptions_ticket_venue_id_idx on dbo.transaction_step_redemptions (ticket_venue_id);
create index transaction_step_redemptions_product_id_idx on dbo.transaction_step_redemptions (product_id);
create index transaction_step_redemptions_sales_product_id_idx on dbo.transaction_step_redemptions (sales_product_id);
  
truncate table dbo.transaction_step_redemptions restart identity;
 
 
create table dbo.ticket_usages
(
	ticket_usage_id bigint generated always as identity primary key,
  ticket_usage_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  usage_date_time timestamp not null,
  site_id int not null,
  ticket_barcode_id bigint not null,
  ticket_id bigint not null,
  ticket_detail_id bigint not null,
  ticket_venue_id bigint not null,
  ticket_location_id bigint not null,
  product_id bigint not null,
  product_variant_id bigint not null,
  business_date_id bigint not null,
  event_id int not null,
  transaction_id bigint not null,
  transaction_step_redemption_id bigint not null,
 
  foreign key (site_id) references dbo.sites(site_id),
	foreign key (ticket_barcode_id) references dbo.ticket_barcodes(ticket_barcode_id),
	foreign key (ticket_id) references dbo.tickets(ticket_id),
	foreign key (ticket_detail_id) references dbo.ticket_details(ticket_detail_id),
	foreign key (ticket_venue_id) references dbo.ticket_venues(ticket_venue_id),
  foreign key (ticket_location_id) references dbo.ticket_locations(ticket_location_id),
  foreign key (product_id) references dbo.products(product_id),
  foreign key (product_variant_id) references dbo.product_variants(product_variant_id),
  foreign key (business_date_id) references dbo.business_dates(business_date_id),
  foreign key (event_id) references dbo.events(event_id),
  foreign key (transaction_id) references dbo.transactions(transaction_id),
  foreign key (transaction_step_redemption_id) references dbo.transaction_step_redemptions(transaction_step_redemption_id) 
);
 
create unique index ticket_usages_ticket_usage_uid_idx on dbo.ticket_usages (ticket_usage_uid);
create index ticket_usages_site_id_idx on dbo.ticket_usages (site_id);
create index ticket_usages_ticket_id_idx on dbo.ticket_usages (ticket_id);
 
truncate table dbo.ticket_usages restart identity;
  

create table dbo.ticket_status_attributes
(
	ticket_status_attribute_id bigint generated always as identity primary key,
  ticket_status_attribute_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
  ticket_status_id int not null,
  ticket_status_code varchar(50) not null,
  is_valid bit not null,
  data jsonb null,
  
  foreign key (ticket_status_id) references dbo.ticket_statuses(ticket_status_id) 
);
 
create unique index ticket_status_attributes_ticket_status_attribute_uid_idx on dbo.ticket_status_attributes (ticket_status_attribute_uid);
create unique index ticket_status_attributes_ticket_status_code_idx on dbo.ticket_status_attributes (ticket_status_code);
 
truncate table dbo.ticket_status_attributes restart identity;
  
   
create table dbo.order_details
(
	order_detail_id bigint generated always as identity primary key,
  order_detail_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
	order_detail_code varchar(50) not null,
  order_detail_name varchar(100) not null,
	order_id bigint not null,
	order_detail_index int not null,
	external_order_detail_id varchar(50) null,
  product_id bigint null, 
  product_variant_id bigint not null, 
  product_bundle_id bigint not null,
  season_id int not null,
	price numeric(15,2) not null,
 
  foreign key (order_id) references dbo.orders(order_id),
	foreign key (product_id) references dbo.products(product_id),
	foreign key (product_variant_id) references dbo.product_variants(product_variant_id),
	foreign key (season_id) references dbo.seasons(season_id) 
);
 
create unique index order_details_uid_idx on dbo.order_details (order_detail_uid);
create unique index order_details_order_detail_code_idx on dbo.order_details (order_detail_code);
create index order_details_order_id_idx on dbo.order_details (order_id);
create index order_details_product_id_idx on dbo.order_details (product_id);
create index order_details_product_variant_id_idx on dbo.order_details (product_variant_id);
   
truncate table dbo.order_details restart identity;
 

create table dbo.transaction_step_activities
(
	transaction_step_activity_id bigint generated always as identity primary key,
  transaction_step_activity_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  transaction_id bigint not null,
	step_index int not null,
	step_date_time timestamp null,
	transaction_activity_type_id int not null,
	ticket_id bigint not null,
	ticket_detail_id bigint not null,
	ticket_venue_id bigint not null,
	ticket_location_id bigint not null,
	order_id bigint not null,
	order_detail_id bigint not null,
	comments text null,
	data jsonb null,
 
  foreign key (transaction_id) references dbo.transactions(transaction_id),
	foreign key (transaction_activity_type_id) references dbo.transaction_activity_types(transaction_activity_type_id),
	foreign key (ticket_id) references dbo.tickets(ticket_id),
	foreign key (ticket_detail_id) references dbo.ticket_details(ticket_detail_id),
	foreign key (ticket_venue_id) references dbo.ticket_venues(ticket_venue_id),
  foreign key (ticket_location_id) references dbo.ticket_locations(ticket_location_id),
  foreign key (order_id) references dbo.orders(order_id),
  foreign key (order_detail_id) references dbo.order_details(order_detail_id)  
);
 
create unique index transaction_step_activities_uid_idx on dbo.transaction_step_activities (transaction_step_activity_uid);
create index transaction_step_activities_transaction_id_idx on dbo.transaction_step_activities (transaction_id);
create index transaction_step_activities_transaction_activity_type_id_idx on dbo.transaction_step_activities (transaction_activity_type_id);
create index transaction_step_activities_ticket_id_idx on dbo.transaction_step_activities (ticket_id);
create index transaction_step_activities_ticket_detail_id_idx on dbo.transaction_step_activities (ticket_detail_id);
create index transaction_step_activities_ticket_venue_id_idx on dbo.transaction_step_activities (ticket_venue_id);
create index transaction_step_activities_ticket_location_id_idx on dbo.transaction_step_activities (ticket_location_id);
create index transaction_step_activities_order_id_idx on dbo.transaction_step_activities (order_id);
create index transaction_step_activities_order_detail_id_idx on dbo.transaction_step_activities (order_detail_id);
 
truncate table dbo.transaction_step_activities restart identity;
 

create table dbo.transaction_step_payments
(
	transaction_step_payment_id bigint generated always as identity primary key,
  transaction_step_payment_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  transaction_id bigint not null,
	step_index int not null,
	step_date_time timestamp null,
	amount numeric(15,2) not null,
	payment_method_id int not null,
	currency_id int not null,
 
  foreign key (transaction_id) references dbo.transactions(transaction_id),
	foreign key (payment_method_id) references dbo.payment_methods(payment_method_id),
	foreign key (currency_id) references dbo.currencies(currency_id) 
);
 
create unique index transaction_step_payments_uid_idx on dbo.transaction_step_payments (transaction_step_payment_uid);
create index transaction_step_payments_transaction_id_idx on dbo.transaction_step_payments (transaction_id);
 
truncate table dbo.transaction_step_payments restart identity;
  

create table dbo.transaction_step_traffic_counts
(
	transaction_step_traffic_count_id bigint generated always as identity primary key,
  transaction_step_traffic_count_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  transaction_id bigint not null,
	step_index int not null,
	step_date_time timestamp null,
	entry_count int not null,
	exit_count int not null,
	is_manual_adjustment bit not null,
 
  foreign key (transaction_id) references dbo.transactions(transaction_id) 
);
 
create unique index transaction_step_traffic_counts_uid_idx on dbo.transaction_step_traffic_counts (transaction_step_traffic_count_uid);
create index transaction_step_traffic_counts_transaction_id_idx on dbo.transaction_step_traffic_counts (transaction_id);
  
truncate table dbo.transaction_step_traffic_counts restart identity;
 

create table dbo.order_payments
(
	order_payment_id bigint generated always as identity primary key,
  order_payment_uid UUID not null default uuid_generate_v4(),
	create_date_time timestamp not null default timezone('utc', now()),
  update_date_time timestamp null,
	order_id bigint not null,
  transaction_id bigint not null, 
  transaction_step_payment_id bigint not null,
	amount numeric(15,2) not null , 
  display_account_number int not null,
 
  foreign key (order_id) references dbo.orders(order_id),
	foreign key (transaction_id) references dbo.transactions(transaction_id),
	foreign key (transaction_step_payment_id) references dbo.transaction_step_payments(transaction_step_payment_id) 
);
 
create unique index order_payments_uid_idx on dbo.order_payments (order_payment_uid);
create index order_payments_order_id_idx on dbo.order_payments (order_id);
create index order_payments_transaction_id_idx on dbo.order_payments (transaction_id);
  
truncate table dbo.order_payments restart identity;
   

insert into dbo.validity_types(validity_type_id, validity_type_name)
VALUES
	(1, 'Single Use'),
	(2, 'Unlimited Use'),
	(3, 'Multi Day'),
	(4, 'Never'),
	(5, 'Max Total Usage');
   
	 
insert into dbo.site_systems(site_system_code, site_system_name)
VALUES
	('GC', 'GATE CENTRAL'),
	('SFTS', 'SIX FLAGS');
  
	
insert into dbo.sites(site_code, site_name, internal_system_site_id, internal_system_site_code, site_system_id)
VALUES
	('SFOT', 'Six Flags Over Texas', 1, '01', 2),
	('SFOG', 'Six Flags Over Georgia', 2, '02', 2),
	('SFSL', 'Six Flags St. Louis', 3, '03', 2),
	('SFGA', 'Six Flags Great Adventure', 4, '05', 2),
	('SFMM', 'Six Flags Magic Mountain', 5, '06', 2),
	('SFAM', 'Six Flags America', 6, '09', 2),
	('SFGR', 'Six Flags Great America', 7, '10', 2),
	('SFHHLA', 'Six Flags Hurricane Harbor, Los Angeles', 8, '11', 2),
	('SFHHA', 'Six Flags Hurricane Harbor, Arlington', 9, '13', 2),
	('SFFT', 'Six Flags Fiesta Texas', 10, '14', 2),
	('SFWS', 'Six Flags Wild Safari, Jackson', 11, '15', 2),
	('SFWWA', 'Six Flags White Water, Atlanta', 12, '22', 2),
	('SFGEL', 'Six Flags Great Escape Lodge & Waterpark', 13, '23', 2),
	('SFGE', 'The Great Escape', 14, '24', 2),
	('SFHHNJ', 'Six Flags Hurricane Harbor, Jackson', 15, '25', 2),
	('SFNE', 'Six Flags New England', 16, '35', 2),
	('SFDK', 'Six Flags Discovery Kingdom', 17, '36', 2),
	('SFDC', 'Six Flags Corporate Office, Arlington', 19, '51', 2),
	('SFMX', 'Six Flags México', 20, '60', 2),
	('SFMC', 'La Ronde, Montreal', 21, '69', 2),
	('SFHHCH', 'Six Flags Hurricane Harbor, Chicago', 22, '20', 2),
	('SFHHOX', 'Six Flags Hurricane Harbor, Oaxtepec', 23, '59', 2),
	('SFHHCO', 'Six Flags Hurricane Harbor, Concord', 24, '42', 2),
	('SFFC', 'Six Flags Frontier City', 25, '43', 2),
	('SFWWB', 'Six Flags Hurricane Harbor, Oklahoma City', 26, '44', 2),
	('SFDL', 'Six Flags Darien Lake', 27, '45', 2),
	('SFWWP', 'Six Flags Hurricane Harbor, Phoenix', 28, '46', 2),
	('SFWWST', 'Six Flags Over Six Flags Hurricane Harbor, SplashTown', 29, '47', 2),
	('SFMW', 'Six Flags Hurricane Harbor, Rockford', 30, '48', 2),
	 
	('CP', 'Cedar Point', 1, NULL, 1), 
	('KB', 'Knott''s Berry Farm', 4, NULL, 1), 
	('WF', 'Worlds of Fun', 6, NULL, 1), 
	('DP', 'Dorney Park', 8, NULL, 1), 
	('MA', 'Michigan''s Adventure', 12, NULL, 1), 
	('VF', 'Valleyfair', 14, NULL, 1), 
	('KI', 'Kings Island', 20, NULL, 1), 
	('KD', 'Kings Dominion', 25, NULL, 1), 
	('NB', 'Schlitterbahn NB', 26, NULL, 1), 
	('GV', 'Schlitterbahn GV', 27, NULL, 1), 
	('CA', 'Carowinds', 30, NULL, 1), 
	('GA', 'Great America', 35, NULL, 1), 
	('CW', 'Canada''s Wonderland', 40, NULL, 1), 
	('KSC', 'Knott''s Soak City', 201, NULL, 1), 
	('CPS', 'Cedar Point Shores', 202, NULL, 1), 
	('CPR', 'Cedar Point Castaway Bay', 203, NULL, 1);
	GRANT INSERT, UPDATE, SELECT, DELETE ON ALL TABLES IN SCHEMA dbo TO dev_iam_ticket;
        """

        query2 = """
            CREATE DATABASE trex;
        """

        cursor = db_connection.cursor(cursor_factory=RealDictCursor)
        db_connection.autocommit = True
        cursor.execute(query2)
        cursor.execute(query)
        db_connection.commit()
        status_code = 200

    except Exception as error:
        print("Error  creating revenue_codes table: " + str(error))
        traceback.print_exc()
        result = str(error)

    response = {
        "statusCode": status_code,
        'headers': cors_headers(),
        "body": json.dumps(result, indent=2, sort_keys=True, default=str)
    }

    return response
