--
-- PostgreSQL database cluster dump
--

\restrict dqRTowiGLAqLFg1Saihbci3coJ6n7uu8b8ccePfwdGl4RejvFnaaZOqTyCPObQE

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE postgres;
ALTER ROLE postgres WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:gPph8n8RKXV/okUY6LeCGw==$K4mCn9Y2bu35O3/xAwVE+g2GKANk0aOb81YiZPsa/xM=:GBk2ucaqKZfgrvFOxud140mUPRBiBbG73TyuHqBOma0=';

--
-- User Configurations
--








\unrestrict dqRTowiGLAqLFg1Saihbci3coJ6n7uu8b8ccePfwdGl4RejvFnaaZOqTyCPObQE

--
-- Databases
--

--
-- Database "template1" dump
--

\connect template1

--
-- PostgreSQL database dump
--

\restrict bMjVMKW5hOh3Od0V42KaoSEEmihXdNkylxJT7bozbZSUTlSrx2q5NYJWngeN5CM

-- Dumped from database version 15.19
-- Dumped by pg_dump version 15.19

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- PostgreSQL database dump complete
--

\unrestrict bMjVMKW5hOh3Od0V42KaoSEEmihXdNkylxJT7bozbZSUTlSrx2q5NYJWngeN5CM

--
-- Database "aether_catalog" dump
--

--
-- PostgreSQL database dump
--

\restrict 5b1VA1buUbkX8XgRss6D0Ld57nUYOXLCsFW5wBGAyqNdABqv2iBbWiGDXd3H9a8

-- Dumped from database version 15.19
-- Dumped by pg_dump version 15.19

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: aether_catalog; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE aether_catalog WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';


ALTER DATABASE aether_catalog OWNER TO postgres;

\unrestrict 5b1VA1buUbkX8XgRss6D0Ld57nUYOXLCsFW5wBGAyqNdABqv2iBbWiGDXd3H9a8
\connect aether_catalog
\restrict 5b1VA1buUbkX8XgRss6D0Ld57nUYOXLCsFW5wBGAyqNdABqv2iBbWiGDXd3H9a8

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: admin_security; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA admin_security;


ALTER SCHEMA admin_security OWNER TO postgres;

--
-- Name: architecture; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA architecture;


ALTER SCHEMA architecture OWNER TO postgres;

--
-- Name: iac; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA iac;


ALTER SCHEMA iac OWNER TO postgres;

--
-- Name: project_manager; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA project_manager;


ALTER SCHEMA project_manager OWNER TO postgres;

--
-- Name: region_ca_central_1; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA region_ca_central_1;


ALTER SCHEMA region_ca_central_1 OWNER TO postgres;

--
-- Name: region_ca_west_1; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA region_ca_west_1;


ALTER SCHEMA region_ca_west_1 OWNER TO postgres;

--
-- Name: region_mx_central_1; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA region_mx_central_1;


ALTER SCHEMA region_mx_central_1 OWNER TO postgres;

--
-- Name: region_sa_east_1; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA region_sa_east_1;


ALTER SCHEMA region_sa_east_1 OWNER TO postgres;

--
-- Name: region_us_east_1; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA region_us_east_1;


ALTER SCHEMA region_us_east_1 OWNER TO postgres;

--
-- Name: region_us_east_2; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA region_us_east_2;


ALTER SCHEMA region_us_east_2 OWNER TO postgres;

--
-- Name: region_us_gov_east_1; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA region_us_gov_east_1;


ALTER SCHEMA region_us_gov_east_1 OWNER TO postgres;

--
-- Name: region_us_gov_west_1; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA region_us_gov_west_1;


ALTER SCHEMA region_us_gov_west_1 OWNER TO postgres;

--
-- Name: region_us_west_1; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA region_us_west_1;


ALTER SCHEMA region_us_west_1 OWNER TO postgres;

--
-- Name: region_us_west_2; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA region_us_west_2;


ALTER SCHEMA region_us_west_2 OWNER TO postgres;

--
-- Name: source_connection; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA source_connection;


ALTER SCHEMA source_connection OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admin_audit_logs; Type: TABLE; Schema: admin_security; Owner: postgres
--

CREATE TABLE admin_security.admin_audit_logs (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    action character varying(64) NOT NULL,
    target_resource character varying(120),
    status character varying(32) NOT NULL,
    ip_address character varying(64),
    details character varying(500),
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE admin_security.admin_audit_logs OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE; Schema: admin_security; Owner: postgres
--

CREATE SEQUENCE admin_security.admin_audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE admin_security.admin_audit_logs_id_seq OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: admin_security; Owner: postgres
--

ALTER SEQUENCE admin_security.admin_audit_logs_id_seq OWNED BY admin_security.admin_audit_logs.id;


--
-- Name: admin_users; Type: TABLE; Schema: admin_security; Owner: postgres
--

CREATE TABLE admin_security.admin_users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(32) NOT NULL,
    is_active boolean NOT NULL,
    failed_attempts integer NOT NULL,
    locked_until timestamp without time zone,
    last_login_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE admin_security.admin_users OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE; Schema: admin_security; Owner: postgres
--

CREATE SEQUENCE admin_security.admin_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE admin_security.admin_users_id_seq OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE OWNED BY; Schema: admin_security; Owner: postgres
--

ALTER SEQUENCE admin_security.admin_users_id_seq OWNED BY admin_security.admin_users.id;


--
-- Name: ec2_catalog; Type: TABLE; Schema: admin_security; Owner: postgres
--

CREATE TABLE admin_security.ec2_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    network_performance character varying(100) NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE admin_security.ec2_catalog OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE; Schema: admin_security; Owner: postgres
--

CREATE SEQUENCE admin_security.ec2_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE admin_security.ec2_catalog_id_seq OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: admin_security; Owner: postgres
--

ALTER SEQUENCE admin_security.ec2_catalog_id_seq OWNED BY admin_security.ec2_catalog.id;


--
-- Name: generic_service_catalog; Type: TABLE; Schema: admin_security; Owner: postgres
--

CREATE TABLE admin_security.generic_service_catalog (
    id integer NOT NULL,
    service character varying(50) NOT NULL,
    instance_type character varying(100) NOT NULL,
    vcpus integer,
    ram_gb double precision,
    price_per_hour double precision NOT NULL,
    unit character varying(50),
    category character varying(50) NOT NULL,
    region character varying(50),
    details character varying(500)
);


ALTER TABLE admin_security.generic_service_catalog OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE; Schema: admin_security; Owner: postgres
--

CREATE SEQUENCE admin_security.generic_service_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE admin_security.generic_service_catalog_id_seq OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: admin_security; Owner: postgres
--

ALTER SEQUENCE admin_security.generic_service_catalog_id_seq OWNED BY admin_security.generic_service_catalog.id;


--
-- Name: rds_catalog; Type: TABLE; Schema: admin_security; Owner: postgres
--

CREATE TABLE admin_security.rds_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE admin_security.rds_catalog OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE; Schema: admin_security; Owner: postgres
--

CREATE SEQUENCE admin_security.rds_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE admin_security.rds_catalog_id_seq OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: admin_security; Owner: postgres
--

ALTER SEQUENCE admin_security.rds_catalog_id_seq OWNED BY admin_security.rds_catalog.id;


--
-- Name: requirement_projects; Type: TABLE; Schema: admin_security; Owner: postgres
--

CREATE TABLE admin_security.requirement_projects (
    id character varying(36) NOT NULL,
    project_name character varying(100) NOT NULL,
    description character varying(500),
    stream character varying(50) NOT NULL,
    target_region character varying(50) NOT NULL,
    traffic_scale character varying(50) NOT NULL,
    reliability character varying(50) NOT NULL,
    security_need character varying(50) NOT NULL,
    data_storage_gb double precision NOT NULL,
    monthly_budget double precision,
    tech_stack text,
    operations text,
    monitoring text,
    architecture_tier character varying(50) NOT NULL,
    estimated_monthly_cost double precision NOT NULL,
    cost_breakdown text,
    service_rationales text,
    cost_optimizations text,
    profile_output text,
    status character varying(30) NOT NULL,
    dispatched_to_m2 boolean,
    m2_graph_summary text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE admin_security.requirement_projects OWNER TO postgres;

--
-- Name: sync_metadata; Type: TABLE; Schema: admin_security; Owner: postgres
--

CREATE TABLE admin_security.sync_metadata (
    id integer NOT NULL,
    region_code character varying(50) NOT NULL,
    last_sync_timestamp timestamp without time zone NOT NULL,
    status character varying(20) NOT NULL,
    records_synced integer NOT NULL,
    ec2_count integer NOT NULL,
    rds_count integer NOT NULL,
    generic_count integer NOT NULL,
    duration_ms integer NOT NULL,
    error_message character varying(500)
);


ALTER TABLE admin_security.sync_metadata OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE; Schema: admin_security; Owner: postgres
--

CREATE SEQUENCE admin_security.sync_metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE admin_security.sync_metadata_id_seq OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: admin_security; Owner: postgres
--

ALTER SEQUENCE admin_security.sync_metadata_id_seq OWNED BY admin_security.sync_metadata.id;


--
-- Name: architecture_versions; Type: TABLE; Schema: architecture; Owner: postgres
--

CREATE TABLE architecture.architecture_versions (
    version_id character varying(100) NOT NULL,
    project_id character varying(100),
    environment_id character varying(100),
    environment_tier character varying(50),
    target_region character varying(50),
    nodes text,
    edges text,
    status character varying(50),
    is_approved boolean,
    approval_id character varying(100),
    approved_by character varying(100),
    approved_at double precision,
    tenant_id character varying(50),
    user_id character varying(100),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE architecture.architecture_versions OWNER TO postgres;

--
-- Name: studio_sessions; Type: TABLE; Schema: architecture; Owner: postgres
--

CREATE TABLE architecture.studio_sessions (
    session_id character varying(100) NOT NULL,
    tenant_id character varying(50),
    user_id character varying(100),
    project_id character varying(100),
    version_id character varying(100),
    state_data text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE architecture.studio_sessions OWNER TO postgres;

--
-- Name: generated_iac_bundles; Type: TABLE; Schema: iac; Owner: postgres
--

CREATE TABLE iac.generated_iac_bundles (
    terraform_version_id character varying(100) NOT NULL,
    architecture_version_id character varying(100) NOT NULL,
    project_name character varying(100),
    aws_region character varying(50),
    iac_tool character varying(50),
    checksum character varying(128) NOT NULL,
    files_json text NOT NULL,
    tenant_id character varying(50),
    user_id character varying(100),
    created_at timestamp without time zone
);


ALTER TABLE iac.generated_iac_bundles OWNER TO postgres;

--
-- Name: aether_dashboard_preferences; Type: TABLE; Schema: project_manager; Owner: postgres
--

CREATE TABLE project_manager.aether_dashboard_preferences (
    id character varying(36) NOT NULL,
    user_id character varying(100) NOT NULL,
    tenant_id character varying(36),
    layout character varying(4000),
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE project_manager.aether_dashboard_preferences OWNER TO postgres;

--
-- Name: aether_environments; Type: TABLE; Schema: project_manager; Owner: postgres
--

CREATE TABLE project_manager.aether_environments (
    id character varying(36) NOT NULL,
    project_id character varying(36) NOT NULL,
    tenant_id character varying(36),
    created_by_user_id character varying(36),
    account_id character varying(36),
    name character varying(100) NOT NULL,
    env_type character varying(30) NOT NULL,
    aws_region character varying(50) NOT NULL,
    description character varying(500),
    status character varying(40) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE project_manager.aether_environments OWNER TO postgres;

--
-- Name: aether_projects; Type: TABLE; Schema: project_manager; Owner: postgres
--

CREATE TABLE project_manager.aether_projects (
    id character varying(36) NOT NULL,
    name character varying(100) NOT NULL,
    description character varying(500),
    project_type character varying(50) NOT NULL,
    owner character varying(100) NOT NULL,
    tenant_id character varying(36),
    created_by_user_id character varying(36),
    account_id character varying(36),
    status character varying(30) NOT NULL,
    environment_count integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE project_manager.aether_projects OWNER TO postgres;

--
-- Name: aether_tenant_memberships; Type: TABLE; Schema: project_manager; Owner: postgres
--

CREATE TABLE project_manager.aether_tenant_memberships (
    id character varying(36) NOT NULL,
    tenant_id character varying(36) NOT NULL,
    user_id character varying(36) NOT NULL,
    role character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE project_manager.aether_tenant_memberships OWNER TO postgres;

--
-- Name: aether_tenants; Type: TABLE; Schema: project_manager; Owner: postgres
--

CREATE TABLE project_manager.aether_tenants (
    id character varying(36) NOT NULL,
    name character varying(100) NOT NULL,
    slug character varying(100) NOT NULL,
    tenant_type character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE project_manager.aether_tenants OWNER TO postgres;

--
-- Name: pm_admin_audit_logs; Type: TABLE; Schema: project_manager; Owner: postgres
--

CREATE TABLE project_manager.pm_admin_audit_logs (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    action character varying(64) NOT NULL,
    target_resource character varying(120),
    status character varying(32) NOT NULL,
    ip_address character varying(64),
    details character varying(500),
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE project_manager.pm_admin_audit_logs OWNER TO postgres;

--
-- Name: pm_admin_audit_logs_id_seq; Type: SEQUENCE; Schema: project_manager; Owner: postgres
--

CREATE SEQUENCE project_manager.pm_admin_audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE project_manager.pm_admin_audit_logs_id_seq OWNER TO postgres;

--
-- Name: pm_admin_audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: project_manager; Owner: postgres
--

ALTER SEQUENCE project_manager.pm_admin_audit_logs_id_seq OWNED BY project_manager.pm_admin_audit_logs.id;


--
-- Name: pm_admin_users; Type: TABLE; Schema: project_manager; Owner: postgres
--

CREATE TABLE project_manager.pm_admin_users (
    id integer NOT NULL,
    uuid character varying(36),
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(32) NOT NULL,
    is_active boolean NOT NULL,
    failed_attempts integer NOT NULL,
    locked_until timestamp without time zone,
    last_login_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE project_manager.pm_admin_users OWNER TO postgres;

--
-- Name: pm_admin_users_id_seq; Type: SEQUENCE; Schema: project_manager; Owner: postgres
--

CREATE SEQUENCE project_manager.pm_admin_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE project_manager.pm_admin_users_id_seq OWNER TO postgres;

--
-- Name: pm_admin_users_id_seq; Type: SEQUENCE OWNED BY; Schema: project_manager; Owner: postgres
--

ALTER SEQUENCE project_manager.pm_admin_users_id_seq OWNED BY project_manager.pm_admin_users.id;


--
-- Name: admin_audit_logs; Type: TABLE; Schema: region_ca_central_1; Owner: postgres
--

CREATE TABLE region_ca_central_1.admin_audit_logs (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    action character varying(64) NOT NULL,
    target_resource character varying(120),
    status character varying(32) NOT NULL,
    ip_address character varying(64),
    details character varying(500),
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_ca_central_1.admin_audit_logs OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE; Schema: region_ca_central_1; Owner: postgres
--

CREATE SEQUENCE region_ca_central_1.admin_audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_ca_central_1.admin_audit_logs_id_seq OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: region_ca_central_1; Owner: postgres
--

ALTER SEQUENCE region_ca_central_1.admin_audit_logs_id_seq OWNED BY region_ca_central_1.admin_audit_logs.id;


--
-- Name: admin_users; Type: TABLE; Schema: region_ca_central_1; Owner: postgres
--

CREATE TABLE region_ca_central_1.admin_users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(32) NOT NULL,
    is_active boolean NOT NULL,
    failed_attempts integer NOT NULL,
    locked_until timestamp without time zone,
    last_login_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_ca_central_1.admin_users OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE; Schema: region_ca_central_1; Owner: postgres
--

CREATE SEQUENCE region_ca_central_1.admin_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_ca_central_1.admin_users_id_seq OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE OWNED BY; Schema: region_ca_central_1; Owner: postgres
--

ALTER SEQUENCE region_ca_central_1.admin_users_id_seq OWNED BY region_ca_central_1.admin_users.id;


--
-- Name: ec2_catalog; Type: TABLE; Schema: region_ca_central_1; Owner: postgres
--

CREATE TABLE region_ca_central_1.ec2_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    network_performance character varying(100) NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_ca_central_1.ec2_catalog OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE; Schema: region_ca_central_1; Owner: postgres
--

CREATE SEQUENCE region_ca_central_1.ec2_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_ca_central_1.ec2_catalog_id_seq OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_ca_central_1; Owner: postgres
--

ALTER SEQUENCE region_ca_central_1.ec2_catalog_id_seq OWNED BY region_ca_central_1.ec2_catalog.id;


--
-- Name: generic_service_catalog; Type: TABLE; Schema: region_ca_central_1; Owner: postgres
--

CREATE TABLE region_ca_central_1.generic_service_catalog (
    id integer NOT NULL,
    service character varying(50) NOT NULL,
    instance_type character varying(100) NOT NULL,
    vcpus integer,
    ram_gb double precision,
    price_per_hour double precision NOT NULL,
    unit character varying(50),
    category character varying(50) NOT NULL,
    region character varying(50),
    details character varying(500)
);


ALTER TABLE region_ca_central_1.generic_service_catalog OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE; Schema: region_ca_central_1; Owner: postgres
--

CREATE SEQUENCE region_ca_central_1.generic_service_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_ca_central_1.generic_service_catalog_id_seq OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_ca_central_1; Owner: postgres
--

ALTER SEQUENCE region_ca_central_1.generic_service_catalog_id_seq OWNED BY region_ca_central_1.generic_service_catalog.id;


--
-- Name: rds_catalog; Type: TABLE; Schema: region_ca_central_1; Owner: postgres
--

CREATE TABLE region_ca_central_1.rds_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_ca_central_1.rds_catalog OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE; Schema: region_ca_central_1; Owner: postgres
--

CREATE SEQUENCE region_ca_central_1.rds_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_ca_central_1.rds_catalog_id_seq OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_ca_central_1; Owner: postgres
--

ALTER SEQUENCE region_ca_central_1.rds_catalog_id_seq OWNED BY region_ca_central_1.rds_catalog.id;


--
-- Name: requirement_projects; Type: TABLE; Schema: region_ca_central_1; Owner: postgres
--

CREATE TABLE region_ca_central_1.requirement_projects (
    id character varying(36) NOT NULL,
    project_name character varying(100) NOT NULL,
    description character varying(500),
    stream character varying(50) NOT NULL,
    target_region character varying(50) NOT NULL,
    traffic_scale character varying(50) NOT NULL,
    reliability character varying(50) NOT NULL,
    security_need character varying(50) NOT NULL,
    data_storage_gb double precision NOT NULL,
    monthly_budget double precision,
    tech_stack text,
    operations text,
    monitoring text,
    architecture_tier character varying(50) NOT NULL,
    estimated_monthly_cost double precision NOT NULL,
    cost_breakdown text,
    service_rationales text,
    cost_optimizations text,
    profile_output text,
    status character varying(30) NOT NULL,
    dispatched_to_m2 boolean,
    m2_graph_summary text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE region_ca_central_1.requirement_projects OWNER TO postgres;

--
-- Name: sync_metadata; Type: TABLE; Schema: region_ca_central_1; Owner: postgres
--

CREATE TABLE region_ca_central_1.sync_metadata (
    id integer NOT NULL,
    region_code character varying(50) NOT NULL,
    last_sync_timestamp timestamp without time zone NOT NULL,
    status character varying(20) NOT NULL,
    records_synced integer NOT NULL,
    ec2_count integer NOT NULL,
    rds_count integer NOT NULL,
    generic_count integer NOT NULL,
    duration_ms integer NOT NULL,
    error_message character varying(500)
);


ALTER TABLE region_ca_central_1.sync_metadata OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE; Schema: region_ca_central_1; Owner: postgres
--

CREATE SEQUENCE region_ca_central_1.sync_metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_ca_central_1.sync_metadata_id_seq OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: region_ca_central_1; Owner: postgres
--

ALTER SEQUENCE region_ca_central_1.sync_metadata_id_seq OWNED BY region_ca_central_1.sync_metadata.id;


--
-- Name: admin_audit_logs; Type: TABLE; Schema: region_ca_west_1; Owner: postgres
--

CREATE TABLE region_ca_west_1.admin_audit_logs (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    action character varying(64) NOT NULL,
    target_resource character varying(120),
    status character varying(32) NOT NULL,
    ip_address character varying(64),
    details character varying(500),
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_ca_west_1.admin_audit_logs OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE; Schema: region_ca_west_1; Owner: postgres
--

CREATE SEQUENCE region_ca_west_1.admin_audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_ca_west_1.admin_audit_logs_id_seq OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: region_ca_west_1; Owner: postgres
--

ALTER SEQUENCE region_ca_west_1.admin_audit_logs_id_seq OWNED BY region_ca_west_1.admin_audit_logs.id;


--
-- Name: admin_users; Type: TABLE; Schema: region_ca_west_1; Owner: postgres
--

CREATE TABLE region_ca_west_1.admin_users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(32) NOT NULL,
    is_active boolean NOT NULL,
    failed_attempts integer NOT NULL,
    locked_until timestamp without time zone,
    last_login_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_ca_west_1.admin_users OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE; Schema: region_ca_west_1; Owner: postgres
--

CREATE SEQUENCE region_ca_west_1.admin_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_ca_west_1.admin_users_id_seq OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE OWNED BY; Schema: region_ca_west_1; Owner: postgres
--

ALTER SEQUENCE region_ca_west_1.admin_users_id_seq OWNED BY region_ca_west_1.admin_users.id;


--
-- Name: ec2_catalog; Type: TABLE; Schema: region_ca_west_1; Owner: postgres
--

CREATE TABLE region_ca_west_1.ec2_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    network_performance character varying(100) NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_ca_west_1.ec2_catalog OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE; Schema: region_ca_west_1; Owner: postgres
--

CREATE SEQUENCE region_ca_west_1.ec2_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_ca_west_1.ec2_catalog_id_seq OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_ca_west_1; Owner: postgres
--

ALTER SEQUENCE region_ca_west_1.ec2_catalog_id_seq OWNED BY region_ca_west_1.ec2_catalog.id;


--
-- Name: generic_service_catalog; Type: TABLE; Schema: region_ca_west_1; Owner: postgres
--

CREATE TABLE region_ca_west_1.generic_service_catalog (
    id integer NOT NULL,
    service character varying(50) NOT NULL,
    instance_type character varying(100) NOT NULL,
    vcpus integer,
    ram_gb double precision,
    price_per_hour double precision NOT NULL,
    unit character varying(50),
    category character varying(50) NOT NULL,
    region character varying(50),
    details character varying(500)
);


ALTER TABLE region_ca_west_1.generic_service_catalog OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE; Schema: region_ca_west_1; Owner: postgres
--

CREATE SEQUENCE region_ca_west_1.generic_service_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_ca_west_1.generic_service_catalog_id_seq OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_ca_west_1; Owner: postgres
--

ALTER SEQUENCE region_ca_west_1.generic_service_catalog_id_seq OWNED BY region_ca_west_1.generic_service_catalog.id;


--
-- Name: rds_catalog; Type: TABLE; Schema: region_ca_west_1; Owner: postgres
--

CREATE TABLE region_ca_west_1.rds_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_ca_west_1.rds_catalog OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE; Schema: region_ca_west_1; Owner: postgres
--

CREATE SEQUENCE region_ca_west_1.rds_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_ca_west_1.rds_catalog_id_seq OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_ca_west_1; Owner: postgres
--

ALTER SEQUENCE region_ca_west_1.rds_catalog_id_seq OWNED BY region_ca_west_1.rds_catalog.id;


--
-- Name: requirement_projects; Type: TABLE; Schema: region_ca_west_1; Owner: postgres
--

CREATE TABLE region_ca_west_1.requirement_projects (
    id character varying(36) NOT NULL,
    project_name character varying(100) NOT NULL,
    description character varying(500),
    stream character varying(50) NOT NULL,
    target_region character varying(50) NOT NULL,
    traffic_scale character varying(50) NOT NULL,
    reliability character varying(50) NOT NULL,
    security_need character varying(50) NOT NULL,
    data_storage_gb double precision NOT NULL,
    monthly_budget double precision,
    tech_stack text,
    operations text,
    monitoring text,
    architecture_tier character varying(50) NOT NULL,
    estimated_monthly_cost double precision NOT NULL,
    cost_breakdown text,
    service_rationales text,
    cost_optimizations text,
    profile_output text,
    status character varying(30) NOT NULL,
    dispatched_to_m2 boolean,
    m2_graph_summary text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE region_ca_west_1.requirement_projects OWNER TO postgres;

--
-- Name: sync_metadata; Type: TABLE; Schema: region_ca_west_1; Owner: postgres
--

CREATE TABLE region_ca_west_1.sync_metadata (
    id integer NOT NULL,
    region_code character varying(50) NOT NULL,
    last_sync_timestamp timestamp without time zone NOT NULL,
    status character varying(20) NOT NULL,
    records_synced integer NOT NULL,
    ec2_count integer NOT NULL,
    rds_count integer NOT NULL,
    generic_count integer NOT NULL,
    duration_ms integer NOT NULL,
    error_message character varying(500)
);


ALTER TABLE region_ca_west_1.sync_metadata OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE; Schema: region_ca_west_1; Owner: postgres
--

CREATE SEQUENCE region_ca_west_1.sync_metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_ca_west_1.sync_metadata_id_seq OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: region_ca_west_1; Owner: postgres
--

ALTER SEQUENCE region_ca_west_1.sync_metadata_id_seq OWNED BY region_ca_west_1.sync_metadata.id;


--
-- Name: admin_audit_logs; Type: TABLE; Schema: region_mx_central_1; Owner: postgres
--

CREATE TABLE region_mx_central_1.admin_audit_logs (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    action character varying(64) NOT NULL,
    target_resource character varying(120),
    status character varying(32) NOT NULL,
    ip_address character varying(64),
    details character varying(500),
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_mx_central_1.admin_audit_logs OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE; Schema: region_mx_central_1; Owner: postgres
--

CREATE SEQUENCE region_mx_central_1.admin_audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_mx_central_1.admin_audit_logs_id_seq OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: region_mx_central_1; Owner: postgres
--

ALTER SEQUENCE region_mx_central_1.admin_audit_logs_id_seq OWNED BY region_mx_central_1.admin_audit_logs.id;


--
-- Name: admin_users; Type: TABLE; Schema: region_mx_central_1; Owner: postgres
--

CREATE TABLE region_mx_central_1.admin_users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(32) NOT NULL,
    is_active boolean NOT NULL,
    failed_attempts integer NOT NULL,
    locked_until timestamp without time zone,
    last_login_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_mx_central_1.admin_users OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE; Schema: region_mx_central_1; Owner: postgres
--

CREATE SEQUENCE region_mx_central_1.admin_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_mx_central_1.admin_users_id_seq OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE OWNED BY; Schema: region_mx_central_1; Owner: postgres
--

ALTER SEQUENCE region_mx_central_1.admin_users_id_seq OWNED BY region_mx_central_1.admin_users.id;


--
-- Name: ec2_catalog; Type: TABLE; Schema: region_mx_central_1; Owner: postgres
--

CREATE TABLE region_mx_central_1.ec2_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    network_performance character varying(100) NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_mx_central_1.ec2_catalog OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE; Schema: region_mx_central_1; Owner: postgres
--

CREATE SEQUENCE region_mx_central_1.ec2_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_mx_central_1.ec2_catalog_id_seq OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_mx_central_1; Owner: postgres
--

ALTER SEQUENCE region_mx_central_1.ec2_catalog_id_seq OWNED BY region_mx_central_1.ec2_catalog.id;


--
-- Name: generic_service_catalog; Type: TABLE; Schema: region_mx_central_1; Owner: postgres
--

CREATE TABLE region_mx_central_1.generic_service_catalog (
    id integer NOT NULL,
    service character varying(50) NOT NULL,
    instance_type character varying(100) NOT NULL,
    vcpus integer,
    ram_gb double precision,
    price_per_hour double precision NOT NULL,
    unit character varying(50),
    category character varying(50) NOT NULL,
    region character varying(50),
    details character varying(500)
);


ALTER TABLE region_mx_central_1.generic_service_catalog OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE; Schema: region_mx_central_1; Owner: postgres
--

CREATE SEQUENCE region_mx_central_1.generic_service_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_mx_central_1.generic_service_catalog_id_seq OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_mx_central_1; Owner: postgres
--

ALTER SEQUENCE region_mx_central_1.generic_service_catalog_id_seq OWNED BY region_mx_central_1.generic_service_catalog.id;


--
-- Name: rds_catalog; Type: TABLE; Schema: region_mx_central_1; Owner: postgres
--

CREATE TABLE region_mx_central_1.rds_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_mx_central_1.rds_catalog OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE; Schema: region_mx_central_1; Owner: postgres
--

CREATE SEQUENCE region_mx_central_1.rds_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_mx_central_1.rds_catalog_id_seq OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_mx_central_1; Owner: postgres
--

ALTER SEQUENCE region_mx_central_1.rds_catalog_id_seq OWNED BY region_mx_central_1.rds_catalog.id;


--
-- Name: requirement_projects; Type: TABLE; Schema: region_mx_central_1; Owner: postgres
--

CREATE TABLE region_mx_central_1.requirement_projects (
    id character varying(36) NOT NULL,
    project_name character varying(100) NOT NULL,
    description character varying(500),
    stream character varying(50) NOT NULL,
    target_region character varying(50) NOT NULL,
    traffic_scale character varying(50) NOT NULL,
    reliability character varying(50) NOT NULL,
    security_need character varying(50) NOT NULL,
    data_storage_gb double precision NOT NULL,
    monthly_budget double precision,
    tech_stack text,
    operations text,
    monitoring text,
    architecture_tier character varying(50) NOT NULL,
    estimated_monthly_cost double precision NOT NULL,
    cost_breakdown text,
    service_rationales text,
    cost_optimizations text,
    profile_output text,
    status character varying(30) NOT NULL,
    dispatched_to_m2 boolean,
    m2_graph_summary text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE region_mx_central_1.requirement_projects OWNER TO postgres;

--
-- Name: sync_metadata; Type: TABLE; Schema: region_mx_central_1; Owner: postgres
--

CREATE TABLE region_mx_central_1.sync_metadata (
    id integer NOT NULL,
    region_code character varying(50) NOT NULL,
    last_sync_timestamp timestamp without time zone NOT NULL,
    status character varying(20) NOT NULL,
    records_synced integer NOT NULL,
    ec2_count integer NOT NULL,
    rds_count integer NOT NULL,
    generic_count integer NOT NULL,
    duration_ms integer NOT NULL,
    error_message character varying(500)
);


ALTER TABLE region_mx_central_1.sync_metadata OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE; Schema: region_mx_central_1; Owner: postgres
--

CREATE SEQUENCE region_mx_central_1.sync_metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_mx_central_1.sync_metadata_id_seq OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: region_mx_central_1; Owner: postgres
--

ALTER SEQUENCE region_mx_central_1.sync_metadata_id_seq OWNED BY region_mx_central_1.sync_metadata.id;


--
-- Name: admin_audit_logs; Type: TABLE; Schema: region_sa_east_1; Owner: postgres
--

CREATE TABLE region_sa_east_1.admin_audit_logs (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    action character varying(64) NOT NULL,
    target_resource character varying(120),
    status character varying(32) NOT NULL,
    ip_address character varying(64),
    details character varying(500),
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_sa_east_1.admin_audit_logs OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE; Schema: region_sa_east_1; Owner: postgres
--

CREATE SEQUENCE region_sa_east_1.admin_audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_sa_east_1.admin_audit_logs_id_seq OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: region_sa_east_1; Owner: postgres
--

ALTER SEQUENCE region_sa_east_1.admin_audit_logs_id_seq OWNED BY region_sa_east_1.admin_audit_logs.id;


--
-- Name: admin_users; Type: TABLE; Schema: region_sa_east_1; Owner: postgres
--

CREATE TABLE region_sa_east_1.admin_users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(32) NOT NULL,
    is_active boolean NOT NULL,
    failed_attempts integer NOT NULL,
    locked_until timestamp without time zone,
    last_login_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_sa_east_1.admin_users OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE; Schema: region_sa_east_1; Owner: postgres
--

CREATE SEQUENCE region_sa_east_1.admin_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_sa_east_1.admin_users_id_seq OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE OWNED BY; Schema: region_sa_east_1; Owner: postgres
--

ALTER SEQUENCE region_sa_east_1.admin_users_id_seq OWNED BY region_sa_east_1.admin_users.id;


--
-- Name: ec2_catalog; Type: TABLE; Schema: region_sa_east_1; Owner: postgres
--

CREATE TABLE region_sa_east_1.ec2_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    network_performance character varying(100) NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_sa_east_1.ec2_catalog OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE; Schema: region_sa_east_1; Owner: postgres
--

CREATE SEQUENCE region_sa_east_1.ec2_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_sa_east_1.ec2_catalog_id_seq OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_sa_east_1; Owner: postgres
--

ALTER SEQUENCE region_sa_east_1.ec2_catalog_id_seq OWNED BY region_sa_east_1.ec2_catalog.id;


--
-- Name: generic_service_catalog; Type: TABLE; Schema: region_sa_east_1; Owner: postgres
--

CREATE TABLE region_sa_east_1.generic_service_catalog (
    id integer NOT NULL,
    service character varying(50) NOT NULL,
    instance_type character varying(100) NOT NULL,
    vcpus integer,
    ram_gb double precision,
    price_per_hour double precision NOT NULL,
    unit character varying(50),
    category character varying(50) NOT NULL,
    region character varying(50),
    details character varying(500)
);


ALTER TABLE region_sa_east_1.generic_service_catalog OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE; Schema: region_sa_east_1; Owner: postgres
--

CREATE SEQUENCE region_sa_east_1.generic_service_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_sa_east_1.generic_service_catalog_id_seq OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_sa_east_1; Owner: postgres
--

ALTER SEQUENCE region_sa_east_1.generic_service_catalog_id_seq OWNED BY region_sa_east_1.generic_service_catalog.id;


--
-- Name: rds_catalog; Type: TABLE; Schema: region_sa_east_1; Owner: postgres
--

CREATE TABLE region_sa_east_1.rds_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_sa_east_1.rds_catalog OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE; Schema: region_sa_east_1; Owner: postgres
--

CREATE SEQUENCE region_sa_east_1.rds_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_sa_east_1.rds_catalog_id_seq OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_sa_east_1; Owner: postgres
--

ALTER SEQUENCE region_sa_east_1.rds_catalog_id_seq OWNED BY region_sa_east_1.rds_catalog.id;


--
-- Name: requirement_projects; Type: TABLE; Schema: region_sa_east_1; Owner: postgres
--

CREATE TABLE region_sa_east_1.requirement_projects (
    id character varying(36) NOT NULL,
    project_name character varying(100) NOT NULL,
    description character varying(500),
    stream character varying(50) NOT NULL,
    target_region character varying(50) NOT NULL,
    traffic_scale character varying(50) NOT NULL,
    reliability character varying(50) NOT NULL,
    security_need character varying(50) NOT NULL,
    data_storage_gb double precision NOT NULL,
    monthly_budget double precision,
    tech_stack text,
    operations text,
    monitoring text,
    architecture_tier character varying(50) NOT NULL,
    estimated_monthly_cost double precision NOT NULL,
    cost_breakdown text,
    service_rationales text,
    cost_optimizations text,
    profile_output text,
    status character varying(30) NOT NULL,
    dispatched_to_m2 boolean,
    m2_graph_summary text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE region_sa_east_1.requirement_projects OWNER TO postgres;

--
-- Name: sync_metadata; Type: TABLE; Schema: region_sa_east_1; Owner: postgres
--

CREATE TABLE region_sa_east_1.sync_metadata (
    id integer NOT NULL,
    region_code character varying(50) NOT NULL,
    last_sync_timestamp timestamp without time zone NOT NULL,
    status character varying(20) NOT NULL,
    records_synced integer NOT NULL,
    ec2_count integer NOT NULL,
    rds_count integer NOT NULL,
    generic_count integer NOT NULL,
    duration_ms integer NOT NULL,
    error_message character varying(500)
);


ALTER TABLE region_sa_east_1.sync_metadata OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE; Schema: region_sa_east_1; Owner: postgres
--

CREATE SEQUENCE region_sa_east_1.sync_metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_sa_east_1.sync_metadata_id_seq OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: region_sa_east_1; Owner: postgres
--

ALTER SEQUENCE region_sa_east_1.sync_metadata_id_seq OWNED BY region_sa_east_1.sync_metadata.id;


--
-- Name: admin_audit_logs; Type: TABLE; Schema: region_us_east_1; Owner: postgres
--

CREATE TABLE region_us_east_1.admin_audit_logs (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    action character varying(64) NOT NULL,
    target_resource character varying(120),
    status character varying(32) NOT NULL,
    ip_address character varying(64),
    details character varying(500),
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_us_east_1.admin_audit_logs OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE; Schema: region_us_east_1; Owner: postgres
--

CREATE SEQUENCE region_us_east_1.admin_audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_east_1.admin_audit_logs_id_seq OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_east_1; Owner: postgres
--

ALTER SEQUENCE region_us_east_1.admin_audit_logs_id_seq OWNED BY region_us_east_1.admin_audit_logs.id;


--
-- Name: admin_users; Type: TABLE; Schema: region_us_east_1; Owner: postgres
--

CREATE TABLE region_us_east_1.admin_users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(32) NOT NULL,
    is_active boolean NOT NULL,
    failed_attempts integer NOT NULL,
    locked_until timestamp without time zone,
    last_login_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_us_east_1.admin_users OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE; Schema: region_us_east_1; Owner: postgres
--

CREATE SEQUENCE region_us_east_1.admin_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_east_1.admin_users_id_seq OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_east_1; Owner: postgres
--

ALTER SEQUENCE region_us_east_1.admin_users_id_seq OWNED BY region_us_east_1.admin_users.id;


--
-- Name: ec2_catalog; Type: TABLE; Schema: region_us_east_1; Owner: postgres
--

CREATE TABLE region_us_east_1.ec2_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    network_performance character varying(100) NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_us_east_1.ec2_catalog OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE; Schema: region_us_east_1; Owner: postgres
--

CREATE SEQUENCE region_us_east_1.ec2_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_east_1.ec2_catalog_id_seq OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_east_1; Owner: postgres
--

ALTER SEQUENCE region_us_east_1.ec2_catalog_id_seq OWNED BY region_us_east_1.ec2_catalog.id;


--
-- Name: generic_service_catalog; Type: TABLE; Schema: region_us_east_1; Owner: postgres
--

CREATE TABLE region_us_east_1.generic_service_catalog (
    id integer NOT NULL,
    service character varying(50) NOT NULL,
    instance_type character varying(100) NOT NULL,
    vcpus integer,
    ram_gb double precision,
    price_per_hour double precision NOT NULL,
    unit character varying(50),
    category character varying(50) NOT NULL,
    region character varying(50),
    details character varying(500)
);


ALTER TABLE region_us_east_1.generic_service_catalog OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE; Schema: region_us_east_1; Owner: postgres
--

CREATE SEQUENCE region_us_east_1.generic_service_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_east_1.generic_service_catalog_id_seq OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_east_1; Owner: postgres
--

ALTER SEQUENCE region_us_east_1.generic_service_catalog_id_seq OWNED BY region_us_east_1.generic_service_catalog.id;


--
-- Name: rds_catalog; Type: TABLE; Schema: region_us_east_1; Owner: postgres
--

CREATE TABLE region_us_east_1.rds_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_us_east_1.rds_catalog OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE; Schema: region_us_east_1; Owner: postgres
--

CREATE SEQUENCE region_us_east_1.rds_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_east_1.rds_catalog_id_seq OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_east_1; Owner: postgres
--

ALTER SEQUENCE region_us_east_1.rds_catalog_id_seq OWNED BY region_us_east_1.rds_catalog.id;


--
-- Name: requirement_projects; Type: TABLE; Schema: region_us_east_1; Owner: postgres
--

CREATE TABLE region_us_east_1.requirement_projects (
    id character varying(36) NOT NULL,
    project_name character varying(100) NOT NULL,
    description character varying(500),
    stream character varying(50) NOT NULL,
    target_region character varying(50) NOT NULL,
    traffic_scale character varying(50) NOT NULL,
    reliability character varying(50) NOT NULL,
    security_need character varying(50) NOT NULL,
    data_storage_gb double precision NOT NULL,
    monthly_budget double precision,
    tech_stack text,
    operations text,
    monitoring text,
    architecture_tier character varying(50) NOT NULL,
    estimated_monthly_cost double precision NOT NULL,
    cost_breakdown text,
    service_rationales text,
    cost_optimizations text,
    profile_output text,
    status character varying(30) NOT NULL,
    dispatched_to_m2 boolean,
    m2_graph_summary text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE region_us_east_1.requirement_projects OWNER TO postgres;

--
-- Name: sync_metadata; Type: TABLE; Schema: region_us_east_1; Owner: postgres
--

CREATE TABLE region_us_east_1.sync_metadata (
    id integer NOT NULL,
    region_code character varying(50) NOT NULL,
    last_sync_timestamp timestamp without time zone NOT NULL,
    status character varying(20) NOT NULL,
    records_synced integer NOT NULL,
    ec2_count integer NOT NULL,
    rds_count integer NOT NULL,
    generic_count integer NOT NULL,
    duration_ms integer NOT NULL,
    error_message character varying(500)
);


ALTER TABLE region_us_east_1.sync_metadata OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE; Schema: region_us_east_1; Owner: postgres
--

CREATE SEQUENCE region_us_east_1.sync_metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_east_1.sync_metadata_id_seq OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_east_1; Owner: postgres
--

ALTER SEQUENCE region_us_east_1.sync_metadata_id_seq OWNED BY region_us_east_1.sync_metadata.id;


--
-- Name: admin_audit_logs; Type: TABLE; Schema: region_us_east_2; Owner: postgres
--

CREATE TABLE region_us_east_2.admin_audit_logs (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    action character varying(64) NOT NULL,
    target_resource character varying(120),
    status character varying(32) NOT NULL,
    ip_address character varying(64),
    details character varying(500),
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_us_east_2.admin_audit_logs OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE; Schema: region_us_east_2; Owner: postgres
--

CREATE SEQUENCE region_us_east_2.admin_audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_east_2.admin_audit_logs_id_seq OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_east_2; Owner: postgres
--

ALTER SEQUENCE region_us_east_2.admin_audit_logs_id_seq OWNED BY region_us_east_2.admin_audit_logs.id;


--
-- Name: admin_users; Type: TABLE; Schema: region_us_east_2; Owner: postgres
--

CREATE TABLE region_us_east_2.admin_users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(32) NOT NULL,
    is_active boolean NOT NULL,
    failed_attempts integer NOT NULL,
    locked_until timestamp without time zone,
    last_login_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_us_east_2.admin_users OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE; Schema: region_us_east_2; Owner: postgres
--

CREATE SEQUENCE region_us_east_2.admin_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_east_2.admin_users_id_seq OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_east_2; Owner: postgres
--

ALTER SEQUENCE region_us_east_2.admin_users_id_seq OWNED BY region_us_east_2.admin_users.id;


--
-- Name: ec2_catalog; Type: TABLE; Schema: region_us_east_2; Owner: postgres
--

CREATE TABLE region_us_east_2.ec2_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    network_performance character varying(100) NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_us_east_2.ec2_catalog OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE; Schema: region_us_east_2; Owner: postgres
--

CREATE SEQUENCE region_us_east_2.ec2_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_east_2.ec2_catalog_id_seq OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_east_2; Owner: postgres
--

ALTER SEQUENCE region_us_east_2.ec2_catalog_id_seq OWNED BY region_us_east_2.ec2_catalog.id;


--
-- Name: generic_service_catalog; Type: TABLE; Schema: region_us_east_2; Owner: postgres
--

CREATE TABLE region_us_east_2.generic_service_catalog (
    id integer NOT NULL,
    service character varying(50) NOT NULL,
    instance_type character varying(100) NOT NULL,
    vcpus integer,
    ram_gb double precision,
    price_per_hour double precision NOT NULL,
    unit character varying(50),
    category character varying(50) NOT NULL,
    region character varying(50),
    details character varying(500)
);


ALTER TABLE region_us_east_2.generic_service_catalog OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE; Schema: region_us_east_2; Owner: postgres
--

CREATE SEQUENCE region_us_east_2.generic_service_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_east_2.generic_service_catalog_id_seq OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_east_2; Owner: postgres
--

ALTER SEQUENCE region_us_east_2.generic_service_catalog_id_seq OWNED BY region_us_east_2.generic_service_catalog.id;


--
-- Name: rds_catalog; Type: TABLE; Schema: region_us_east_2; Owner: postgres
--

CREATE TABLE region_us_east_2.rds_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_us_east_2.rds_catalog OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE; Schema: region_us_east_2; Owner: postgres
--

CREATE SEQUENCE region_us_east_2.rds_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_east_2.rds_catalog_id_seq OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_east_2; Owner: postgres
--

ALTER SEQUENCE region_us_east_2.rds_catalog_id_seq OWNED BY region_us_east_2.rds_catalog.id;


--
-- Name: requirement_projects; Type: TABLE; Schema: region_us_east_2; Owner: postgres
--

CREATE TABLE region_us_east_2.requirement_projects (
    id character varying(36) NOT NULL,
    project_name character varying(100) NOT NULL,
    description character varying(500),
    stream character varying(50) NOT NULL,
    target_region character varying(50) NOT NULL,
    traffic_scale character varying(50) NOT NULL,
    reliability character varying(50) NOT NULL,
    security_need character varying(50) NOT NULL,
    data_storage_gb double precision NOT NULL,
    monthly_budget double precision,
    tech_stack text,
    operations text,
    monitoring text,
    architecture_tier character varying(50) NOT NULL,
    estimated_monthly_cost double precision NOT NULL,
    cost_breakdown text,
    service_rationales text,
    cost_optimizations text,
    profile_output text,
    status character varying(30) NOT NULL,
    dispatched_to_m2 boolean,
    m2_graph_summary text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE region_us_east_2.requirement_projects OWNER TO postgres;

--
-- Name: sync_metadata; Type: TABLE; Schema: region_us_east_2; Owner: postgres
--

CREATE TABLE region_us_east_2.sync_metadata (
    id integer NOT NULL,
    region_code character varying(50) NOT NULL,
    last_sync_timestamp timestamp without time zone NOT NULL,
    status character varying(20) NOT NULL,
    records_synced integer NOT NULL,
    ec2_count integer NOT NULL,
    rds_count integer NOT NULL,
    generic_count integer NOT NULL,
    duration_ms integer NOT NULL,
    error_message character varying(500)
);


ALTER TABLE region_us_east_2.sync_metadata OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE; Schema: region_us_east_2; Owner: postgres
--

CREATE SEQUENCE region_us_east_2.sync_metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_east_2.sync_metadata_id_seq OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_east_2; Owner: postgres
--

ALTER SEQUENCE region_us_east_2.sync_metadata_id_seq OWNED BY region_us_east_2.sync_metadata.id;


--
-- Name: admin_audit_logs; Type: TABLE; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE TABLE region_us_gov_east_1.admin_audit_logs (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    action character varying(64) NOT NULL,
    target_resource character varying(120),
    status character varying(32) NOT NULL,
    ip_address character varying(64),
    details character varying(500),
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_us_gov_east_1.admin_audit_logs OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE SEQUENCE region_us_gov_east_1.admin_audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_gov_east_1.admin_audit_logs_id_seq OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER SEQUENCE region_us_gov_east_1.admin_audit_logs_id_seq OWNED BY region_us_gov_east_1.admin_audit_logs.id;


--
-- Name: admin_users; Type: TABLE; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE TABLE region_us_gov_east_1.admin_users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(32) NOT NULL,
    is_active boolean NOT NULL,
    failed_attempts integer NOT NULL,
    locked_until timestamp without time zone,
    last_login_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_us_gov_east_1.admin_users OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE SEQUENCE region_us_gov_east_1.admin_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_gov_east_1.admin_users_id_seq OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER SEQUENCE region_us_gov_east_1.admin_users_id_seq OWNED BY region_us_gov_east_1.admin_users.id;


--
-- Name: ec2_catalog; Type: TABLE; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE TABLE region_us_gov_east_1.ec2_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    network_performance character varying(100) NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_us_gov_east_1.ec2_catalog OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE SEQUENCE region_us_gov_east_1.ec2_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_gov_east_1.ec2_catalog_id_seq OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER SEQUENCE region_us_gov_east_1.ec2_catalog_id_seq OWNED BY region_us_gov_east_1.ec2_catalog.id;


--
-- Name: generic_service_catalog; Type: TABLE; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE TABLE region_us_gov_east_1.generic_service_catalog (
    id integer NOT NULL,
    service character varying(50) NOT NULL,
    instance_type character varying(100) NOT NULL,
    vcpus integer,
    ram_gb double precision,
    price_per_hour double precision NOT NULL,
    unit character varying(50),
    category character varying(50) NOT NULL,
    region character varying(50),
    details character varying(500)
);


ALTER TABLE region_us_gov_east_1.generic_service_catalog OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE SEQUENCE region_us_gov_east_1.generic_service_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_gov_east_1.generic_service_catalog_id_seq OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER SEQUENCE region_us_gov_east_1.generic_service_catalog_id_seq OWNED BY region_us_gov_east_1.generic_service_catalog.id;


--
-- Name: rds_catalog; Type: TABLE; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE TABLE region_us_gov_east_1.rds_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_us_gov_east_1.rds_catalog OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE SEQUENCE region_us_gov_east_1.rds_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_gov_east_1.rds_catalog_id_seq OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER SEQUENCE region_us_gov_east_1.rds_catalog_id_seq OWNED BY region_us_gov_east_1.rds_catalog.id;


--
-- Name: requirement_projects; Type: TABLE; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE TABLE region_us_gov_east_1.requirement_projects (
    id character varying(36) NOT NULL,
    project_name character varying(100) NOT NULL,
    description character varying(500),
    stream character varying(50) NOT NULL,
    target_region character varying(50) NOT NULL,
    traffic_scale character varying(50) NOT NULL,
    reliability character varying(50) NOT NULL,
    security_need character varying(50) NOT NULL,
    data_storage_gb double precision NOT NULL,
    monthly_budget double precision,
    tech_stack text,
    operations text,
    monitoring text,
    architecture_tier character varying(50) NOT NULL,
    estimated_monthly_cost double precision NOT NULL,
    cost_breakdown text,
    service_rationales text,
    cost_optimizations text,
    profile_output text,
    status character varying(30) NOT NULL,
    dispatched_to_m2 boolean,
    m2_graph_summary text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE region_us_gov_east_1.requirement_projects OWNER TO postgres;

--
-- Name: sync_metadata; Type: TABLE; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE TABLE region_us_gov_east_1.sync_metadata (
    id integer NOT NULL,
    region_code character varying(50) NOT NULL,
    last_sync_timestamp timestamp without time zone NOT NULL,
    status character varying(20) NOT NULL,
    records_synced integer NOT NULL,
    ec2_count integer NOT NULL,
    rds_count integer NOT NULL,
    generic_count integer NOT NULL,
    duration_ms integer NOT NULL,
    error_message character varying(500)
);


ALTER TABLE region_us_gov_east_1.sync_metadata OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE SEQUENCE region_us_gov_east_1.sync_metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_gov_east_1.sync_metadata_id_seq OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER SEQUENCE region_us_gov_east_1.sync_metadata_id_seq OWNED BY region_us_gov_east_1.sync_metadata.id;


--
-- Name: admin_audit_logs; Type: TABLE; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE TABLE region_us_gov_west_1.admin_audit_logs (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    action character varying(64) NOT NULL,
    target_resource character varying(120),
    status character varying(32) NOT NULL,
    ip_address character varying(64),
    details character varying(500),
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_us_gov_west_1.admin_audit_logs OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE SEQUENCE region_us_gov_west_1.admin_audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_gov_west_1.admin_audit_logs_id_seq OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER SEQUENCE region_us_gov_west_1.admin_audit_logs_id_seq OWNED BY region_us_gov_west_1.admin_audit_logs.id;


--
-- Name: admin_users; Type: TABLE; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE TABLE region_us_gov_west_1.admin_users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(32) NOT NULL,
    is_active boolean NOT NULL,
    failed_attempts integer NOT NULL,
    locked_until timestamp without time zone,
    last_login_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_us_gov_west_1.admin_users OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE SEQUENCE region_us_gov_west_1.admin_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_gov_west_1.admin_users_id_seq OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER SEQUENCE region_us_gov_west_1.admin_users_id_seq OWNED BY region_us_gov_west_1.admin_users.id;


--
-- Name: ec2_catalog; Type: TABLE; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE TABLE region_us_gov_west_1.ec2_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    network_performance character varying(100) NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_us_gov_west_1.ec2_catalog OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE SEQUENCE region_us_gov_west_1.ec2_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_gov_west_1.ec2_catalog_id_seq OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER SEQUENCE region_us_gov_west_1.ec2_catalog_id_seq OWNED BY region_us_gov_west_1.ec2_catalog.id;


--
-- Name: generic_service_catalog; Type: TABLE; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE TABLE region_us_gov_west_1.generic_service_catalog (
    id integer NOT NULL,
    service character varying(50) NOT NULL,
    instance_type character varying(100) NOT NULL,
    vcpus integer,
    ram_gb double precision,
    price_per_hour double precision NOT NULL,
    unit character varying(50),
    category character varying(50) NOT NULL,
    region character varying(50),
    details character varying(500)
);


ALTER TABLE region_us_gov_west_1.generic_service_catalog OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE SEQUENCE region_us_gov_west_1.generic_service_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_gov_west_1.generic_service_catalog_id_seq OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER SEQUENCE region_us_gov_west_1.generic_service_catalog_id_seq OWNED BY region_us_gov_west_1.generic_service_catalog.id;


--
-- Name: rds_catalog; Type: TABLE; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE TABLE region_us_gov_west_1.rds_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_us_gov_west_1.rds_catalog OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE SEQUENCE region_us_gov_west_1.rds_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_gov_west_1.rds_catalog_id_seq OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER SEQUENCE region_us_gov_west_1.rds_catalog_id_seq OWNED BY region_us_gov_west_1.rds_catalog.id;


--
-- Name: requirement_projects; Type: TABLE; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE TABLE region_us_gov_west_1.requirement_projects (
    id character varying(36) NOT NULL,
    project_name character varying(100) NOT NULL,
    description character varying(500),
    stream character varying(50) NOT NULL,
    target_region character varying(50) NOT NULL,
    traffic_scale character varying(50) NOT NULL,
    reliability character varying(50) NOT NULL,
    security_need character varying(50) NOT NULL,
    data_storage_gb double precision NOT NULL,
    monthly_budget double precision,
    tech_stack text,
    operations text,
    monitoring text,
    architecture_tier character varying(50) NOT NULL,
    estimated_monthly_cost double precision NOT NULL,
    cost_breakdown text,
    service_rationales text,
    cost_optimizations text,
    profile_output text,
    status character varying(30) NOT NULL,
    dispatched_to_m2 boolean,
    m2_graph_summary text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE region_us_gov_west_1.requirement_projects OWNER TO postgres;

--
-- Name: sync_metadata; Type: TABLE; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE TABLE region_us_gov_west_1.sync_metadata (
    id integer NOT NULL,
    region_code character varying(50) NOT NULL,
    last_sync_timestamp timestamp without time zone NOT NULL,
    status character varying(20) NOT NULL,
    records_synced integer NOT NULL,
    ec2_count integer NOT NULL,
    rds_count integer NOT NULL,
    generic_count integer NOT NULL,
    duration_ms integer NOT NULL,
    error_message character varying(500)
);


ALTER TABLE region_us_gov_west_1.sync_metadata OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE SEQUENCE region_us_gov_west_1.sync_metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_gov_west_1.sync_metadata_id_seq OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER SEQUENCE region_us_gov_west_1.sync_metadata_id_seq OWNED BY region_us_gov_west_1.sync_metadata.id;


--
-- Name: admin_audit_logs; Type: TABLE; Schema: region_us_west_1; Owner: postgres
--

CREATE TABLE region_us_west_1.admin_audit_logs (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    action character varying(64) NOT NULL,
    target_resource character varying(120),
    status character varying(32) NOT NULL,
    ip_address character varying(64),
    details character varying(500),
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_us_west_1.admin_audit_logs OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE; Schema: region_us_west_1; Owner: postgres
--

CREATE SEQUENCE region_us_west_1.admin_audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_west_1.admin_audit_logs_id_seq OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_west_1; Owner: postgres
--

ALTER SEQUENCE region_us_west_1.admin_audit_logs_id_seq OWNED BY region_us_west_1.admin_audit_logs.id;


--
-- Name: admin_users; Type: TABLE; Schema: region_us_west_1; Owner: postgres
--

CREATE TABLE region_us_west_1.admin_users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(32) NOT NULL,
    is_active boolean NOT NULL,
    failed_attempts integer NOT NULL,
    locked_until timestamp without time zone,
    last_login_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_us_west_1.admin_users OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE; Schema: region_us_west_1; Owner: postgres
--

CREATE SEQUENCE region_us_west_1.admin_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_west_1.admin_users_id_seq OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_west_1; Owner: postgres
--

ALTER SEQUENCE region_us_west_1.admin_users_id_seq OWNED BY region_us_west_1.admin_users.id;


--
-- Name: ec2_catalog; Type: TABLE; Schema: region_us_west_1; Owner: postgres
--

CREATE TABLE region_us_west_1.ec2_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    network_performance character varying(100) NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_us_west_1.ec2_catalog OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE; Schema: region_us_west_1; Owner: postgres
--

CREATE SEQUENCE region_us_west_1.ec2_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_west_1.ec2_catalog_id_seq OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_west_1; Owner: postgres
--

ALTER SEQUENCE region_us_west_1.ec2_catalog_id_seq OWNED BY region_us_west_1.ec2_catalog.id;


--
-- Name: generic_service_catalog; Type: TABLE; Schema: region_us_west_1; Owner: postgres
--

CREATE TABLE region_us_west_1.generic_service_catalog (
    id integer NOT NULL,
    service character varying(50) NOT NULL,
    instance_type character varying(100) NOT NULL,
    vcpus integer,
    ram_gb double precision,
    price_per_hour double precision NOT NULL,
    unit character varying(50),
    category character varying(50) NOT NULL,
    region character varying(50),
    details character varying(500)
);


ALTER TABLE region_us_west_1.generic_service_catalog OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE; Schema: region_us_west_1; Owner: postgres
--

CREATE SEQUENCE region_us_west_1.generic_service_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_west_1.generic_service_catalog_id_seq OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_west_1; Owner: postgres
--

ALTER SEQUENCE region_us_west_1.generic_service_catalog_id_seq OWNED BY region_us_west_1.generic_service_catalog.id;


--
-- Name: rds_catalog; Type: TABLE; Schema: region_us_west_1; Owner: postgres
--

CREATE TABLE region_us_west_1.rds_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_us_west_1.rds_catalog OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE; Schema: region_us_west_1; Owner: postgres
--

CREATE SEQUENCE region_us_west_1.rds_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_west_1.rds_catalog_id_seq OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_west_1; Owner: postgres
--

ALTER SEQUENCE region_us_west_1.rds_catalog_id_seq OWNED BY region_us_west_1.rds_catalog.id;


--
-- Name: requirement_projects; Type: TABLE; Schema: region_us_west_1; Owner: postgres
--

CREATE TABLE region_us_west_1.requirement_projects (
    id character varying(36) NOT NULL,
    project_name character varying(100) NOT NULL,
    description character varying(500),
    stream character varying(50) NOT NULL,
    target_region character varying(50) NOT NULL,
    traffic_scale character varying(50) NOT NULL,
    reliability character varying(50) NOT NULL,
    security_need character varying(50) NOT NULL,
    data_storage_gb double precision NOT NULL,
    monthly_budget double precision,
    tech_stack text,
    operations text,
    monitoring text,
    architecture_tier character varying(50) NOT NULL,
    estimated_monthly_cost double precision NOT NULL,
    cost_breakdown text,
    service_rationales text,
    cost_optimizations text,
    profile_output text,
    status character varying(30) NOT NULL,
    dispatched_to_m2 boolean,
    m2_graph_summary text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE region_us_west_1.requirement_projects OWNER TO postgres;

--
-- Name: sync_metadata; Type: TABLE; Schema: region_us_west_1; Owner: postgres
--

CREATE TABLE region_us_west_1.sync_metadata (
    id integer NOT NULL,
    region_code character varying(50) NOT NULL,
    last_sync_timestamp timestamp without time zone NOT NULL,
    status character varying(20) NOT NULL,
    records_synced integer NOT NULL,
    ec2_count integer NOT NULL,
    rds_count integer NOT NULL,
    generic_count integer NOT NULL,
    duration_ms integer NOT NULL,
    error_message character varying(500)
);


ALTER TABLE region_us_west_1.sync_metadata OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE; Schema: region_us_west_1; Owner: postgres
--

CREATE SEQUENCE region_us_west_1.sync_metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_west_1.sync_metadata_id_seq OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_west_1; Owner: postgres
--

ALTER SEQUENCE region_us_west_1.sync_metadata_id_seq OWNED BY region_us_west_1.sync_metadata.id;


--
-- Name: admin_audit_logs; Type: TABLE; Schema: region_us_west_2; Owner: postgres
--

CREATE TABLE region_us_west_2.admin_audit_logs (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    action character varying(64) NOT NULL,
    target_resource character varying(120),
    status character varying(32) NOT NULL,
    ip_address character varying(64),
    details character varying(500),
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_us_west_2.admin_audit_logs OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE; Schema: region_us_west_2; Owner: postgres
--

CREATE SEQUENCE region_us_west_2.admin_audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_west_2.admin_audit_logs_id_seq OWNER TO postgres;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_west_2; Owner: postgres
--

ALTER SEQUENCE region_us_west_2.admin_audit_logs_id_seq OWNED BY region_us_west_2.admin_audit_logs.id;


--
-- Name: admin_users; Type: TABLE; Schema: region_us_west_2; Owner: postgres
--

CREATE TABLE region_us_west_2.admin_users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(32) NOT NULL,
    is_active boolean NOT NULL,
    failed_attempts integer NOT NULL,
    locked_until timestamp without time zone,
    last_login_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE region_us_west_2.admin_users OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE; Schema: region_us_west_2; Owner: postgres
--

CREATE SEQUENCE region_us_west_2.admin_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_west_2.admin_users_id_seq OWNER TO postgres;

--
-- Name: admin_users_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_west_2; Owner: postgres
--

ALTER SEQUENCE region_us_west_2.admin_users_id_seq OWNED BY region_us_west_2.admin_users.id;


--
-- Name: ec2_catalog; Type: TABLE; Schema: region_us_west_2; Owner: postgres
--

CREATE TABLE region_us_west_2.ec2_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    network_performance character varying(100) NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_us_west_2.ec2_catalog OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE; Schema: region_us_west_2; Owner: postgres
--

CREATE SEQUENCE region_us_west_2.ec2_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_west_2.ec2_catalog_id_seq OWNER TO postgres;

--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_west_2; Owner: postgres
--

ALTER SEQUENCE region_us_west_2.ec2_catalog_id_seq OWNED BY region_us_west_2.ec2_catalog.id;


--
-- Name: generic_service_catalog; Type: TABLE; Schema: region_us_west_2; Owner: postgres
--

CREATE TABLE region_us_west_2.generic_service_catalog (
    id integer NOT NULL,
    service character varying(50) NOT NULL,
    instance_type character varying(100) NOT NULL,
    vcpus integer,
    ram_gb double precision,
    price_per_hour double precision NOT NULL,
    unit character varying(50),
    category character varying(50) NOT NULL,
    region character varying(50),
    details character varying(500)
);


ALTER TABLE region_us_west_2.generic_service_catalog OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE; Schema: region_us_west_2; Owner: postgres
--

CREATE SEQUENCE region_us_west_2.generic_service_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_west_2.generic_service_catalog_id_seq OWNER TO postgres;

--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_west_2; Owner: postgres
--

ALTER SEQUENCE region_us_west_2.generic_service_catalog_id_seq OWNED BY region_us_west_2.generic_service_catalog.id;


--
-- Name: rds_catalog; Type: TABLE; Schema: region_us_west_2; Owner: postgres
--

CREATE TABLE region_us_west_2.rds_catalog (
    id integer NOT NULL,
    instance_type character varying(50) NOT NULL,
    vcpus integer NOT NULL,
    ram_gb double precision NOT NULL,
    price_per_hour double precision NOT NULL,
    category character varying(50) NOT NULL
);


ALTER TABLE region_us_west_2.rds_catalog OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE; Schema: region_us_west_2; Owner: postgres
--

CREATE SEQUENCE region_us_west_2.rds_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_west_2.rds_catalog_id_seq OWNER TO postgres;

--
-- Name: rds_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_west_2; Owner: postgres
--

ALTER SEQUENCE region_us_west_2.rds_catalog_id_seq OWNED BY region_us_west_2.rds_catalog.id;


--
-- Name: requirement_projects; Type: TABLE; Schema: region_us_west_2; Owner: postgres
--

CREATE TABLE region_us_west_2.requirement_projects (
    id character varying(36) NOT NULL,
    project_name character varying(100) NOT NULL,
    description character varying(500),
    stream character varying(50) NOT NULL,
    target_region character varying(50) NOT NULL,
    traffic_scale character varying(50) NOT NULL,
    reliability character varying(50) NOT NULL,
    security_need character varying(50) NOT NULL,
    data_storage_gb double precision NOT NULL,
    monthly_budget double precision,
    tech_stack text,
    operations text,
    monitoring text,
    architecture_tier character varying(50) NOT NULL,
    estimated_monthly_cost double precision NOT NULL,
    cost_breakdown text,
    service_rationales text,
    cost_optimizations text,
    profile_output text,
    status character varying(30) NOT NULL,
    dispatched_to_m2 boolean,
    m2_graph_summary text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE region_us_west_2.requirement_projects OWNER TO postgres;

--
-- Name: sync_metadata; Type: TABLE; Schema: region_us_west_2; Owner: postgres
--

CREATE TABLE region_us_west_2.sync_metadata (
    id integer NOT NULL,
    region_code character varying(50) NOT NULL,
    last_sync_timestamp timestamp without time zone NOT NULL,
    status character varying(20) NOT NULL,
    records_synced integer NOT NULL,
    ec2_count integer NOT NULL,
    rds_count integer NOT NULL,
    generic_count integer NOT NULL,
    duration_ms integer NOT NULL,
    error_message character varying(500)
);


ALTER TABLE region_us_west_2.sync_metadata OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE; Schema: region_us_west_2; Owner: postgres
--

CREATE SEQUENCE region_us_west_2.sync_metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE region_us_west_2.sync_metadata_id_seq OWNER TO postgres;

--
-- Name: sync_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: region_us_west_2; Owner: postgres
--

ALTER SEQUENCE region_us_west_2.sync_metadata_id_seq OWNED BY region_us_west_2.sync_metadata.id;


--
-- Name: sc_admin_audit_logs; Type: TABLE; Schema: source_connection; Owner: postgres
--

CREATE TABLE source_connection.sc_admin_audit_logs (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    action character varying(64) NOT NULL,
    target_resource character varying(120),
    status character varying(32) NOT NULL,
    ip_address character varying(64),
    details character varying(500),
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE source_connection.sc_admin_audit_logs OWNER TO postgres;

--
-- Name: sc_admin_audit_logs_id_seq; Type: SEQUENCE; Schema: source_connection; Owner: postgres
--

CREATE SEQUENCE source_connection.sc_admin_audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE source_connection.sc_admin_audit_logs_id_seq OWNER TO postgres;

--
-- Name: sc_admin_audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: source_connection; Owner: postgres
--

ALTER SEQUENCE source_connection.sc_admin_audit_logs_id_seq OWNED BY source_connection.sc_admin_audit_logs.id;


--
-- Name: sc_admin_users; Type: TABLE; Schema: source_connection; Owner: postgres
--

CREATE TABLE source_connection.sc_admin_users (
    id integer NOT NULL,
    uuid character varying(36),
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(32) NOT NULL,
    is_active boolean NOT NULL,
    failed_attempts integer NOT NULL,
    locked_until timestamp without time zone,
    last_login_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE source_connection.sc_admin_users OWNER TO postgres;

--
-- Name: sc_admin_users_id_seq; Type: SEQUENCE; Schema: source_connection; Owner: postgres
--

CREATE SEQUENCE source_connection.sc_admin_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE source_connection.sc_admin_users_id_seq OWNER TO postgres;

--
-- Name: sc_admin_users_id_seq; Type: SEQUENCE OWNED BY; Schema: source_connection; Owner: postgres
--

ALTER SEQUENCE source_connection.sc_admin_users_id_seq OWNED BY source_connection.sc_admin_users.id;


--
-- Name: sc_cloud_connections; Type: TABLE; Schema: source_connection; Owner: postgres
--

CREATE TABLE source_connection.sc_cloud_connections (
    id character varying(36) NOT NULL,
    project_id character varying(36) NOT NULL,
    environment_id character varying(36) NOT NULL,
    tenant_id character varying(36),
    created_by_user_id character varying(36),
    owner character varying(100) NOT NULL,
    provider character varying(30) NOT NULL,
    auth_type character varying(30) NOT NULL,
    aws_region character varying(50) NOT NULL,
    access_key_masked character varying(30),
    access_key_id character varying(128),
    secret_key_hash character varying(255),
    encrypted_secret text,
    encryption_nonce character varying(64),
    encryption_tag character varying(64),
    encryption_key_id character varying(64),
    role_arn character varying(300),
    external_id character varying(100),
    account_id character varying(30),
    caller_arn character varying(300),
    caller_user_id character varying(100),
    status character varying(30) NOT NULL,
    last_validated_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE source_connection.sc_cloud_connections OWNER TO postgres;

--
-- Name: sc_git_connections; Type: TABLE; Schema: source_connection; Owner: postgres
--

CREATE TABLE source_connection.sc_git_connections (
    id character varying(36) NOT NULL,
    project_id character varying(36) NOT NULL,
    environment_id character varying(36) NOT NULL,
    tenant_id character varying(36),
    created_by_user_id character varying(36),
    owner character varying(100) NOT NULL,
    repo_url character varying(500) NOT NULL,
    repo_name character varying(200) NOT NULL,
    branch character varying(200) NOT NULL,
    pat_label character varying(100),
    pat_token_hash character varying(255),
    encrypted_pat text,
    pat_nonce character varying(64),
    pat_tag character varying(64),
    auth_type character varying(30),
    github_user character varying(100),
    default_branch character varying(200),
    last_commit_sha character varying(40),
    last_commit_msg character varying(500),
    last_commit_author character varying(200),
    last_commit_at timestamp without time zone,
    is_private boolean,
    stars character varying(20),
    language character varying(50),
    status character varying(30) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE source_connection.sc_git_connections OWNER TO postgres;

--
-- Name: sc_source_snapshots; Type: TABLE; Schema: source_connection; Owner: postgres
--

CREATE TABLE source_connection.sc_source_snapshots (
    id character varying(36) NOT NULL,
    connection_id character varying(36) NOT NULL,
    project_id character varying(36) NOT NULL,
    environment_id character varying(36) NOT NULL,
    commit_sha character varying(40) NOT NULL,
    branch character varying(200) NOT NULL,
    file_tree text,
    detected_files text,
    language_hints text,
    total_files character varying(20),
    total_size_kb character varying(20),
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE source_connection.sc_source_snapshots OWNER TO postgres;

--
-- Name: admin_audit_logs id; Type: DEFAULT; Schema: admin_security; Owner: postgres
--

ALTER TABLE ONLY admin_security.admin_audit_logs ALTER COLUMN id SET DEFAULT nextval('admin_security.admin_audit_logs_id_seq'::regclass);


--
-- Name: admin_users id; Type: DEFAULT; Schema: admin_security; Owner: postgres
--

ALTER TABLE ONLY admin_security.admin_users ALTER COLUMN id SET DEFAULT nextval('admin_security.admin_users_id_seq'::regclass);


--
-- Name: ec2_catalog id; Type: DEFAULT; Schema: admin_security; Owner: postgres
--

ALTER TABLE ONLY admin_security.ec2_catalog ALTER COLUMN id SET DEFAULT nextval('admin_security.ec2_catalog_id_seq'::regclass);


--
-- Name: generic_service_catalog id; Type: DEFAULT; Schema: admin_security; Owner: postgres
--

ALTER TABLE ONLY admin_security.generic_service_catalog ALTER COLUMN id SET DEFAULT nextval('admin_security.generic_service_catalog_id_seq'::regclass);


--
-- Name: rds_catalog id; Type: DEFAULT; Schema: admin_security; Owner: postgres
--

ALTER TABLE ONLY admin_security.rds_catalog ALTER COLUMN id SET DEFAULT nextval('admin_security.rds_catalog_id_seq'::regclass);


--
-- Name: sync_metadata id; Type: DEFAULT; Schema: admin_security; Owner: postgres
--

ALTER TABLE ONLY admin_security.sync_metadata ALTER COLUMN id SET DEFAULT nextval('admin_security.sync_metadata_id_seq'::regclass);


--
-- Name: pm_admin_audit_logs id; Type: DEFAULT; Schema: project_manager; Owner: postgres
--

ALTER TABLE ONLY project_manager.pm_admin_audit_logs ALTER COLUMN id SET DEFAULT nextval('project_manager.pm_admin_audit_logs_id_seq'::regclass);


--
-- Name: pm_admin_users id; Type: DEFAULT; Schema: project_manager; Owner: postgres
--

ALTER TABLE ONLY project_manager.pm_admin_users ALTER COLUMN id SET DEFAULT nextval('project_manager.pm_admin_users_id_seq'::regclass);


--
-- Name: admin_audit_logs id; Type: DEFAULT; Schema: region_ca_central_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_central_1.admin_audit_logs ALTER COLUMN id SET DEFAULT nextval('region_ca_central_1.admin_audit_logs_id_seq'::regclass);


--
-- Name: admin_users id; Type: DEFAULT; Schema: region_ca_central_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_central_1.admin_users ALTER COLUMN id SET DEFAULT nextval('region_ca_central_1.admin_users_id_seq'::regclass);


--
-- Name: ec2_catalog id; Type: DEFAULT; Schema: region_ca_central_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_central_1.ec2_catalog ALTER COLUMN id SET DEFAULT nextval('region_ca_central_1.ec2_catalog_id_seq'::regclass);


--
-- Name: generic_service_catalog id; Type: DEFAULT; Schema: region_ca_central_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_central_1.generic_service_catalog ALTER COLUMN id SET DEFAULT nextval('region_ca_central_1.generic_service_catalog_id_seq'::regclass);


--
-- Name: rds_catalog id; Type: DEFAULT; Schema: region_ca_central_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_central_1.rds_catalog ALTER COLUMN id SET DEFAULT nextval('region_ca_central_1.rds_catalog_id_seq'::regclass);


--
-- Name: sync_metadata id; Type: DEFAULT; Schema: region_ca_central_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_central_1.sync_metadata ALTER COLUMN id SET DEFAULT nextval('region_ca_central_1.sync_metadata_id_seq'::regclass);


--
-- Name: admin_audit_logs id; Type: DEFAULT; Schema: region_ca_west_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_west_1.admin_audit_logs ALTER COLUMN id SET DEFAULT nextval('region_ca_west_1.admin_audit_logs_id_seq'::regclass);


--
-- Name: admin_users id; Type: DEFAULT; Schema: region_ca_west_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_west_1.admin_users ALTER COLUMN id SET DEFAULT nextval('region_ca_west_1.admin_users_id_seq'::regclass);


--
-- Name: ec2_catalog id; Type: DEFAULT; Schema: region_ca_west_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_west_1.ec2_catalog ALTER COLUMN id SET DEFAULT nextval('region_ca_west_1.ec2_catalog_id_seq'::regclass);


--
-- Name: generic_service_catalog id; Type: DEFAULT; Schema: region_ca_west_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_west_1.generic_service_catalog ALTER COLUMN id SET DEFAULT nextval('region_ca_west_1.generic_service_catalog_id_seq'::regclass);


--
-- Name: rds_catalog id; Type: DEFAULT; Schema: region_ca_west_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_west_1.rds_catalog ALTER COLUMN id SET DEFAULT nextval('region_ca_west_1.rds_catalog_id_seq'::regclass);


--
-- Name: sync_metadata id; Type: DEFAULT; Schema: region_ca_west_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_west_1.sync_metadata ALTER COLUMN id SET DEFAULT nextval('region_ca_west_1.sync_metadata_id_seq'::regclass);


--
-- Name: admin_audit_logs id; Type: DEFAULT; Schema: region_mx_central_1; Owner: postgres
--

ALTER TABLE ONLY region_mx_central_1.admin_audit_logs ALTER COLUMN id SET DEFAULT nextval('region_mx_central_1.admin_audit_logs_id_seq'::regclass);


--
-- Name: admin_users id; Type: DEFAULT; Schema: region_mx_central_1; Owner: postgres
--

ALTER TABLE ONLY region_mx_central_1.admin_users ALTER COLUMN id SET DEFAULT nextval('region_mx_central_1.admin_users_id_seq'::regclass);


--
-- Name: ec2_catalog id; Type: DEFAULT; Schema: region_mx_central_1; Owner: postgres
--

ALTER TABLE ONLY region_mx_central_1.ec2_catalog ALTER COLUMN id SET DEFAULT nextval('region_mx_central_1.ec2_catalog_id_seq'::regclass);


--
-- Name: generic_service_catalog id; Type: DEFAULT; Schema: region_mx_central_1; Owner: postgres
--

ALTER TABLE ONLY region_mx_central_1.generic_service_catalog ALTER COLUMN id SET DEFAULT nextval('region_mx_central_1.generic_service_catalog_id_seq'::regclass);


--
-- Name: rds_catalog id; Type: DEFAULT; Schema: region_mx_central_1; Owner: postgres
--

ALTER TABLE ONLY region_mx_central_1.rds_catalog ALTER COLUMN id SET DEFAULT nextval('region_mx_central_1.rds_catalog_id_seq'::regclass);


--
-- Name: sync_metadata id; Type: DEFAULT; Schema: region_mx_central_1; Owner: postgres
--

ALTER TABLE ONLY region_mx_central_1.sync_metadata ALTER COLUMN id SET DEFAULT nextval('region_mx_central_1.sync_metadata_id_seq'::regclass);


--
-- Name: admin_audit_logs id; Type: DEFAULT; Schema: region_sa_east_1; Owner: postgres
--

ALTER TABLE ONLY region_sa_east_1.admin_audit_logs ALTER COLUMN id SET DEFAULT nextval('region_sa_east_1.admin_audit_logs_id_seq'::regclass);


--
-- Name: admin_users id; Type: DEFAULT; Schema: region_sa_east_1; Owner: postgres
--

ALTER TABLE ONLY region_sa_east_1.admin_users ALTER COLUMN id SET DEFAULT nextval('region_sa_east_1.admin_users_id_seq'::regclass);


--
-- Name: ec2_catalog id; Type: DEFAULT; Schema: region_sa_east_1; Owner: postgres
--

ALTER TABLE ONLY region_sa_east_1.ec2_catalog ALTER COLUMN id SET DEFAULT nextval('region_sa_east_1.ec2_catalog_id_seq'::regclass);


--
-- Name: generic_service_catalog id; Type: DEFAULT; Schema: region_sa_east_1; Owner: postgres
--

ALTER TABLE ONLY region_sa_east_1.generic_service_catalog ALTER COLUMN id SET DEFAULT nextval('region_sa_east_1.generic_service_catalog_id_seq'::regclass);


--
-- Name: rds_catalog id; Type: DEFAULT; Schema: region_sa_east_1; Owner: postgres
--

ALTER TABLE ONLY region_sa_east_1.rds_catalog ALTER COLUMN id SET DEFAULT nextval('region_sa_east_1.rds_catalog_id_seq'::regclass);


--
-- Name: sync_metadata id; Type: DEFAULT; Schema: region_sa_east_1; Owner: postgres
--

ALTER TABLE ONLY region_sa_east_1.sync_metadata ALTER COLUMN id SET DEFAULT nextval('region_sa_east_1.sync_metadata_id_seq'::regclass);


--
-- Name: admin_audit_logs id; Type: DEFAULT; Schema: region_us_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_east_1.admin_audit_logs ALTER COLUMN id SET DEFAULT nextval('region_us_east_1.admin_audit_logs_id_seq'::regclass);


--
-- Name: admin_users id; Type: DEFAULT; Schema: region_us_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_east_1.admin_users ALTER COLUMN id SET DEFAULT nextval('region_us_east_1.admin_users_id_seq'::regclass);


--
-- Name: ec2_catalog id; Type: DEFAULT; Schema: region_us_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_east_1.ec2_catalog ALTER COLUMN id SET DEFAULT nextval('region_us_east_1.ec2_catalog_id_seq'::regclass);


--
-- Name: generic_service_catalog id; Type: DEFAULT; Schema: region_us_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_east_1.generic_service_catalog ALTER COLUMN id SET DEFAULT nextval('region_us_east_1.generic_service_catalog_id_seq'::regclass);


--
-- Name: rds_catalog id; Type: DEFAULT; Schema: region_us_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_east_1.rds_catalog ALTER COLUMN id SET DEFAULT nextval('region_us_east_1.rds_catalog_id_seq'::regclass);


--
-- Name: sync_metadata id; Type: DEFAULT; Schema: region_us_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_east_1.sync_metadata ALTER COLUMN id SET DEFAULT nextval('region_us_east_1.sync_metadata_id_seq'::regclass);


--
-- Name: admin_audit_logs id; Type: DEFAULT; Schema: region_us_east_2; Owner: postgres
--

ALTER TABLE ONLY region_us_east_2.admin_audit_logs ALTER COLUMN id SET DEFAULT nextval('region_us_east_2.admin_audit_logs_id_seq'::regclass);


--
-- Name: admin_users id; Type: DEFAULT; Schema: region_us_east_2; Owner: postgres
--

ALTER TABLE ONLY region_us_east_2.admin_users ALTER COLUMN id SET DEFAULT nextval('region_us_east_2.admin_users_id_seq'::regclass);


--
-- Name: ec2_catalog id; Type: DEFAULT; Schema: region_us_east_2; Owner: postgres
--

ALTER TABLE ONLY region_us_east_2.ec2_catalog ALTER COLUMN id SET DEFAULT nextval('region_us_east_2.ec2_catalog_id_seq'::regclass);


--
-- Name: generic_service_catalog id; Type: DEFAULT; Schema: region_us_east_2; Owner: postgres
--

ALTER TABLE ONLY region_us_east_2.generic_service_catalog ALTER COLUMN id SET DEFAULT nextval('region_us_east_2.generic_service_catalog_id_seq'::regclass);


--
-- Name: rds_catalog id; Type: DEFAULT; Schema: region_us_east_2; Owner: postgres
--

ALTER TABLE ONLY region_us_east_2.rds_catalog ALTER COLUMN id SET DEFAULT nextval('region_us_east_2.rds_catalog_id_seq'::regclass);


--
-- Name: sync_metadata id; Type: DEFAULT; Schema: region_us_east_2; Owner: postgres
--

ALTER TABLE ONLY region_us_east_2.sync_metadata ALTER COLUMN id SET DEFAULT nextval('region_us_east_2.sync_metadata_id_seq'::regclass);


--
-- Name: admin_audit_logs id; Type: DEFAULT; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_east_1.admin_audit_logs ALTER COLUMN id SET DEFAULT nextval('region_us_gov_east_1.admin_audit_logs_id_seq'::regclass);


--
-- Name: admin_users id; Type: DEFAULT; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_east_1.admin_users ALTER COLUMN id SET DEFAULT nextval('region_us_gov_east_1.admin_users_id_seq'::regclass);


--
-- Name: ec2_catalog id; Type: DEFAULT; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_east_1.ec2_catalog ALTER COLUMN id SET DEFAULT nextval('region_us_gov_east_1.ec2_catalog_id_seq'::regclass);


--
-- Name: generic_service_catalog id; Type: DEFAULT; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_east_1.generic_service_catalog ALTER COLUMN id SET DEFAULT nextval('region_us_gov_east_1.generic_service_catalog_id_seq'::regclass);


--
-- Name: rds_catalog id; Type: DEFAULT; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_east_1.rds_catalog ALTER COLUMN id SET DEFAULT nextval('region_us_gov_east_1.rds_catalog_id_seq'::regclass);


--
-- Name: sync_metadata id; Type: DEFAULT; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_east_1.sync_metadata ALTER COLUMN id SET DEFAULT nextval('region_us_gov_east_1.sync_metadata_id_seq'::regclass);


--
-- Name: admin_audit_logs id; Type: DEFAULT; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_west_1.admin_audit_logs ALTER COLUMN id SET DEFAULT nextval('region_us_gov_west_1.admin_audit_logs_id_seq'::regclass);


--
-- Name: admin_users id; Type: DEFAULT; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_west_1.admin_users ALTER COLUMN id SET DEFAULT nextval('region_us_gov_west_1.admin_users_id_seq'::regclass);


--
-- Name: ec2_catalog id; Type: DEFAULT; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_west_1.ec2_catalog ALTER COLUMN id SET DEFAULT nextval('region_us_gov_west_1.ec2_catalog_id_seq'::regclass);


--
-- Name: generic_service_catalog id; Type: DEFAULT; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_west_1.generic_service_catalog ALTER COLUMN id SET DEFAULT nextval('region_us_gov_west_1.generic_service_catalog_id_seq'::regclass);


--
-- Name: rds_catalog id; Type: DEFAULT; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_west_1.rds_catalog ALTER COLUMN id SET DEFAULT nextval('region_us_gov_west_1.rds_catalog_id_seq'::regclass);


--
-- Name: sync_metadata id; Type: DEFAULT; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_west_1.sync_metadata ALTER COLUMN id SET DEFAULT nextval('region_us_gov_west_1.sync_metadata_id_seq'::regclass);


--
-- Name: admin_audit_logs id; Type: DEFAULT; Schema: region_us_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_west_1.admin_audit_logs ALTER COLUMN id SET DEFAULT nextval('region_us_west_1.admin_audit_logs_id_seq'::regclass);


--
-- Name: admin_users id; Type: DEFAULT; Schema: region_us_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_west_1.admin_users ALTER COLUMN id SET DEFAULT nextval('region_us_west_1.admin_users_id_seq'::regclass);


--
-- Name: ec2_catalog id; Type: DEFAULT; Schema: region_us_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_west_1.ec2_catalog ALTER COLUMN id SET DEFAULT nextval('region_us_west_1.ec2_catalog_id_seq'::regclass);


--
-- Name: generic_service_catalog id; Type: DEFAULT; Schema: region_us_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_west_1.generic_service_catalog ALTER COLUMN id SET DEFAULT nextval('region_us_west_1.generic_service_catalog_id_seq'::regclass);


--
-- Name: rds_catalog id; Type: DEFAULT; Schema: region_us_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_west_1.rds_catalog ALTER COLUMN id SET DEFAULT nextval('region_us_west_1.rds_catalog_id_seq'::regclass);


--
-- Name: sync_metadata id; Type: DEFAULT; Schema: region_us_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_west_1.sync_metadata ALTER COLUMN id SET DEFAULT nextval('region_us_west_1.sync_metadata_id_seq'::regclass);


--
-- Name: admin_audit_logs id; Type: DEFAULT; Schema: region_us_west_2; Owner: postgres
--

ALTER TABLE ONLY region_us_west_2.admin_audit_logs ALTER COLUMN id SET DEFAULT nextval('region_us_west_2.admin_audit_logs_id_seq'::regclass);


--
-- Name: admin_users id; Type: DEFAULT; Schema: region_us_west_2; Owner: postgres
--

ALTER TABLE ONLY region_us_west_2.admin_users ALTER COLUMN id SET DEFAULT nextval('region_us_west_2.admin_users_id_seq'::regclass);


--
-- Name: ec2_catalog id; Type: DEFAULT; Schema: region_us_west_2; Owner: postgres
--

ALTER TABLE ONLY region_us_west_2.ec2_catalog ALTER COLUMN id SET DEFAULT nextval('region_us_west_2.ec2_catalog_id_seq'::regclass);


--
-- Name: generic_service_catalog id; Type: DEFAULT; Schema: region_us_west_2; Owner: postgres
--

ALTER TABLE ONLY region_us_west_2.generic_service_catalog ALTER COLUMN id SET DEFAULT nextval('region_us_west_2.generic_service_catalog_id_seq'::regclass);


--
-- Name: rds_catalog id; Type: DEFAULT; Schema: region_us_west_2; Owner: postgres
--

ALTER TABLE ONLY region_us_west_2.rds_catalog ALTER COLUMN id SET DEFAULT nextval('region_us_west_2.rds_catalog_id_seq'::regclass);


--
-- Name: sync_metadata id; Type: DEFAULT; Schema: region_us_west_2; Owner: postgres
--

ALTER TABLE ONLY region_us_west_2.sync_metadata ALTER COLUMN id SET DEFAULT nextval('region_us_west_2.sync_metadata_id_seq'::regclass);


--
-- Name: sc_admin_audit_logs id; Type: DEFAULT; Schema: source_connection; Owner: postgres
--

ALTER TABLE ONLY source_connection.sc_admin_audit_logs ALTER COLUMN id SET DEFAULT nextval('source_connection.sc_admin_audit_logs_id_seq'::regclass);


--
-- Name: sc_admin_users id; Type: DEFAULT; Schema: source_connection; Owner: postgres
--

ALTER TABLE ONLY source_connection.sc_admin_users ALTER COLUMN id SET DEFAULT nextval('source_connection.sc_admin_users_id_seq'::regclass);


--
-- Data for Name: admin_audit_logs; Type: TABLE DATA; Schema: admin_security; Owner: postgres
--

COPY admin_security.admin_audit_logs (id, username, action, target_resource, status, ip_address, details, created_at) FROM stdin;
\.


--
-- Data for Name: admin_users; Type: TABLE DATA; Schema: admin_security; Owner: postgres
--

COPY admin_security.admin_users (id, username, email, password_hash, role, is_active, failed_attempts, locked_until, last_login_at, created_at) FROM stdin;
1	admin	admin@aetherops.cloud	$2b$12$QkJGuI3WWo5Idg.1a1FL8uW2Quu3lFj6H3iEjmU/qShJGIFkWIgba	SUPER_ADMIN	t	0	\N	\N	2026-11-09 12:04:38.032931
\.


--
-- Data for Name: ec2_catalog; Type: TABLE DATA; Schema: admin_security; Owner: postgres
--

COPY admin_security.ec2_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, network_performance, category) FROM stdin;
\.


--
-- Data for Name: generic_service_catalog; Type: TABLE DATA; Schema: admin_security; Owner: postgres
--

COPY admin_security.generic_service_catalog (id, service, instance_type, vcpus, ram_gb, price_per_hour, unit, category, region, details) FROM stdin;
\.


--
-- Data for Name: rds_catalog; Type: TABLE DATA; Schema: admin_security; Owner: postgres
--

COPY admin_security.rds_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, category) FROM stdin;
\.


--
-- Data for Name: requirement_projects; Type: TABLE DATA; Schema: admin_security; Owner: postgres
--

COPY admin_security.requirement_projects (id, project_name, description, stream, target_region, traffic_scale, reliability, security_need, data_storage_gb, monthly_budget, tech_stack, operations, monitoring, architecture_tier, estimated_monthly_cost, cost_breakdown, service_rationales, cost_optimizations, profile_output, status, dispatched_to_m2, m2_graph_summary, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: sync_metadata; Type: TABLE DATA; Schema: admin_security; Owner: postgres
--

COPY admin_security.sync_metadata (id, region_code, last_sync_timestamp, status, records_synced, ec2_count, rds_count, generic_count, duration_ms, error_message) FROM stdin;
\.


--
-- Data for Name: architecture_versions; Type: TABLE DATA; Schema: architecture; Owner: postgres
--

COPY architecture.architecture_versions (version_id, project_id, environment_id, environment_tier, target_region, nodes, edges, status, is_approved, approval_id, approved_by, approved_at, tenant_id, user_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: studio_sessions; Type: TABLE DATA; Schema: architecture; Owner: postgres
--

COPY architecture.studio_sessions (session_id, tenant_id, user_id, project_id, version_id, state_data, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: generated_iac_bundles; Type: TABLE DATA; Schema: iac; Owner: postgres
--

COPY iac.generated_iac_bundles (terraform_version_id, architecture_version_id, project_name, aws_region, iac_tool, checksum, files_json, tenant_id, user_id, created_at) FROM stdin;
tf-dfdb6a2a97d0	draft	Clock	us-east-1	terraform	4487234f2d511d0874f19a482ff4adf4c49bc858d0444a8935072edee1d02b86	[{"filename": "provider.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n\\nprovider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"Clock\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Production\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"Clock\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t4g.micro (2 vCPU, 1 GB RAM)\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n", "language": "hcl"}, {"filename": "main.tf", "content": "# VPC & Networking (Multi-Tier Production)\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = {\\n    Name = \\"${var.project_name}-vpc\\"\\n  }\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n}\\n\\nresource \\"aws_subnet\\" \\"public_b\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.2.0/24\\"\\n  availability_zone       = \\"${var.aws_region}b\\"\\n  map_public_ip_on_launch = true\\n}\\n\\n# Security Groups\\nresource \\"aws_security_group\\" \\"alb_sg\\" {\\n  name        = \\"${var.project_name}-alb-sg\\"\\n  description = \\"Allow inbound HTTP/HTTPS traffic\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n}\\n\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 12:21:59.514768
tf-2d18775e7091	draft	Clock	us-east-1	terraform	4487234f2d511d0874f19a482ff4adf4c49bc858d0444a8935072edee1d02b86	[{"filename": "provider.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n\\nprovider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"Clock\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Production\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"Clock\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t4g.micro (2 vCPU, 1 GB RAM)\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n", "language": "hcl"}, {"filename": "main.tf", "content": "# VPC & Networking (Multi-Tier Production)\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = {\\n    Name = \\"${var.project_name}-vpc\\"\\n  }\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n}\\n\\nresource \\"aws_subnet\\" \\"public_b\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.2.0/24\\"\\n  availability_zone       = \\"${var.aws_region}b\\"\\n  map_public_ip_on_launch = true\\n}\\n\\n# Security Groups\\nresource \\"aws_security_group\\" \\"alb_sg\\" {\\n  name        = \\"${var.project_name}-alb-sg\\"\\n  description = \\"Allow inbound HTTP/HTTPS traffic\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n}\\n\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 12:23:34.890509
tf-bfb9c69fb941	draft	aether-cloud	us-east-1	terraform	d9f4c748c2f20284d95df1ae5c82f9a364de177aee5c541cdf5db0d4a40091fb	[{"filename": "provider.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n\\nprovider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Production\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t4g.micro (2 vCPU, 1 GB RAM)\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n\\nvariable \\"db_instance_class\\" {\\n  type        = string\\n  default     = \\"Amazon RDS PostgreSQL\\"\\n  description = \\"RDS instance class\\"\\n}\\n", "language": "hcl"}, {"filename": "main.tf", "content": "# VPC & Networking (Multi-Tier Production)\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = {\\n    Name = \\"${var.project_name}-vpc\\"\\n  }\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n}\\n\\nresource \\"aws_subnet\\" \\"public_b\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.2.0/24\\"\\n  availability_zone       = \\"${var.aws_region}b\\"\\n  map_public_ip_on_launch = true\\n}\\n\\nresource \\"aws_subnet\\" \\"private_a\\" {\\n  vpc_id            = aws_vpc.main.id\\n  cidr_block        = \\"10.0.10.0/24\\"\\n  availability_zone = \\"${var.aws_region}a\\"\\n}\\n\\nresource \\"aws_subnet\\" \\"private_b\\" {\\n  vpc_id            = aws_vpc.main.id\\n  cidr_block        = \\"10.0.20.0/24\\"\\n  availability_zone = \\"${var.aws_region}b\\"\\n}\\n\\n# Security Groups\\nresource \\"aws_security_group\\" \\"alb_sg\\" {\\n  name        = \\"${var.project_name}-alb-sg\\"\\n  description = \\"Allow inbound HTTP/HTTPS traffic\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n}\\n\\nresource \\"aws_db_subnet_group\\" \\"rds\\" {\\n  name       = \\"${var.project_name}-db-subnet-group\\"\\n  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]\\n}\\n\\nresource \\"aws_db_instance\\" \\"main\\" {\\n  identifier             = \\"${var.project_name}-db\\"\\n  allocated_storage      = 20\\n  max_allocated_storage  = 40\\n  storage_type           = \\"gp3\\"\\n  engine                 = \\"postgres\\"\\n  engine_version         = \\"15.4\\"\\n  instance_class         = var.db_instance_class\\n  multi_az               = true\\n  db_subnet_group_name   = aws_db_subnet_group.rds.name\\n  skip_final_snapshot    = true\\n  storage_encrypted      = true\\n  kms_key_id             = null\\n}\\n\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\noutput \\"rds_endpoint\\" {\\n  description = \\"Primary RDS Connection Endpoint\\"\\n  value       = aws_db_instance.main.endpoint\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 17:08:42.024478
tf-7cfef312c978	draft	aether-cloud	us-east-1	terraform	d9f4c748c2f20284d95df1ae5c82f9a364de177aee5c541cdf5db0d4a40091fb	[{"filename": "provider.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n\\nprovider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Production\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t4g.micro (2 vCPU, 1 GB RAM)\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n\\nvariable \\"db_instance_class\\" {\\n  type        = string\\n  default     = \\"Amazon RDS PostgreSQL\\"\\n  description = \\"RDS instance class\\"\\n}\\n", "language": "hcl"}, {"filename": "main.tf", "content": "# VPC & Networking (Multi-Tier Production)\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = {\\n    Name = \\"${var.project_name}-vpc\\"\\n  }\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n}\\n\\nresource \\"aws_subnet\\" \\"public_b\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.2.0/24\\"\\n  availability_zone       = \\"${var.aws_region}b\\"\\n  map_public_ip_on_launch = true\\n}\\n\\nresource \\"aws_subnet\\" \\"private_a\\" {\\n  vpc_id            = aws_vpc.main.id\\n  cidr_block        = \\"10.0.10.0/24\\"\\n  availability_zone = \\"${var.aws_region}a\\"\\n}\\n\\nresource \\"aws_subnet\\" \\"private_b\\" {\\n  vpc_id            = aws_vpc.main.id\\n  cidr_block        = \\"10.0.20.0/24\\"\\n  availability_zone = \\"${var.aws_region}b\\"\\n}\\n\\n# Security Groups\\nresource \\"aws_security_group\\" \\"alb_sg\\" {\\n  name        = \\"${var.project_name}-alb-sg\\"\\n  description = \\"Allow inbound HTTP/HTTPS traffic\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n}\\n\\nresource \\"aws_db_subnet_group\\" \\"rds\\" {\\n  name       = \\"${var.project_name}-db-subnet-group\\"\\n  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]\\n}\\n\\nresource \\"aws_db_instance\\" \\"main\\" {\\n  identifier             = \\"${var.project_name}-db\\"\\n  allocated_storage      = 20\\n  max_allocated_storage  = 40\\n  storage_type           = \\"gp3\\"\\n  engine                 = \\"postgres\\"\\n  engine_version         = \\"15.4\\"\\n  instance_class         = var.db_instance_class\\n  multi_az               = true\\n  db_subnet_group_name   = aws_db_subnet_group.rds.name\\n  skip_final_snapshot    = true\\n  storage_encrypted      = true\\n  kms_key_id             = null\\n}\\n\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\noutput \\"rds_endpoint\\" {\\n  description = \\"Primary RDS Connection Endpoint\\"\\n  value       = aws_db_instance.main.endpoint\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 17:19:57.201287
tf-ced6836f15cc	draft	aether-cloud	us-east-1	terraform	d9f4c748c2f20284d95df1ae5c82f9a364de177aee5c541cdf5db0d4a40091fb	[{"filename": "provider.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n\\nprovider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Production\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t4g.micro (2 vCPU, 1 GB RAM)\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n\\nvariable \\"db_instance_class\\" {\\n  type        = string\\n  default     = \\"Amazon RDS PostgreSQL\\"\\n  description = \\"RDS instance class\\"\\n}\\n", "language": "hcl"}, {"filename": "main.tf", "content": "# VPC & Networking (Multi-Tier Production)\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = {\\n    Name = \\"${var.project_name}-vpc\\"\\n  }\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n}\\n\\nresource \\"aws_subnet\\" \\"public_b\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.2.0/24\\"\\n  availability_zone       = \\"${var.aws_region}b\\"\\n  map_public_ip_on_launch = true\\n}\\n\\nresource \\"aws_subnet\\" \\"private_a\\" {\\n  vpc_id            = aws_vpc.main.id\\n  cidr_block        = \\"10.0.10.0/24\\"\\n  availability_zone = \\"${var.aws_region}a\\"\\n}\\n\\nresource \\"aws_subnet\\" \\"private_b\\" {\\n  vpc_id            = aws_vpc.main.id\\n  cidr_block        = \\"10.0.20.0/24\\"\\n  availability_zone = \\"${var.aws_region}b\\"\\n}\\n\\n# Security Groups\\nresource \\"aws_security_group\\" \\"alb_sg\\" {\\n  name        = \\"${var.project_name}-alb-sg\\"\\n  description = \\"Allow inbound HTTP/HTTPS traffic\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n}\\n\\nresource \\"aws_db_subnet_group\\" \\"rds\\" {\\n  name       = \\"${var.project_name}-db-subnet-group\\"\\n  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]\\n}\\n\\nresource \\"aws_db_instance\\" \\"main\\" {\\n  identifier             = \\"${var.project_name}-db\\"\\n  allocated_storage      = 20\\n  max_allocated_storage  = 40\\n  storage_type           = \\"gp3\\"\\n  engine                 = \\"postgres\\"\\n  engine_version         = \\"15.4\\"\\n  instance_class         = var.db_instance_class\\n  multi_az               = true\\n  db_subnet_group_name   = aws_db_subnet_group.rds.name\\n  skip_final_snapshot    = true\\n  storage_encrypted      = true\\n  kms_key_id             = null\\n}\\n\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\noutput \\"rds_endpoint\\" {\\n  description = \\"Primary RDS Connection Endpoint\\"\\n  value       = aws_db_instance.main.endpoint\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 17:31:25.362639
tf-97cf0df16842	draft	aether-cloud	us-east-1	terraform	e705758c628c8205879d3e9477374511b939f0185ae15be39b411b49d55317c6	[{"filename": "versions.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "provider.tf", "content": "provider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Production\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t4g.micro (2 vCPU, 1 GB RAM)\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n\\nvariable \\"db_instance_class\\" {\\n  type        = string\\n  default     = \\"Amazon RDS PostgreSQL\\"\\n  description = \\"RDS instance class\\"\\n}\\n", "language": "hcl"}, {"filename": "locals.tf", "content": "locals {\\n  name_prefix = var.project_name\\n  common_tags = {\\n    Project     = var.project_name\\n    ManagedBy   = \\"AetherOps\\"\\n    ArchitectureVersion = \\"draft\\"\\n  }\\n}\\n", "language": "hcl"}, {"filename": "network.tf", "content": "# VPC & Networking\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-vpc\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_internet_gateway\\" \\"igw\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-igw\\"\\n  })\\n}\\n\\nresource \\"aws_route_table\\" \\"public\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  route {\\n    cidr_block = \\"0.0.0.0/0\\"\\n    gateway_id = aws_internet_gateway.igw.id\\n  }\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-rt\\"\\n  })\\n}\\n\\nresource \\"aws_route_table_association\\" \\"public_a\\" {\\n  subnet_id      = aws_subnet.public_a.id\\n  route_table_id = aws_route_table.public.id\\n}\\n\\nresource \\"aws_subnet\\" \\"public_b\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.2.0/24\\"\\n  availability_zone       = \\"${var.aws_region}b\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-b\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"private_a\\" {\\n  vpc_id            = aws_vpc.main.id\\n  cidr_block        = \\"10.0.10.0/24\\"\\n  availability_zone = \\"${var.aws_region}a\\"\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-private-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"private_b\\" {\\n  vpc_id            = aws_vpc.main.id\\n  cidr_block        = \\"10.0.20.0/24\\"\\n  availability_zone = \\"${var.aws_region}b\\"\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-private-subnet-b\\"\\n  })\\n}\\n", "language": "hcl"}, {"filename": "security.tf", "content": "# Security Groups & Policies\\nresource \\"aws_security_group\\" \\"app_sg\\" {\\n  name        = \\"${local.name_prefix}-app-sg\\"\\n  description = \\"AetherOps security group for application workload\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 8080\\n    to_port     = 8080\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  tags = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "compute.tf", "content": "# Compute Resources (EC2)\\nresource \\"aws_instance\\" \\"app\\" {\\n  ami                    = data.aws_ami.ubuntu.id\\n  instance_type          = var.instance_type\\n  subnet_id              = aws_subnet.public_a.id\\n  vpc_security_group_ids = [aws_security_group.app_sg.id]\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-instance\\"\\n  })\\n}\\n\\ndata \\"aws_ami\\" \\"ubuntu\\" {\\n  most_recent = true\\n  filter {\\n    name   = \\"name\\"\\n    values = [\\"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*\\"]\\n  }\\n  filter {\\n    name   = \\"virtualization-type\\"\\n    values = [\\"hvm\\"]\\n  }\\n  owners = [\\"099720109477\\"]\\n}\\n", "language": "hcl"}, {"filename": "storage.tf", "content": "\\nresource \\"aws_db_subnet_group\\" \\"rds\\" {\\n  name       = \\"${local.name_prefix}-db-subnet-group\\"\\n  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]\\n  tags       = local.common_tags\\n}\\n\\nresource \\"aws_db_instance\\" \\"main\\" {\\n  identifier             = \\"${local.name_prefix}-db\\"\\n  allocated_storage      = 20\\n  max_allocated_storage  = 40\\n  storage_type           = \\"gp3\\"\\n  engine                 = \\"postgres\\"\\n  engine_version         = \\"15.4\\"\\n  instance_class         = var.db_instance_class\\n  multi_az               = false\\n  db_subnet_group_name   = aws_db_subnet_group.rds.name\\n  skip_final_snapshot    = true\\n  storage_encrypted      = true\\n  tags                   = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "main.tf", "content": "# Main Architecture Integration & Security Services\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n\\noutput \\"instance_ip\\" {\\n  description = \\"Public IP of the application instance\\"\\n  value       = aws_instance.app.public_ip\\n}\\n\\noutput \\"rds_endpoint\\" {\\n  description = \\"Primary RDS Connection Endpoint\\"\\n  value       = aws_db_instance.main.endpoint\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 17:34:03.883943
tf-633321ec0647	draft	aether-cloud	us-east-1	terraform	e705758c628c8205879d3e9477374511b939f0185ae15be39b411b49d55317c6	[{"filename": "versions.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "provider.tf", "content": "provider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Production\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t4g.micro (2 vCPU, 1 GB RAM)\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n\\nvariable \\"db_instance_class\\" {\\n  type        = string\\n  default     = \\"Amazon RDS PostgreSQL\\"\\n  description = \\"RDS instance class\\"\\n}\\n", "language": "hcl"}, {"filename": "locals.tf", "content": "locals {\\n  name_prefix = var.project_name\\n  common_tags = {\\n    Project     = var.project_name\\n    ManagedBy   = \\"AetherOps\\"\\n    ArchitectureVersion = \\"draft\\"\\n  }\\n}\\n", "language": "hcl"}, {"filename": "network.tf", "content": "# VPC & Networking\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-vpc\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_internet_gateway\\" \\"igw\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-igw\\"\\n  })\\n}\\n\\nresource \\"aws_route_table\\" \\"public\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  route {\\n    cidr_block = \\"0.0.0.0/0\\"\\n    gateway_id = aws_internet_gateway.igw.id\\n  }\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-rt\\"\\n  })\\n}\\n\\nresource \\"aws_route_table_association\\" \\"public_a\\" {\\n  subnet_id      = aws_subnet.public_a.id\\n  route_table_id = aws_route_table.public.id\\n}\\n\\nresource \\"aws_subnet\\" \\"public_b\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.2.0/24\\"\\n  availability_zone       = \\"${var.aws_region}b\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-b\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"private_a\\" {\\n  vpc_id            = aws_vpc.main.id\\n  cidr_block        = \\"10.0.10.0/24\\"\\n  availability_zone = \\"${var.aws_region}a\\"\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-private-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"private_b\\" {\\n  vpc_id            = aws_vpc.main.id\\n  cidr_block        = \\"10.0.20.0/24\\"\\n  availability_zone = \\"${var.aws_region}b\\"\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-private-subnet-b\\"\\n  })\\n}\\n", "language": "hcl"}, {"filename": "security.tf", "content": "# Security Groups & Policies\\nresource \\"aws_security_group\\" \\"app_sg\\" {\\n  name        = \\"${local.name_prefix}-app-sg\\"\\n  description = \\"AetherOps security group for application workload\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 8080\\n    to_port     = 8080\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  tags = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "compute.tf", "content": "# Compute Resources (EC2)\\nresource \\"aws_instance\\" \\"app\\" {\\n  ami                    = data.aws_ami.ubuntu.id\\n  instance_type          = var.instance_type\\n  subnet_id              = aws_subnet.public_a.id\\n  vpc_security_group_ids = [aws_security_group.app_sg.id]\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-instance\\"\\n  })\\n}\\n\\ndata \\"aws_ami\\" \\"ubuntu\\" {\\n  most_recent = true\\n  filter {\\n    name   = \\"name\\"\\n    values = [\\"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*\\"]\\n  }\\n  filter {\\n    name   = \\"virtualization-type\\"\\n    values = [\\"hvm\\"]\\n  }\\n  owners = [\\"099720109477\\"]\\n}\\n", "language": "hcl"}, {"filename": "storage.tf", "content": "\\nresource \\"aws_db_subnet_group\\" \\"rds\\" {\\n  name       = \\"${local.name_prefix}-db-subnet-group\\"\\n  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]\\n  tags       = local.common_tags\\n}\\n\\nresource \\"aws_db_instance\\" \\"main\\" {\\n  identifier             = \\"${local.name_prefix}-db\\"\\n  allocated_storage      = 20\\n  max_allocated_storage  = 40\\n  storage_type           = \\"gp3\\"\\n  engine                 = \\"postgres\\"\\n  engine_version         = \\"15.4\\"\\n  instance_class         = var.db_instance_class\\n  multi_az               = false\\n  db_subnet_group_name   = aws_db_subnet_group.rds.name\\n  skip_final_snapshot    = true\\n  storage_encrypted      = true\\n  tags                   = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "main.tf", "content": "# Main Architecture Integration & Security Services\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n\\noutput \\"instance_ip\\" {\\n  description = \\"Public IP of the application instance\\"\\n  value       = aws_instance.app.public_ip\\n}\\n\\noutput \\"rds_endpoint\\" {\\n  description = \\"Primary RDS Connection Endpoint\\"\\n  value       = aws_db_instance.main.endpoint\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 17:35:00.587256
tf-b031e1d00306	draft	aether-cloud	us-east-1	terraform	e705758c628c8205879d3e9477374511b939f0185ae15be39b411b49d55317c6	[{"filename": "versions.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "provider.tf", "content": "provider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Production\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t4g.micro (2 vCPU, 1 GB RAM)\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n\\nvariable \\"db_instance_class\\" {\\n  type        = string\\n  default     = \\"Amazon RDS PostgreSQL\\"\\n  description = \\"RDS instance class\\"\\n}\\n", "language": "hcl"}, {"filename": "locals.tf", "content": "locals {\\n  name_prefix = var.project_name\\n  common_tags = {\\n    Project     = var.project_name\\n    ManagedBy   = \\"AetherOps\\"\\n    ArchitectureVersion = \\"draft\\"\\n  }\\n}\\n", "language": "hcl"}, {"filename": "network.tf", "content": "# VPC & Networking\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-vpc\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_internet_gateway\\" \\"igw\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-igw\\"\\n  })\\n}\\n\\nresource \\"aws_route_table\\" \\"public\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  route {\\n    cidr_block = \\"0.0.0.0/0\\"\\n    gateway_id = aws_internet_gateway.igw.id\\n  }\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-rt\\"\\n  })\\n}\\n\\nresource \\"aws_route_table_association\\" \\"public_a\\" {\\n  subnet_id      = aws_subnet.public_a.id\\n  route_table_id = aws_route_table.public.id\\n}\\n\\nresource \\"aws_subnet\\" \\"public_b\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.2.0/24\\"\\n  availability_zone       = \\"${var.aws_region}b\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-b\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"private_a\\" {\\n  vpc_id            = aws_vpc.main.id\\n  cidr_block        = \\"10.0.10.0/24\\"\\n  availability_zone = \\"${var.aws_region}a\\"\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-private-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"private_b\\" {\\n  vpc_id            = aws_vpc.main.id\\n  cidr_block        = \\"10.0.20.0/24\\"\\n  availability_zone = \\"${var.aws_region}b\\"\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-private-subnet-b\\"\\n  })\\n}\\n", "language": "hcl"}, {"filename": "security.tf", "content": "# Security Groups & Policies\\nresource \\"aws_security_group\\" \\"app_sg\\" {\\n  name        = \\"${local.name_prefix}-app-sg\\"\\n  description = \\"AetherOps security group for application workload\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 8080\\n    to_port     = 8080\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  tags = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "compute.tf", "content": "# Compute Resources (EC2)\\nresource \\"aws_instance\\" \\"app\\" {\\n  ami                    = data.aws_ami.ubuntu.id\\n  instance_type          = var.instance_type\\n  subnet_id              = aws_subnet.public_a.id\\n  vpc_security_group_ids = [aws_security_group.app_sg.id]\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-instance\\"\\n  })\\n}\\n\\ndata \\"aws_ami\\" \\"ubuntu\\" {\\n  most_recent = true\\n  filter {\\n    name   = \\"name\\"\\n    values = [\\"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*\\"]\\n  }\\n  filter {\\n    name   = \\"virtualization-type\\"\\n    values = [\\"hvm\\"]\\n  }\\n  owners = [\\"099720109477\\"]\\n}\\n", "language": "hcl"}, {"filename": "storage.tf", "content": "\\nresource \\"aws_db_subnet_group\\" \\"rds\\" {\\n  name       = \\"${local.name_prefix}-db-subnet-group\\"\\n  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]\\n  tags       = local.common_tags\\n}\\n\\nresource \\"aws_db_instance\\" \\"main\\" {\\n  identifier             = \\"${local.name_prefix}-db\\"\\n  allocated_storage      = 20\\n  max_allocated_storage  = 40\\n  storage_type           = \\"gp3\\"\\n  engine                 = \\"postgres\\"\\n  engine_version         = \\"15.4\\"\\n  instance_class         = var.db_instance_class\\n  multi_az               = false\\n  db_subnet_group_name   = aws_db_subnet_group.rds.name\\n  skip_final_snapshot    = true\\n  storage_encrypted      = true\\n  tags                   = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "main.tf", "content": "# Main Architecture Integration & Security Services\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n\\noutput \\"instance_ip\\" {\\n  description = \\"Public IP of the application instance\\"\\n  value       = aws_instance.app.public_ip\\n}\\n\\noutput \\"rds_endpoint\\" {\\n  description = \\"Primary RDS Connection Endpoint\\"\\n  value       = aws_db_instance.main.endpoint\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 17:35:01.789969
tf-014858fbf007	draft	aether-cloud	us-east-1	terraform	567b6b34b3013fab876f931faafca3c6c29c9ce5835515ea67018047ae02e369	[{"filename": "versions.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "provider.tf", "content": "provider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Development\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t4g.micro (2 vCPU, 1 GB RAM)\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n\\nvariable \\"db_instance_class\\" {\\n  type        = string\\n  default     = \\"Amazon RDS PostgreSQL\\"\\n  description = \\"RDS instance class\\"\\n}\\n", "language": "hcl"}, {"filename": "locals.tf", "content": "locals {\\n  name_prefix = var.project_name\\n  common_tags = {\\n    Project     = var.project_name\\n    ManagedBy   = \\"AetherOps\\"\\n    ArchitectureVersion = \\"draft\\"\\n  }\\n}\\n", "language": "hcl"}, {"filename": "network.tf", "content": "# VPC & Networking\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-vpc\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_internet_gateway\\" \\"igw\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-igw\\"\\n  })\\n}\\n\\nresource \\"aws_route_table\\" \\"public\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  route {\\n    cidr_block = \\"0.0.0.0/0\\"\\n    gateway_id = aws_internet_gateway.igw.id\\n  }\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-rt\\"\\n  })\\n}\\n\\nresource \\"aws_route_table_association\\" \\"public_a\\" {\\n  subnet_id      = aws_subnet.public_a.id\\n  route_table_id = aws_route_table.public.id\\n}\\n\\nresource \\"aws_subnet\\" \\"public_b\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.2.0/24\\"\\n  availability_zone       = \\"${var.aws_region}b\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-b\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"private_a\\" {\\n  vpc_id            = aws_vpc.main.id\\n  cidr_block        = \\"10.0.10.0/24\\"\\n  availability_zone = \\"${var.aws_region}a\\"\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-private-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"private_b\\" {\\n  vpc_id            = aws_vpc.main.id\\n  cidr_block        = \\"10.0.20.0/24\\"\\n  availability_zone = \\"${var.aws_region}b\\"\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-private-subnet-b\\"\\n  })\\n}\\n", "language": "hcl"}, {"filename": "security.tf", "content": "# Security Groups & Policies\\nresource \\"aws_security_group\\" \\"app_sg\\" {\\n  name        = \\"${local.name_prefix}-app-sg\\"\\n  description = \\"AetherOps security group for application workload\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 8080\\n    to_port     = 8080\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  tags = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "compute.tf", "content": "# Compute Resources (EC2)\\nresource \\"aws_instance\\" \\"app\\" {\\n  ami                    = data.aws_ami.ubuntu.id\\n  instance_type          = var.instance_type\\n  subnet_id              = aws_subnet.public_a.id\\n  vpc_security_group_ids = [aws_security_group.app_sg.id]\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-instance\\"\\n  })\\n}\\n\\ndata \\"aws_ami\\" \\"ubuntu\\" {\\n  most_recent = true\\n  filter {\\n    name   = \\"name\\"\\n    values = [\\"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*\\"]\\n  }\\n  filter {\\n    name   = \\"virtualization-type\\"\\n    values = [\\"hvm\\"]\\n  }\\n  owners = [\\"099720109477\\"]\\n}\\n", "language": "hcl"}, {"filename": "storage.tf", "content": "\\nresource \\"aws_db_subnet_group\\" \\"rds\\" {\\n  name       = \\"${local.name_prefix}-db-subnet-group\\"\\n  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]\\n  tags       = local.common_tags\\n}\\n\\nresource \\"aws_db_instance\\" \\"main\\" {\\n  identifier             = \\"${local.name_prefix}-db\\"\\n  allocated_storage      = 20\\n  max_allocated_storage  = 40\\n  storage_type           = \\"gp3\\"\\n  engine                 = \\"postgres\\"\\n  engine_version         = \\"15.4\\"\\n  instance_class         = var.db_instance_class\\n  multi_az               = false\\n  db_subnet_group_name   = aws_db_subnet_group.rds.name\\n  skip_final_snapshot    = true\\n  storage_encrypted      = true\\n  tags                   = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "main.tf", "content": "# Main Architecture Integration & Security Services\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n\\noutput \\"instance_ip\\" {\\n  description = \\"Public IP of the application instance\\"\\n  value       = aws_instance.app.public_ip\\n}\\n\\noutput \\"rds_endpoint\\" {\\n  description = \\"Primary RDS Connection Endpoint\\"\\n  value       = aws_db_instance.main.endpoint\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 17:49:15.99728
tf-f8ef56ffdba7	draft	aether-cloud	us-east-1	terraform	2891fe02bb95189bc2a1aa3ad947b947d6906def7543af0f34621a6260736196	[{"filename": "versions.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "provider.tf", "content": "provider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Development\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t3.medium\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n", "language": "hcl"}, {"filename": "locals.tf", "content": "locals {\\n  name_prefix = var.project_name\\n  common_tags = {\\n    Project     = var.project_name\\n    ManagedBy   = \\"AetherOps\\"\\n    ArchitectureVersion = \\"draft\\"\\n  }\\n}\\n", "language": "hcl"}, {"filename": "network.tf", "content": "# VPC & Networking\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-vpc\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_internet_gateway\\" \\"igw\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-igw\\"\\n  })\\n}\\n\\nresource \\"aws_route_table\\" \\"public\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  route {\\n    cidr_block = \\"0.0.0.0/0\\"\\n    gateway_id = aws_internet_gateway.igw.id\\n  }\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-rt\\"\\n  })\\n}\\n\\nresource \\"aws_route_table_association\\" \\"public_a\\" {\\n  subnet_id      = aws_subnet.public_a.id\\n  route_table_id = aws_route_table.public.id\\n}\\n", "language": "hcl"}, {"filename": "security.tf", "content": "# Security Groups & Policies\\nresource \\"aws_security_group\\" \\"app_sg\\" {\\n  name        = \\"${local.name_prefix}-app-sg\\"\\n  description = \\"AetherOps security group for application workload\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 8080\\n    to_port     = 8080\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  tags = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "compute.tf", "content": "# Compute Resources (EC2)\\nresource \\"aws_instance\\" \\"app\\" {\\n  ami                    = data.aws_ami.ubuntu.id\\n  instance_type          = var.instance_type\\n  subnet_id              = aws_subnet.public_a.id\\n  vpc_security_group_ids = [aws_security_group.app_sg.id]\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-instance\\"\\n  })\\n}\\n\\ndata \\"aws_ami\\" \\"ubuntu\\" {\\n  most_recent = true\\n  filter {\\n    name   = \\"name\\"\\n    values = [\\"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*\\"]\\n  }\\n  filter {\\n    name   = \\"virtualization-type\\"\\n    values = [\\"hvm\\"]\\n  }\\n  owners = [\\"099720109477\\"]\\n}\\n", "language": "hcl"}, {"filename": "storage.tf", "content": "# Storage configuration (No additional storage resources approved)", "language": "hcl"}, {"filename": "main.tf", "content": "# Main Architecture Integration & Security Services\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n\\noutput \\"instance_ip\\" {\\n  description = \\"Public IP of the application instance\\"\\n  value       = aws_instance.app.public_ip\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 17:51:35.798563
tf-70ffd445e65d	draft	aether-cloud	us-east-1	terraform	0ab9e6cde908a33605180a64806a26f4dc04dbef1ec6911d07e6de7a2252f5db	[{"filename": "versions.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "provider.tf", "content": "provider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Production\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t3.medium\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n", "language": "hcl"}, {"filename": "locals.tf", "content": "locals {\\n  name_prefix = var.project_name\\n  common_tags = {\\n    Project     = var.project_name\\n    ManagedBy   = \\"AetherOps\\"\\n    ArchitectureVersion = \\"draft\\"\\n  }\\n}\\n", "language": "hcl"}, {"filename": "network.tf", "content": "# VPC & Networking\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-vpc\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_internet_gateway\\" \\"igw\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-igw\\"\\n  })\\n}\\n\\nresource \\"aws_route_table\\" \\"public\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  route {\\n    cidr_block = \\"0.0.0.0/0\\"\\n    gateway_id = aws_internet_gateway.igw.id\\n  }\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-rt\\"\\n  })\\n}\\n\\nresource \\"aws_route_table_association\\" \\"public_a\\" {\\n  subnet_id      = aws_subnet.public_a.id\\n  route_table_id = aws_route_table.public.id\\n}\\n", "language": "hcl"}, {"filename": "security.tf", "content": "# Security Groups & Policies\\nresource \\"aws_security_group\\" \\"app_sg\\" {\\n  name        = \\"${local.name_prefix}-app-sg\\"\\n  description = \\"AetherOps security group for application workload\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 8080\\n    to_port     = 8080\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  tags = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "compute.tf", "content": "# Compute Resources (EC2)\\nresource \\"aws_instance\\" \\"app\\" {\\n  ami                    = data.aws_ami.ubuntu.id\\n  instance_type          = var.instance_type\\n  subnet_id              = aws_subnet.public_a.id\\n  vpc_security_group_ids = [aws_security_group.app_sg.id]\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-instance\\"\\n  })\\n}\\n\\ndata \\"aws_ami\\" \\"ubuntu\\" {\\n  most_recent = true\\n  filter {\\n    name   = \\"name\\"\\n    values = [\\"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*\\"]\\n  }\\n  filter {\\n    name   = \\"virtualization-type\\"\\n    values = [\\"hvm\\"]\\n  }\\n  owners = [\\"099720109477\\"]\\n}\\n", "language": "hcl"}, {"filename": "storage.tf", "content": "# Storage configuration (No additional storage resources approved)", "language": "hcl"}, {"filename": "main.tf", "content": "# Main Architecture Integration & Security Services\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n\\noutput \\"instance_ip\\" {\\n  description = \\"Public IP of the application instance\\"\\n  value       = aws_instance.app.public_ip\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 18:00:00.597188
tf-6a9751062b11	draft	aether-cloud	us-east-1	terraform	0ab9e6cde908a33605180a64806a26f4dc04dbef1ec6911d07e6de7a2252f5db	[{"filename": "versions.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "provider.tf", "content": "provider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Production\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t3.medium\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n", "language": "hcl"}, {"filename": "locals.tf", "content": "locals {\\n  name_prefix = var.project_name\\n  common_tags = {\\n    Project     = var.project_name\\n    ManagedBy   = \\"AetherOps\\"\\n    ArchitectureVersion = \\"draft\\"\\n  }\\n}\\n", "language": "hcl"}, {"filename": "network.tf", "content": "# VPC & Networking\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-vpc\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_internet_gateway\\" \\"igw\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-igw\\"\\n  })\\n}\\n\\nresource \\"aws_route_table\\" \\"public\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  route {\\n    cidr_block = \\"0.0.0.0/0\\"\\n    gateway_id = aws_internet_gateway.igw.id\\n  }\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-rt\\"\\n  })\\n}\\n\\nresource \\"aws_route_table_association\\" \\"public_a\\" {\\n  subnet_id      = aws_subnet.public_a.id\\n  route_table_id = aws_route_table.public.id\\n}\\n", "language": "hcl"}, {"filename": "security.tf", "content": "# Security Groups & Policies\\nresource \\"aws_security_group\\" \\"app_sg\\" {\\n  name        = \\"${local.name_prefix}-app-sg\\"\\n  description = \\"AetherOps security group for application workload\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 8080\\n    to_port     = 8080\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  tags = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "compute.tf", "content": "# Compute Resources (EC2)\\nresource \\"aws_instance\\" \\"app\\" {\\n  ami                    = data.aws_ami.ubuntu.id\\n  instance_type          = var.instance_type\\n  subnet_id              = aws_subnet.public_a.id\\n  vpc_security_group_ids = [aws_security_group.app_sg.id]\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-instance\\"\\n  })\\n}\\n\\ndata \\"aws_ami\\" \\"ubuntu\\" {\\n  most_recent = true\\n  filter {\\n    name   = \\"name\\"\\n    values = [\\"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*\\"]\\n  }\\n  filter {\\n    name   = \\"virtualization-type\\"\\n    values = [\\"hvm\\"]\\n  }\\n  owners = [\\"099720109477\\"]\\n}\\n", "language": "hcl"}, {"filename": "storage.tf", "content": "# Storage configuration (No additional storage resources approved)", "language": "hcl"}, {"filename": "main.tf", "content": "# Main Architecture Integration & Security Services\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n\\noutput \\"instance_ip\\" {\\n  description = \\"Public IP of the application instance\\"\\n  value       = aws_instance.app.public_ip\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 18:00:48.929796
tf-a5c604778087	draft	aether-cloud	us-east-1	terraform	0ab9e6cde908a33605180a64806a26f4dc04dbef1ec6911d07e6de7a2252f5db	[{"filename": "versions.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "provider.tf", "content": "provider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Production\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t3.medium\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n", "language": "hcl"}, {"filename": "locals.tf", "content": "locals {\\n  name_prefix = var.project_name\\n  common_tags = {\\n    Project     = var.project_name\\n    ManagedBy   = \\"AetherOps\\"\\n    ArchitectureVersion = \\"draft\\"\\n  }\\n}\\n", "language": "hcl"}, {"filename": "network.tf", "content": "# VPC & Networking\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-vpc\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_internet_gateway\\" \\"igw\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-igw\\"\\n  })\\n}\\n\\nresource \\"aws_route_table\\" \\"public\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  route {\\n    cidr_block = \\"0.0.0.0/0\\"\\n    gateway_id = aws_internet_gateway.igw.id\\n  }\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-rt\\"\\n  })\\n}\\n\\nresource \\"aws_route_table_association\\" \\"public_a\\" {\\n  subnet_id      = aws_subnet.public_a.id\\n  route_table_id = aws_route_table.public.id\\n}\\n", "language": "hcl"}, {"filename": "security.tf", "content": "# Security Groups & Policies\\nresource \\"aws_security_group\\" \\"app_sg\\" {\\n  name        = \\"${local.name_prefix}-app-sg\\"\\n  description = \\"AetherOps security group for application workload\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 8080\\n    to_port     = 8080\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  tags = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "compute.tf", "content": "# Compute Resources (EC2)\\nresource \\"aws_instance\\" \\"app\\" {\\n  ami                    = data.aws_ami.ubuntu.id\\n  instance_type          = var.instance_type\\n  subnet_id              = aws_subnet.public_a.id\\n  vpc_security_group_ids = [aws_security_group.app_sg.id]\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-instance\\"\\n  })\\n}\\n\\ndata \\"aws_ami\\" \\"ubuntu\\" {\\n  most_recent = true\\n  filter {\\n    name   = \\"name\\"\\n    values = [\\"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*\\"]\\n  }\\n  filter {\\n    name   = \\"virtualization-type\\"\\n    values = [\\"hvm\\"]\\n  }\\n  owners = [\\"099720109477\\"]\\n}\\n", "language": "hcl"}, {"filename": "storage.tf", "content": "# Storage configuration (No additional storage resources approved)", "language": "hcl"}, {"filename": "main.tf", "content": "# Main Architecture Integration & Security Services\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n\\noutput \\"instance_ip\\" {\\n  description = \\"Public IP of the application instance\\"\\n  value       = aws_instance.app.public_ip\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 18:00:54.804613
tf-9a3cce836cb3	draft	aether-cloud	us-east-1	terraform	0ab9e6cde908a33605180a64806a26f4dc04dbef1ec6911d07e6de7a2252f5db	[{"filename": "versions.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "provider.tf", "content": "provider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Production\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t3.medium\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n", "language": "hcl"}, {"filename": "locals.tf", "content": "locals {\\n  name_prefix = var.project_name\\n  common_tags = {\\n    Project     = var.project_name\\n    ManagedBy   = \\"AetherOps\\"\\n    ArchitectureVersion = \\"draft\\"\\n  }\\n}\\n", "language": "hcl"}, {"filename": "network.tf", "content": "# VPC & Networking\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-vpc\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_internet_gateway\\" \\"igw\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-igw\\"\\n  })\\n}\\n\\nresource \\"aws_route_table\\" \\"public\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  route {\\n    cidr_block = \\"0.0.0.0/0\\"\\n    gateway_id = aws_internet_gateway.igw.id\\n  }\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-rt\\"\\n  })\\n}\\n\\nresource \\"aws_route_table_association\\" \\"public_a\\" {\\n  subnet_id      = aws_subnet.public_a.id\\n  route_table_id = aws_route_table.public.id\\n}\\n", "language": "hcl"}, {"filename": "security.tf", "content": "# Security Groups & Policies\\nresource \\"aws_security_group\\" \\"app_sg\\" {\\n  name        = \\"${local.name_prefix}-app-sg\\"\\n  description = \\"AetherOps security group for application workload\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 8080\\n    to_port     = 8080\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  tags = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "compute.tf", "content": "# Compute Resources (EC2)\\nresource \\"aws_instance\\" \\"app\\" {\\n  ami                    = data.aws_ami.ubuntu.id\\n  instance_type          = var.instance_type\\n  subnet_id              = aws_subnet.public_a.id\\n  vpc_security_group_ids = [aws_security_group.app_sg.id]\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-instance\\"\\n  })\\n}\\n\\ndata \\"aws_ami\\" \\"ubuntu\\" {\\n  most_recent = true\\n  filter {\\n    name   = \\"name\\"\\n    values = [\\"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*\\"]\\n  }\\n  filter {\\n    name   = \\"virtualization-type\\"\\n    values = [\\"hvm\\"]\\n  }\\n  owners = [\\"099720109477\\"]\\n}\\n", "language": "hcl"}, {"filename": "storage.tf", "content": "# Storage configuration (No additional storage resources approved)", "language": "hcl"}, {"filename": "main.tf", "content": "# Main Architecture Integration & Security Services\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n\\noutput \\"instance_ip\\" {\\n  description = \\"Public IP of the application instance\\"\\n  value       = aws_instance.app.public_ip\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 18:01:02.253625
tf-bad1d1656fb5	draft	aether-cloud	us-east-1	terraform	0ab9e6cde908a33605180a64806a26f4dc04dbef1ec6911d07e6de7a2252f5db	[{"filename": "versions.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "provider.tf", "content": "provider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Production\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t3.medium\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n", "language": "hcl"}, {"filename": "locals.tf", "content": "locals {\\n  name_prefix = var.project_name\\n  common_tags = {\\n    Project     = var.project_name\\n    ManagedBy   = \\"AetherOps\\"\\n    ArchitectureVersion = \\"draft\\"\\n  }\\n}\\n", "language": "hcl"}, {"filename": "network.tf", "content": "# VPC & Networking\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-vpc\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_internet_gateway\\" \\"igw\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-igw\\"\\n  })\\n}\\n\\nresource \\"aws_route_table\\" \\"public\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  route {\\n    cidr_block = \\"0.0.0.0/0\\"\\n    gateway_id = aws_internet_gateway.igw.id\\n  }\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-rt\\"\\n  })\\n}\\n\\nresource \\"aws_route_table_association\\" \\"public_a\\" {\\n  subnet_id      = aws_subnet.public_a.id\\n  route_table_id = aws_route_table.public.id\\n}\\n", "language": "hcl"}, {"filename": "security.tf", "content": "# Security Groups & Policies\\nresource \\"aws_security_group\\" \\"app_sg\\" {\\n  name        = \\"${local.name_prefix}-app-sg\\"\\n  description = \\"AetherOps security group for application workload\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 8080\\n    to_port     = 8080\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  tags = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "compute.tf", "content": "# Compute Resources (EC2)\\nresource \\"aws_instance\\" \\"app\\" {\\n  ami                    = data.aws_ami.ubuntu.id\\n  instance_type          = var.instance_type\\n  subnet_id              = aws_subnet.public_a.id\\n  vpc_security_group_ids = [aws_security_group.app_sg.id]\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-instance\\"\\n  })\\n}\\n\\ndata \\"aws_ami\\" \\"ubuntu\\" {\\n  most_recent = true\\n  filter {\\n    name   = \\"name\\"\\n    values = [\\"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*\\"]\\n  }\\n  filter {\\n    name   = \\"virtualization-type\\"\\n    values = [\\"hvm\\"]\\n  }\\n  owners = [\\"099720109477\\"]\\n}\\n", "language": "hcl"}, {"filename": "storage.tf", "content": "# Storage configuration (No additional storage resources approved)", "language": "hcl"}, {"filename": "main.tf", "content": "# Main Architecture Integration & Security Services\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n\\noutput \\"instance_ip\\" {\\n  description = \\"Public IP of the application instance\\"\\n  value       = aws_instance.app.public_ip\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 18:12:19.579372
tf-3949aa9fdf2f	draft	aether-cloud	us-east-1	terraform	0ab9e6cde908a33605180a64806a26f4dc04dbef1ec6911d07e6de7a2252f5db	[{"filename": "versions.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "provider.tf", "content": "provider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Production\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t3.medium\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n", "language": "hcl"}, {"filename": "locals.tf", "content": "locals {\\n  name_prefix = var.project_name\\n  common_tags = {\\n    Project     = var.project_name\\n    ManagedBy   = \\"AetherOps\\"\\n    ArchitectureVersion = \\"draft\\"\\n  }\\n}\\n", "language": "hcl"}, {"filename": "network.tf", "content": "# VPC & Networking\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-vpc\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_internet_gateway\\" \\"igw\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-igw\\"\\n  })\\n}\\n\\nresource \\"aws_route_table\\" \\"public\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  route {\\n    cidr_block = \\"0.0.0.0/0\\"\\n    gateway_id = aws_internet_gateway.igw.id\\n  }\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-rt\\"\\n  })\\n}\\n\\nresource \\"aws_route_table_association\\" \\"public_a\\" {\\n  subnet_id      = aws_subnet.public_a.id\\n  route_table_id = aws_route_table.public.id\\n}\\n", "language": "hcl"}, {"filename": "security.tf", "content": "# Security Groups & Policies\\nresource \\"aws_security_group\\" \\"app_sg\\" {\\n  name        = \\"${local.name_prefix}-app-sg\\"\\n  description = \\"AetherOps security group for application workload\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 8080\\n    to_port     = 8080\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  tags = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "compute.tf", "content": "# Compute Resources (EC2)\\nresource \\"aws_instance\\" \\"app\\" {\\n  ami                    = data.aws_ami.ubuntu.id\\n  instance_type          = var.instance_type\\n  subnet_id              = aws_subnet.public_a.id\\n  vpc_security_group_ids = [aws_security_group.app_sg.id]\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-instance\\"\\n  })\\n}\\n\\ndata \\"aws_ami\\" \\"ubuntu\\" {\\n  most_recent = true\\n  filter {\\n    name   = \\"name\\"\\n    values = [\\"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*\\"]\\n  }\\n  filter {\\n    name   = \\"virtualization-type\\"\\n    values = [\\"hvm\\"]\\n  }\\n  owners = [\\"099720109477\\"]\\n}\\n", "language": "hcl"}, {"filename": "storage.tf", "content": "# Storage configuration (No additional storage resources approved)", "language": "hcl"}, {"filename": "main.tf", "content": "# Main Architecture Integration & Security Services\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n\\noutput \\"instance_ip\\" {\\n  description = \\"Public IP of the application instance\\"\\n  value       = aws_instance.app.public_ip\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 18:19:08.389737
tf-9cba73fd2be0	draft	aether-cloud	us-east-1	terraform	0ab9e6cde908a33605180a64806a26f4dc04dbef1ec6911d07e6de7a2252f5db	[{"filename": "versions.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "provider.tf", "content": "provider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Production\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t3.medium\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n", "language": "hcl"}, {"filename": "locals.tf", "content": "locals {\\n  name_prefix = var.project_name\\n  common_tags = {\\n    Project     = var.project_name\\n    ManagedBy   = \\"AetherOps\\"\\n    ArchitectureVersion = \\"draft\\"\\n  }\\n}\\n", "language": "hcl"}, {"filename": "network.tf", "content": "# VPC & Networking\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-vpc\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_internet_gateway\\" \\"igw\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-igw\\"\\n  })\\n}\\n\\nresource \\"aws_route_table\\" \\"public\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  route {\\n    cidr_block = \\"0.0.0.0/0\\"\\n    gateway_id = aws_internet_gateway.igw.id\\n  }\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-rt\\"\\n  })\\n}\\n\\nresource \\"aws_route_table_association\\" \\"public_a\\" {\\n  subnet_id      = aws_subnet.public_a.id\\n  route_table_id = aws_route_table.public.id\\n}\\n", "language": "hcl"}, {"filename": "security.tf", "content": "# Security Groups & Policies\\nresource \\"aws_security_group\\" \\"app_sg\\" {\\n  name        = \\"${local.name_prefix}-app-sg\\"\\n  description = \\"AetherOps security group for application workload\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 8080\\n    to_port     = 8080\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  tags = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "compute.tf", "content": "# Compute Resources (EC2)\\nresource \\"aws_instance\\" \\"app\\" {\\n  ami                    = data.aws_ami.ubuntu.id\\n  instance_type          = var.instance_type\\n  subnet_id              = aws_subnet.public_a.id\\n  vpc_security_group_ids = [aws_security_group.app_sg.id]\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-instance\\"\\n  })\\n}\\n\\ndata \\"aws_ami\\" \\"ubuntu\\" {\\n  most_recent = true\\n  filter {\\n    name   = \\"name\\"\\n    values = [\\"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*\\"]\\n  }\\n  filter {\\n    name   = \\"virtualization-type\\"\\n    values = [\\"hvm\\"]\\n  }\\n  owners = [\\"099720109477\\"]\\n}\\n", "language": "hcl"}, {"filename": "storage.tf", "content": "# Storage configuration (No additional storage resources approved)", "language": "hcl"}, {"filename": "main.tf", "content": "# Main Architecture Integration & Security Services\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n\\noutput \\"instance_ip\\" {\\n  description = \\"Public IP of the application instance\\"\\n  value       = aws_instance.app.public_ip\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 18:19:09.043047
tf-4969999766ff	draft	aether-cloud	us-east-1	terraform	2891fe02bb95189bc2a1aa3ad947b947d6906def7543af0f34621a6260736196	[{"filename": "versions.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "provider.tf", "content": "provider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Development\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t3.medium\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n", "language": "hcl"}, {"filename": "locals.tf", "content": "locals {\\n  name_prefix = var.project_name\\n  common_tags = {\\n    Project     = var.project_name\\n    ManagedBy   = \\"AetherOps\\"\\n    ArchitectureVersion = \\"draft\\"\\n  }\\n}\\n", "language": "hcl"}, {"filename": "network.tf", "content": "# VPC & Networking\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-vpc\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_internet_gateway\\" \\"igw\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-igw\\"\\n  })\\n}\\n\\nresource \\"aws_route_table\\" \\"public\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  route {\\n    cidr_block = \\"0.0.0.0/0\\"\\n    gateway_id = aws_internet_gateway.igw.id\\n  }\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-rt\\"\\n  })\\n}\\n\\nresource \\"aws_route_table_association\\" \\"public_a\\" {\\n  subnet_id      = aws_subnet.public_a.id\\n  route_table_id = aws_route_table.public.id\\n}\\n", "language": "hcl"}, {"filename": "security.tf", "content": "# Security Groups & Policies\\nresource \\"aws_security_group\\" \\"app_sg\\" {\\n  name        = \\"${local.name_prefix}-app-sg\\"\\n  description = \\"AetherOps security group for application workload\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 8080\\n    to_port     = 8080\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  tags = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "compute.tf", "content": "# Compute Resources (EC2)\\nresource \\"aws_instance\\" \\"app\\" {\\n  ami                    = data.aws_ami.ubuntu.id\\n  instance_type          = var.instance_type\\n  subnet_id              = aws_subnet.public_a.id\\n  vpc_security_group_ids = [aws_security_group.app_sg.id]\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-instance\\"\\n  })\\n}\\n\\ndata \\"aws_ami\\" \\"ubuntu\\" {\\n  most_recent = true\\n  filter {\\n    name   = \\"name\\"\\n    values = [\\"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*\\"]\\n  }\\n  filter {\\n    name   = \\"virtualization-type\\"\\n    values = [\\"hvm\\"]\\n  }\\n  owners = [\\"099720109477\\"]\\n}\\n", "language": "hcl"}, {"filename": "storage.tf", "content": "# Storage configuration (No additional storage resources approved)", "language": "hcl"}, {"filename": "main.tf", "content": "# Main Architecture Integration & Security Services\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n\\noutput \\"instance_ip\\" {\\n  description = \\"Public IP of the application instance\\"\\n  value       = aws_instance.app.public_ip\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 18:23:52.023253
tf-07e3948990a4	draft	aether-cloud	us-east-1	terraform	2891fe02bb95189bc2a1aa3ad947b947d6906def7543af0f34621a6260736196	[{"filename": "versions.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "provider.tf", "content": "provider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Development\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t3.medium\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n", "language": "hcl"}, {"filename": "locals.tf", "content": "locals {\\n  name_prefix = var.project_name\\n  common_tags = {\\n    Project     = var.project_name\\n    ManagedBy   = \\"AetherOps\\"\\n    ArchitectureVersion = \\"draft\\"\\n  }\\n}\\n", "language": "hcl"}, {"filename": "network.tf", "content": "# VPC & Networking\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-vpc\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_internet_gateway\\" \\"igw\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-igw\\"\\n  })\\n}\\n\\nresource \\"aws_route_table\\" \\"public\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  route {\\n    cidr_block = \\"0.0.0.0/0\\"\\n    gateway_id = aws_internet_gateway.igw.id\\n  }\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-rt\\"\\n  })\\n}\\n\\nresource \\"aws_route_table_association\\" \\"public_a\\" {\\n  subnet_id      = aws_subnet.public_a.id\\n  route_table_id = aws_route_table.public.id\\n}\\n", "language": "hcl"}, {"filename": "security.tf", "content": "# Security Groups & Policies\\nresource \\"aws_security_group\\" \\"app_sg\\" {\\n  name        = \\"${local.name_prefix}-app-sg\\"\\n  description = \\"AetherOps security group for application workload\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 8080\\n    to_port     = 8080\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  tags = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "compute.tf", "content": "# Compute Resources (EC2)\\nresource \\"aws_instance\\" \\"app\\" {\\n  ami                    = data.aws_ami.ubuntu.id\\n  instance_type          = var.instance_type\\n  subnet_id              = aws_subnet.public_a.id\\n  vpc_security_group_ids = [aws_security_group.app_sg.id]\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-instance\\"\\n  })\\n}\\n\\ndata \\"aws_ami\\" \\"ubuntu\\" {\\n  most_recent = true\\n  filter {\\n    name   = \\"name\\"\\n    values = [\\"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*\\"]\\n  }\\n  filter {\\n    name   = \\"virtualization-type\\"\\n    values = [\\"hvm\\"]\\n  }\\n  owners = [\\"099720109477\\"]\\n}\\n", "language": "hcl"}, {"filename": "storage.tf", "content": "# Storage configuration (No additional storage resources approved)", "language": "hcl"}, {"filename": "main.tf", "content": "# Main Architecture Integration & Security Services\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n\\noutput \\"instance_ip\\" {\\n  description = \\"Public IP of the application instance\\"\\n  value       = aws_instance.app.public_ip\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 18:35:35.945663
tf-f4a08f7c4e15	draft	aether-cloud	us-east-1	terraform	2891fe02bb95189bc2a1aa3ad947b947d6906def7543af0f34621a6260736196	[{"filename": "versions.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "provider.tf", "content": "provider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Development\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t3.medium\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n", "language": "hcl"}, {"filename": "locals.tf", "content": "locals {\\n  name_prefix = var.project_name\\n  common_tags = {\\n    Project     = var.project_name\\n    ManagedBy   = \\"AetherOps\\"\\n    ArchitectureVersion = \\"draft\\"\\n  }\\n}\\n", "language": "hcl"}, {"filename": "network.tf", "content": "# VPC & Networking\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-vpc\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_internet_gateway\\" \\"igw\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-igw\\"\\n  })\\n}\\n\\nresource \\"aws_route_table\\" \\"public\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  route {\\n    cidr_block = \\"0.0.0.0/0\\"\\n    gateway_id = aws_internet_gateway.igw.id\\n  }\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-rt\\"\\n  })\\n}\\n\\nresource \\"aws_route_table_association\\" \\"public_a\\" {\\n  subnet_id      = aws_subnet.public_a.id\\n  route_table_id = aws_route_table.public.id\\n}\\n", "language": "hcl"}, {"filename": "security.tf", "content": "# Security Groups & Policies\\nresource \\"aws_security_group\\" \\"app_sg\\" {\\n  name        = \\"${local.name_prefix}-app-sg\\"\\n  description = \\"AetherOps security group for application workload\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 8080\\n    to_port     = 8080\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  tags = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "compute.tf", "content": "# Compute Resources (EC2)\\nresource \\"aws_instance\\" \\"app\\" {\\n  ami                    = data.aws_ami.ubuntu.id\\n  instance_type          = var.instance_type\\n  subnet_id              = aws_subnet.public_a.id\\n  vpc_security_group_ids = [aws_security_group.app_sg.id]\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-instance\\"\\n  })\\n}\\n\\ndata \\"aws_ami\\" \\"ubuntu\\" {\\n  most_recent = true\\n  filter {\\n    name   = \\"name\\"\\n    values = [\\"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*\\"]\\n  }\\n  filter {\\n    name   = \\"virtualization-type\\"\\n    values = [\\"hvm\\"]\\n  }\\n  owners = [\\"099720109477\\"]\\n}\\n", "language": "hcl"}, {"filename": "storage.tf", "content": "# Storage configuration (No additional storage resources approved)", "language": "hcl"}, {"filename": "main.tf", "content": "# Main Architecture Integration & Security Services\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n\\noutput \\"instance_ip\\" {\\n  description = \\"Public IP of the application instance\\"\\n  value       = aws_instance.app.public_ip\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 18:37:04.250614
tf-9f53e783693d	draft	aether-cloud	us-east-1	terraform	2891fe02bb95189bc2a1aa3ad947b947d6906def7543af0f34621a6260736196	[{"filename": "versions.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "provider.tf", "content": "provider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Development\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t3.medium\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n", "language": "hcl"}, {"filename": "locals.tf", "content": "locals {\\n  name_prefix = var.project_name\\n  common_tags = {\\n    Project     = var.project_name\\n    ManagedBy   = \\"AetherOps\\"\\n    ArchitectureVersion = \\"draft\\"\\n  }\\n}\\n", "language": "hcl"}, {"filename": "network.tf", "content": "# VPC & Networking\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-vpc\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_internet_gateway\\" \\"igw\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-igw\\"\\n  })\\n}\\n\\nresource \\"aws_route_table\\" \\"public\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  route {\\n    cidr_block = \\"0.0.0.0/0\\"\\n    gateway_id = aws_internet_gateway.igw.id\\n  }\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-rt\\"\\n  })\\n}\\n\\nresource \\"aws_route_table_association\\" \\"public_a\\" {\\n  subnet_id      = aws_subnet.public_a.id\\n  route_table_id = aws_route_table.public.id\\n}\\n", "language": "hcl"}, {"filename": "security.tf", "content": "# Security Groups & Policies\\nresource \\"aws_security_group\\" \\"app_sg\\" {\\n  name        = \\"${local.name_prefix}-app-sg\\"\\n  description = \\"AetherOps security group for application workload\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 8080\\n    to_port     = 8080\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  tags = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "compute.tf", "content": "# Compute Resources (EC2)\\nresource \\"aws_instance\\" \\"app\\" {\\n  ami                    = data.aws_ami.ubuntu.id\\n  instance_type          = var.instance_type\\n  subnet_id              = aws_subnet.public_a.id\\n  vpc_security_group_ids = [aws_security_group.app_sg.id]\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-instance\\"\\n  })\\n}\\n\\ndata \\"aws_ami\\" \\"ubuntu\\" {\\n  most_recent = true\\n  filter {\\n    name   = \\"name\\"\\n    values = [\\"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*\\"]\\n  }\\n  filter {\\n    name   = \\"virtualization-type\\"\\n    values = [\\"hvm\\"]\\n  }\\n  owners = [\\"099720109477\\"]\\n}\\n", "language": "hcl"}, {"filename": "storage.tf", "content": "# Storage configuration (No additional storage resources approved)", "language": "hcl"}, {"filename": "main.tf", "content": "# Main Architecture Integration & Security Services\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n\\noutput \\"instance_ip\\" {\\n  description = \\"Public IP of the application instance\\"\\n  value       = aws_instance.app.public_ip\\n}\\n", "language": "hcl"}]	tenant-000000000002	user	2026-11-09 18:57:57.892846
tf-d7c85cacfd58	draft	Clock	us-east-1	terraform	55da03c51f79e26af92f3e7f55f498e1c30731a1888ad6500085b53946da84ae	[{"filename": "versions.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "provider.tf", "content": "provider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"Clock\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Development\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"Clock\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t3.medium\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n", "language": "hcl"}, {"filename": "locals.tf", "content": "locals {\\n  name_prefix = var.project_name\\n  common_tags = {\\n    Project     = var.project_name\\n    ManagedBy   = \\"AetherOps\\"\\n    ArchitectureVersion = \\"draft\\"\\n  }\\n}\\n", "language": "hcl"}, {"filename": "network.tf", "content": "# VPC & Networking\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-vpc\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_internet_gateway\\" \\"igw\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-igw\\"\\n  })\\n}\\n\\nresource \\"aws_route_table\\" \\"public\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  route {\\n    cidr_block = \\"0.0.0.0/0\\"\\n    gateway_id = aws_internet_gateway.igw.id\\n  }\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-rt\\"\\n  })\\n}\\n\\nresource \\"aws_route_table_association\\" \\"public_a\\" {\\n  subnet_id      = aws_subnet.public_a.id\\n  route_table_id = aws_route_table.public.id\\n}\\n", "language": "hcl"}, {"filename": "security.tf", "content": "# Security Groups & Policies\\nresource \\"aws_security_group\\" \\"app_sg\\" {\\n  name        = \\"${local.name_prefix}-app-sg\\"\\n  description = \\"AetherOps security group for application workload\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 8080\\n    to_port     = 8080\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  tags = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "compute.tf", "content": "# Compute Resources (EC2)\\nresource \\"aws_instance\\" \\"app\\" {\\n  ami                    = data.aws_ami.ubuntu.id\\n  instance_type          = var.instance_type\\n  subnet_id              = aws_subnet.public_a.id\\n  vpc_security_group_ids = [aws_security_group.app_sg.id]\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-instance\\"\\n  })\\n}\\n\\ndata \\"aws_ami\\" \\"ubuntu\\" {\\n  most_recent = true\\n  filter {\\n    name   = \\"name\\"\\n    values = [\\"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*\\"]\\n  }\\n  filter {\\n    name   = \\"virtualization-type\\"\\n    values = [\\"hvm\\"]\\n  }\\n  owners = [\\"099720109477\\"]\\n}\\n", "language": "hcl"}, {"filename": "storage.tf", "content": "# Storage configuration (No additional storage resources approved)", "language": "hcl"}, {"filename": "main.tf", "content": "# Main Architecture Integration & Security Services\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n\\noutput \\"instance_ip\\" {\\n  description = \\"Public IP of the application instance\\"\\n  value       = aws_instance.app.public_ip\\n}\\n", "language": "hcl"}]	tenant-eb8e04f5597a9283	prathap-32	2026-11-09 19:45:51.985771
tf-4f282f3c4d93	draft	aether-cloud	us-east-1	terraform	0ab9e6cde908a33605180a64806a26f4dc04dbef1ec6911d07e6de7a2252f5db	[{"filename": "versions.tf", "content": "terraform {\\n  required_version = \\">= 1.5.0\\"\\n  required_providers {\\n    aws = {\\n      source  = \\"hashicorp/aws\\"\\n      version = \\"~> 5.0\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "provider.tf", "content": "provider \\"aws\\" {\\n  region = var.aws_region\\n\\n  default_tags {\\n    tags = {\\n      Project     = \\"aether-cloud\\"\\n      ManagedBy   = \\"AetherOps\\"\\n      Environment = \\"Production\\"\\n    }\\n  }\\n}\\n", "language": "hcl"}, {"filename": "variables.tf", "content": "variable \\"aws_region\\" {\\n  type        = string\\n  default     = \\"us-east-1\\"\\n  description = \\"Target AWS deployment region\\"\\n}\\n\\nvariable \\"project_name\\" {\\n  type        = string\\n  default     = \\"aether-cloud\\"\\n  description = \\"Workload project identifier\\"\\n}\\n\\nvariable \\"instance_type\\" {\\n  type        = string\\n  default     = \\"t3.medium\\"\\n  description = \\"EC2 instance sizing\\"\\n}\\n", "language": "hcl"}, {"filename": "locals.tf", "content": "locals {\\n  name_prefix = var.project_name\\n  common_tags = {\\n    Project     = var.project_name\\n    ManagedBy   = \\"AetherOps\\"\\n    ArchitectureVersion = \\"draft\\"\\n  }\\n}\\n", "language": "hcl"}, {"filename": "network.tf", "content": "# VPC & Networking\\nresource \\"aws_vpc\\" \\"main\\" {\\n  cidr_block           = \\"10.0.0.0/16\\"\\n  enable_dns_hostnames = true\\n  enable_dns_support   = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-vpc\\"\\n  })\\n}\\n\\nresource \\"aws_subnet\\" \\"public_a\\" {\\n  vpc_id                  = aws_vpc.main.id\\n  cidr_block              = \\"10.0.1.0/24\\"\\n  availability_zone       = \\"${var.aws_region}a\\"\\n  map_public_ip_on_launch = true\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-subnet-a\\"\\n  })\\n}\\n\\nresource \\"aws_internet_gateway\\" \\"igw\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-igw\\"\\n  })\\n}\\n\\nresource \\"aws_route_table\\" \\"public\\" {\\n  vpc_id = aws_vpc.main.id\\n\\n  route {\\n    cidr_block = \\"0.0.0.0/0\\"\\n    gateway_id = aws_internet_gateway.igw.id\\n  }\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-public-rt\\"\\n  })\\n}\\n\\nresource \\"aws_route_table_association\\" \\"public_a\\" {\\n  subnet_id      = aws_subnet.public_a.id\\n  route_table_id = aws_route_table.public.id\\n}\\n", "language": "hcl"}, {"filename": "security.tf", "content": "# Security Groups & Policies\\nresource \\"aws_security_group\\" \\"app_sg\\" {\\n  name        = \\"${local.name_prefix}-app-sg\\"\\n  description = \\"AetherOps security group for application workload\\"\\n  vpc_id      = aws_vpc.main.id\\n\\n  ingress {\\n    from_port   = 80\\n    to_port     = 80\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 443\\n    to_port     = 443\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  ingress {\\n    from_port   = 8080\\n    to_port     = 8080\\n    protocol    = \\"tcp\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  egress {\\n    from_port   = 0\\n    to_port     = 0\\n    protocol    = \\"-1\\"\\n    cidr_blocks = [\\"0.0.0.0/0\\"]\\n  }\\n\\n  tags = local.common_tags\\n}\\n", "language": "hcl"}, {"filename": "compute.tf", "content": "# Compute Resources (EC2)\\nresource \\"aws_instance\\" \\"app\\" {\\n  ami                    = data.aws_ami.ubuntu.id\\n  instance_type          = var.instance_type\\n  subnet_id              = aws_subnet.public_a.id\\n  vpc_security_group_ids = [aws_security_group.app_sg.id]\\n\\n  tags = merge(local.common_tags, {\\n    Name = \\"${local.name_prefix}-instance\\"\\n  })\\n}\\n\\ndata \\"aws_ami\\" \\"ubuntu\\" {\\n  most_recent = true\\n  filter {\\n    name   = \\"name\\"\\n    values = [\\"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*\\"]\\n  }\\n  filter {\\n    name   = \\"virtualization-type\\"\\n    values = [\\"hvm\\"]\\n  }\\n  owners = [\\"099720109477\\"]\\n}\\n", "language": "hcl"}, {"filename": "storage.tf", "content": "# Storage configuration (No additional storage resources approved)", "language": "hcl"}, {"filename": "main.tf", "content": "# Main Architecture Integration & Security Services\\n", "language": "hcl"}, {"filename": "outputs.tf", "content": "output \\"vpc_id\\" {\\n  description = \\"Created VPC Identifier\\"\\n  value       = aws_vpc.main.id\\n}\\n\\noutput \\"instance_ip\\" {\\n  description = \\"Public IP of the application instance\\"\\n  value       = aws_instance.app.public_ip\\n}\\n", "language": "hcl"}]	tenant-eb8e04f5597a9283	prathap-32	2026-11-10 10:15:32.360178
\.


--
-- Data for Name: aether_dashboard_preferences; Type: TABLE DATA; Schema: project_manager; Owner: postgres
--

COPY project_manager.aether_dashboard_preferences (id, user_id, tenant_id, layout, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: aether_environments; Type: TABLE DATA; Schema: project_manager; Owner: postgres
--

COPY project_manager.aether_environments (id, project_id, tenant_id, created_by_user_id, account_id, name, env_type, aws_region, description, status, created_at, updated_at) FROM stdin;
ca6c1cc4-670b-4aed-b485-c3283268b585	6cb0ef5f-af3a-45d6-94d1-3fbf025a09b5	tenant-000000000002	00000000-0000-0000-0000-000000000002	987654321098	Dev	development	us-east-1	\N	CREATED	2026-11-09 12:05:03.15888	2026-11-09 12:05:03.158883
c760b614-b2dc-4bfd-9ef6-e1177629ffba	e9765404-3599-4da8-8cc4-84a3291448e2	e22da04a-35f4-4b0b-9072-bfe8b3718c7d	00000000-0000-0000-0000-000000000001	109283746519	Production-DR	disaster_recovery	mx-central-1	Cross-region disaster recovery standby fleet	CREATED	2026-11-09 17:04:21.247513	2026-11-09 17:04:21.247515
78e438da-da79-466d-8ba7-f9e996b550a8	1bb57e35-a71e-4a1b-b3a7-a9f3c69f9da6	tenant-accafa225032a40b	e4732b44-976b-4e29-975b-83020b353e17	375307448220	Edge-Sandbox	sandbox	ap-south-2	Hyderabad sandbox environment	CREATED	2026-11-09 17:04:21.537045	2026-11-09 17:04:21.537046
581a4587-cd32-44a3-a3a1-b78ad21fdaca	3feaa5ba-80ce-42ab-a7e3-3e8f6ab1b2a6	e22da04a-35f4-4b0b-9072-bfe8b3718c7d	00000000-0000-0000-0000-000000000001	109283746519	Production-DR	disaster_recovery	mx-central-1	Cross-region disaster recovery standby fleet	CREATED	2026-11-09 18:21:46.28638	2026-11-09 18:21:46.286381
bb0a47d8-db47-4ed2-9acb-08b1c1278a89	1c5e4107-307b-45f2-821e-34699ae58606	tenant-ab556f5b9f1d21de	8bf56aac-4325-41ca-95f1-b2d2bd94d55f	908376714563	Edge-Sandbox	sandbox	ap-south-2	Hyderabad sandbox environment	CREATED	2026-11-09 18:21:46.580712	2026-11-09 18:21:46.580714
3e2d171b-498d-4819-b2ee-e07a9fa650fe	abfa2b43-49af-4727-912d-ed441669a340	e22da04a-35f4-4b0b-9072-bfe8b3718c7d	00000000-0000-0000-0000-000000000001	109283746519	Production-DR	disaster_recovery	mx-central-1	Cross-region disaster recovery standby fleet	CREATED	2026-11-09 18:23:53.328654	2026-11-09 18:23:53.328656
4af2de36-8e77-476b-af84-66a5318aa069	7e0ba434-4da0-4457-8b20-274d3d51f8c1	tenant-3d43053400f6cf6f	846c659b-e02e-4d81-ac90-385587dbe03a	897972791092	Edge-Sandbox	sandbox	ap-south-2	Hyderabad sandbox environment	CREATED	2026-11-09 18:23:53.639341	2026-11-09 18:23:53.639343
077d6011-45fc-420b-8266-de7d63f001ef	87f082e7-f6a8-4e05-bf54-e2a1a4a83814	e22da04a-35f4-4b0b-9072-bfe8b3718c7d	00000000-0000-0000-0000-000000000001	109283746519	Production-DR	disaster_recovery	mx-central-1	Cross-region disaster recovery standby fleet	CREATED	2026-11-09 19:20:52.905297	2026-11-09 19:20:52.905298
19688642-ce56-4d5f-8116-9e2b105bbeeb	2c21366b-917a-4d08-8ce2-a677672a5131	tenant-8ffe2b1816e33d82	58d9853c-5e82-43f6-a8a7-9e5aa6f5769a	933278657090	Edge-Sandbox	sandbox	ap-south-2	Hyderabad sandbox environment	CREATED	2026-11-09 19:20:53.184108	2026-11-09 19:20:53.184109
d09aec85-8171-4dbd-af49-624b1d599193	74853f53-2973-443b-9b4f-f3dda3d7dd3b	tenant-eb8e04f5597a9283	f6c6bfd2-0ef4-40ec-9e4c-f3d838dca864	312766511865	Dev	development	ap-south-1	\N	CREATED	2026-11-09 19:42:30.46379	2026-11-09 19:42:30.463791
af34ff98-b6f3-4ad1-bcb1-d6f74fee54c3	f63ec5e5-d28a-46d6-bba6-9e20a4b24dfe	tenant-eb8e04f5597a9283	f6c6bfd2-0ef4-40ec-9e4c-f3d838dca864	312766511865	Dev	development	ap-southeast-1	\N	CREATED	2026-11-10 07:53:53.018686	2026-11-10 07:53:53.018687
5053332b-f960-474d-8a9f-dfa0b6a5f795	457af0e2-7714-465d-9c98-32576b8b039f	e22da04a-35f4-4b0b-9072-bfe8b3718c7d	00000000-0000-0000-0000-000000000001	109283746519	Production-DR	disaster_recovery	mx-central-1	Cross-region disaster recovery standby fleet	CREATED	2026-11-10 16:36:06.76037	2026-11-10 16:36:06.760371
3f386fa1-62c2-43dd-b884-928d52ab5876	c87eee57-ab12-4c26-9de4-3cac51814cc4	tenant-c6da3ecee91bbdf7	834ab1be-6f2c-4d00-8d26-d45586b955c2	496769225690	Edge-Sandbox	sandbox	ap-south-2	Hyderabad sandbox environment	CREATED	2026-11-10 16:36:07.067654	2026-11-10 16:36:07.067656
e1260120-d2c1-4d32-b0e9-906bfcf4a880	494e66bb-1e05-410b-a9ce-3b25e269038d	tenant-8a83305f3c57c1f7	dc92a89c-6c65-4f6f-9d6d-8d69e105d9e5	311253129938	Creation	development	ap-south-1	\N	CREATED	2026-11-10 16:37:35.409069	2026-11-10 16:37:35.409071
\.


--
-- Data for Name: aether_projects; Type: TABLE DATA; Schema: project_manager; Owner: postgres
--

COPY project_manager.aether_projects (id, name, description, project_type, owner, tenant_id, created_by_user_id, account_id, status, environment_count, created_at, updated_at) FROM stdin;
6cb0ef5f-af3a-45d6-94d1-3fbf025a09b5	Clock	\N	web_application	user	tenant-000000000002	00000000-0000-0000-0000-000000000002	987654321098	CREATED	1	2026-11-09 12:04:57.942023	2026-11-09 12:05:03.159043
e9765404-3599-4da8-8cc4-84a3291448e2	Admin-CloudBackend-24839	Serverless and event driven core	serverless_backend	admin	e22da04a-35f4-4b0b-9072-bfe8b3718c7d	00000000-0000-0000-0000-000000000001	109283746519	CREATED	1	2026-11-09 17:04:21.196027	2026-11-09 17:04:21.247628
1bb57e35-a71e-4a1b-b3a7-a9f3c69f9da6	IoT-Telemetry-5292	Edge telemetry ingest pipeline	iot_ingestion	tenant_dev_4165	tenant-accafa225032a40b	e4732b44-976b-4e29-975b-83020b353e17	375307448220	CREATED	1	2026-11-09 17:04:21.486649	2026-11-09 17:04:21.537172
3feaa5ba-80ce-42ab-a7e3-3e8f6ab1b2a6	Admin-CloudBackend-28943	Serverless and event driven core	serverless_backend	admin	e22da04a-35f4-4b0b-9072-bfe8b3718c7d	00000000-0000-0000-0000-000000000001	109283746519	CREATED	1	2026-11-09 18:21:46.233787	2026-11-09 18:21:46.286502
1c5e4107-307b-45f2-821e-34699ae58606	IoT-Telemetry-2722	Edge telemetry ingest pipeline	iot_ingestion	tenant_dev_26312	tenant-ab556f5b9f1d21de	8bf56aac-4325-41ca-95f1-b2d2bd94d55f	908376714563	CREATED	1	2026-11-09 18:21:46.534283	2026-11-09 18:21:46.580816
abfa2b43-49af-4727-912d-ed441669a340	Admin-CloudBackend-4213	Serverless and event driven core	serverless_backend	admin	e22da04a-35f4-4b0b-9072-bfe8b3718c7d	00000000-0000-0000-0000-000000000001	109283746519	CREATED	1	2026-11-09 18:23:53.277892	2026-11-09 18:23:53.328776
7e0ba434-4da0-4457-8b20-274d3d51f8c1	IoT-Telemetry-2259	Edge telemetry ingest pipeline	iot_ingestion	tenant_dev_5035	tenant-3d43053400f6cf6f	846c659b-e02e-4d81-ac90-385587dbe03a	897972791092	CREATED	1	2026-11-09 18:23:53.592621	2026-11-09 18:23:53.639445
87f082e7-f6a8-4e05-bf54-e2a1a4a83814	Admin-CloudBackend-12410	Serverless and event driven core	serverless_backend	admin	e22da04a-35f4-4b0b-9072-bfe8b3718c7d	00000000-0000-0000-0000-000000000001	109283746519	CREATED	1	2026-11-09 19:20:52.859386	2026-11-09 19:20:52.905393
2c21366b-917a-4d08-8ce2-a677672a5131	IoT-Telemetry-21927	Edge telemetry ingest pipeline	iot_ingestion	tenant_dev_20026	tenant-8ffe2b1816e33d82	58d9853c-5e82-43f6-a8a7-9e5aa6f5769a	933278657090	CREATED	1	2026-11-09 19:20:53.138564	2026-11-09 19:20:53.184202
74853f53-2973-443b-9b4f-f3dda3d7dd3b	Clock	\N	web_application	prathap-32	tenant-eb8e04f5597a9283	f6c6bfd2-0ef4-40ec-9e4c-f3d838dca864	312766511865	CREATED	1	2026-11-09 19:42:06.780405	2026-11-09 19:42:30.463886
f63ec5e5-d28a-46d6-bba6-9e20a4b24dfe	Clock	\N	web_application	prathap-32	tenant-eb8e04f5597a9283	f6c6bfd2-0ef4-40ec-9e4c-f3d838dca864	312766511865	CREATED	1	2026-11-10 07:53:09.406431	2026-11-10 07:53:53.018788
457af0e2-7714-465d-9c98-32576b8b039f	Admin-CloudBackend-13632	Serverless and event driven core	serverless_backend	admin	e22da04a-35f4-4b0b-9072-bfe8b3718c7d	00000000-0000-0000-0000-000000000001	109283746519	CREATED	1	2026-11-10 16:36:06.705719	2026-11-10 16:36:06.760478
c87eee57-ab12-4c26-9de4-3cac51814cc4	IoT-Telemetry-7519	Edge telemetry ingest pipeline	iot_ingestion	tenant_dev_10853	tenant-c6da3ecee91bbdf7	834ab1be-6f2c-4d00-8d26-d45586b955c2	496769225690	CREATED	1	2026-11-10 16:36:06.998202	2026-11-10 16:36:07.067752
494e66bb-1e05-410b-a9ce-3b25e269038d	To_do_list	\N	web_application	reno	tenant-8a83305f3c57c1f7	dc92a89c-6c65-4f6f-9d6d-8d69e105d9e5	311253129938	CREATED	1	2026-11-10 16:37:04.592914	2026-11-10 16:37:35.409167
\.


--
-- Data for Name: aether_tenant_memberships; Type: TABLE DATA; Schema: project_manager; Owner: postgres
--

COPY project_manager.aether_tenant_memberships (id, tenant_id, user_id, role, status, created_at, updated_at) FROM stdin;
d485822a-7a66-4c31-907c-c2c7da7abe4c	tenant-000000000002	00000000-0000-0000-0000-000000000002	OWNER	ACTIVE	2026-11-09 12:04:35.658973	2026-11-09 12:04:35.658977
cf849dfb-84f4-4630-b558-53f27b6146cf	e22da04a-35f4-4b0b-9072-bfe8b3718c7d	00000000-0000-0000-0000-000000000001	OWNER	ACTIVE	2026-11-09 12:21:02.789668	2026-11-09 12:21:02.789671
85214644-e465-410c-8528-f222abdb2e02	tenant-eb8e04f5597a9283	f6c6bfd2-0ef4-40ec-9e4c-f3d838dca864	OWNER	ACTIVE	2026-11-09 12:31:19.678604	2026-11-09 12:31:19.678606
83686e27-ba27-49aa-9953-898a8eb9d87f	tenant-accafa225032a40b	e4732b44-976b-4e29-975b-83020b353e17	OWNER	ACTIVE	2026-11-09 17:04:21.439733	2026-11-09 17:04:21.439735
184eb378-0f1d-4a97-b759-40ca560fb8c8	tenant-ab556f5b9f1d21de	8bf56aac-4325-41ca-95f1-b2d2bd94d55f	OWNER	ACTIVE	2026-11-09 18:21:46.483054	2026-11-09 18:21:46.483056
d252dc9b-992a-4686-911c-3df5a940303a	tenant-3d43053400f6cf6f	846c659b-e02e-4d81-ac90-385587dbe03a	OWNER	ACTIVE	2026-11-09 18:23:53.54363	2026-11-09 18:23:53.543633
868d93cb-b83f-481c-ab40-092f55c5c2c1	tenant-8ffe2b1816e33d82	58d9853c-5e82-43f6-a8a7-9e5aa6f5769a	OWNER	ACTIVE	2026-11-09 19:20:53.089643	2026-11-09 19:20:53.089645
418a7d8b-cb09-40ff-9bdd-9002a917a904	tenant-8a83305f3c57c1f7	dc92a89c-6c65-4f6f-9d6d-8d69e105d9e5	OWNER	ACTIVE	2026-11-10 16:35:43.841512	2026-11-10 16:35:43.841515
9d7bd3a2-55ac-4b7a-b415-3b8bc301f6b4	tenant-c6da3ecee91bbdf7	834ab1be-6f2c-4d00-8d26-d45586b955c2	OWNER	ACTIVE	2026-11-10 16:36:06.950095	2026-11-10 16:36:06.950097
910bb62e-9fb2-42b2-a891-d21ab6d9ea3c	tenant-8434b169f6e89d54	a8aaa6f0-cc68-40a9-8a50-fe19a67e4c30	OWNER	ACTIVE	2026-11-10 16:59:10.84857	2026-11-10 16:59:10.848572
b0f4bb23-e02d-433c-b8a1-b23c4315678e	tenant-e45207d965c37e08	c5811463-cf7c-4aee-afee-c212ad0a8d04	OWNER	ACTIVE	2026-11-11 10:37:45.081461	2026-11-11 10:37:45.081464
8aca7664-ffd7-48e4-a00d-36411aee3280	tenant-2d9ff2770710ffc0	f55a4128-c713-424c-8737-b12da5a4b26c	OWNER	ACTIVE	2026-11-11 10:43:21.496241	2026-11-11 10:43:21.496243
a1de6808-c1db-452f-b201-b99f2c4e4f77	tenant-e9c97a3cbaf019c1	68acea56-2d5a-4b59-990b-e167228e033c	OWNER	ACTIVE	2026-11-11 10:47:26.7601	2026-11-11 10:47:26.760102
d6ad4113-4e3d-4353-8834-d468d1ee7989	tenant-76a6cadefc68fb1a	8cd2f4d2-66d7-4c1b-b7aa-1498131b4ebf	OWNER	ACTIVE	2026-11-11 10:50:47.841199	2026-11-11 10:50:47.841202
e688ea20-0068-4ac0-84ed-1869910cbb49	tenant-db416a6fdd316414	bd29080d-dc65-4321-90e0-af1486e96819	OWNER	ACTIVE	2026-11-11 10:59:04.630464	2026-11-11 10:59:04.630466
\.


--
-- Data for Name: aether_tenants; Type: TABLE DATA; Schema: project_manager; Owner: postgres
--

COPY project_manager.aether_tenants (id, name, slug, tenant_type, status, created_at, updated_at) FROM stdin;
tenant-000000000002	user's Workspace	personal-user-00000000	PERSONAL	ACTIVE	2026-11-09 12:04:35.655946	2026-11-09 12:04:35.655953
e22da04a-35f4-4b0b-9072-bfe8b3718c7d	root_admin's Workspace	personal-root-admin-00000000	PERSONAL	ACTIVE	2026-11-09 12:21:02.78489	2026-11-09 12:21:02.784893
tenant-eb8e04f5597a9283	prathap-32's Workspace	personal-prathap-32-f6c6bfd2	PERSONAL	ACTIVE	2026-11-09 12:31:19.676526	2026-11-09 12:31:19.676528
tenant-accafa225032a40b	tenant_dev_4165's Workspace	personal-tenant-dev-4165-e4732b44	PERSONAL	ACTIVE	2026-11-09 17:04:21.437876	2026-11-09 17:04:21.437878
tenant-ab556f5b9f1d21de	tenant_dev_26312's Workspace	personal-tenant-dev-26312-8bf56aac	PERSONAL	ACTIVE	2026-11-09 18:21:46.481388	2026-11-09 18:21:46.48139
tenant-3d43053400f6cf6f	tenant_dev_5035's Workspace	personal-tenant-dev-5035-846c659b	PERSONAL	ACTIVE	2026-11-09 18:23:53.541665	2026-11-09 18:23:53.541668
tenant-8ffe2b1816e33d82	tenant_dev_20026's Workspace	personal-tenant-dev-20026-58d9853c	PERSONAL	ACTIVE	2026-11-09 19:20:53.088575	2026-11-09 19:20:53.088579
tenant-8a83305f3c57c1f7	reno's Workspace	personal-reno-dc92a89c	PERSONAL	ACTIVE	2026-11-10 16:35:43.838802	2026-11-10 16:35:43.838804
tenant-c6da3ecee91bbdf7	tenant_dev_10853's Workspace	personal-tenant-dev-10853-834ab1be	PERSONAL	ACTIVE	2026-11-10 16:36:06.948969	2026-11-10 16:36:06.948971
tenant-8434b169f6e89d54	reno_acden's Workspace	personal-reno-acden-a8aaa6f0	PERSONAL	ACTIVE	2026-11-10 16:59:10.846693	2026-11-10 16:59:10.846696
tenant-e45207d965c37e08	movies_._net's Workspace	personal-movies-net-c5811463	PERSONAL	ACTIVE	2026-11-11 10:37:45.079278	2026-11-11 10:37:45.079281
tenant-2d9ff2770710ffc0	stranger_things2's Workspace	personal-stranger-things2-f55a4128	PERSONAL	ACTIVE	2026-11-11 10:43:21.494915	2026-11-11 10:43:21.494917
tenant-e9c97a3cbaf019c1	gp_king's Workspace	personal-gp-king-68acea56	PERSONAL	ACTIVE	2026-11-11 10:47:26.758577	2026-11-11 10:47:26.75858
tenant-76a6cadefc68fb1a	prathap_g_651's Workspace	personal-prathap-g-651-8cd2f4d2	PERSONAL	ACTIVE	2026-11-11 10:50:47.840163	2026-11-11 10:50:47.840166
tenant-db416a6fdd316414	pradeepa_gunasekaran's Workspace	personal-pradeepa-gunasekaran-bd29080d	PERSONAL	ACTIVE	2026-11-11 10:59:04.628129	2026-11-11 10:59:04.628132
\.


--
-- Data for Name: pm_admin_audit_logs; Type: TABLE DATA; Schema: project_manager; Owner: postgres
--

COPY project_manager.pm_admin_audit_logs (id, username, action, target_resource, status, ip_address, details, created_at) FROM stdin;
\.


--
-- Data for Name: pm_admin_users; Type: TABLE DATA; Schema: project_manager; Owner: postgres
--

COPY project_manager.pm_admin_users (id, uuid, username, email, password_hash, role, is_active, failed_attempts, locked_until, last_login_at, created_at) FROM stdin;
1	1929c224-f520-5a31-96c1-64a22e1cb790	admin	admin@aetherops.cloud	$2b$12$ayFzjdUyGAlAJFEeu2FPeux9zsRfosfyjUzpjePRNBIEoJ7mj9Wse	SUPER_ADMIN	t	0	\N	\N	2026-11-09 12:04:34.116058
\.


--
-- Data for Name: admin_audit_logs; Type: TABLE DATA; Schema: region_ca_central_1; Owner: postgres
--

COPY region_ca_central_1.admin_audit_logs (id, username, action, target_resource, status, ip_address, details, created_at) FROM stdin;
\.


--
-- Data for Name: admin_users; Type: TABLE DATA; Schema: region_ca_central_1; Owner: postgres
--

COPY region_ca_central_1.admin_users (id, username, email, password_hash, role, is_active, failed_attempts, locked_until, last_login_at, created_at) FROM stdin;
\.


--
-- Data for Name: ec2_catalog; Type: TABLE DATA; Schema: region_ca_central_1; Owner: postgres
--

COPY region_ca_central_1.ec2_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, network_performance, category) FROM stdin;
\.


--
-- Data for Name: generic_service_catalog; Type: TABLE DATA; Schema: region_ca_central_1; Owner: postgres
--

COPY region_ca_central_1.generic_service_catalog (id, service, instance_type, vcpus, ram_gb, price_per_hour, unit, category, region, details) FROM stdin;
\.


--
-- Data for Name: rds_catalog; Type: TABLE DATA; Schema: region_ca_central_1; Owner: postgres
--

COPY region_ca_central_1.rds_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, category) FROM stdin;
\.


--
-- Data for Name: requirement_projects; Type: TABLE DATA; Schema: region_ca_central_1; Owner: postgres
--

COPY region_ca_central_1.requirement_projects (id, project_name, description, stream, target_region, traffic_scale, reliability, security_need, data_storage_gb, monthly_budget, tech_stack, operations, monitoring, architecture_tier, estimated_monthly_cost, cost_breakdown, service_rationales, cost_optimizations, profile_output, status, dispatched_to_m2, m2_graph_summary, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: sync_metadata; Type: TABLE DATA; Schema: region_ca_central_1; Owner: postgres
--

COPY region_ca_central_1.sync_metadata (id, region_code, last_sync_timestamp, status, records_synced, ec2_count, rds_count, generic_count, duration_ms, error_message) FROM stdin;
\.


--
-- Data for Name: admin_audit_logs; Type: TABLE DATA; Schema: region_ca_west_1; Owner: postgres
--

COPY region_ca_west_1.admin_audit_logs (id, username, action, target_resource, status, ip_address, details, created_at) FROM stdin;
\.


--
-- Data for Name: admin_users; Type: TABLE DATA; Schema: region_ca_west_1; Owner: postgres
--

COPY region_ca_west_1.admin_users (id, username, email, password_hash, role, is_active, failed_attempts, locked_until, last_login_at, created_at) FROM stdin;
\.


--
-- Data for Name: ec2_catalog; Type: TABLE DATA; Schema: region_ca_west_1; Owner: postgres
--

COPY region_ca_west_1.ec2_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, network_performance, category) FROM stdin;
\.


--
-- Data for Name: generic_service_catalog; Type: TABLE DATA; Schema: region_ca_west_1; Owner: postgres
--

COPY region_ca_west_1.generic_service_catalog (id, service, instance_type, vcpus, ram_gb, price_per_hour, unit, category, region, details) FROM stdin;
\.


--
-- Data for Name: rds_catalog; Type: TABLE DATA; Schema: region_ca_west_1; Owner: postgres
--

COPY region_ca_west_1.rds_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, category) FROM stdin;
\.


--
-- Data for Name: requirement_projects; Type: TABLE DATA; Schema: region_ca_west_1; Owner: postgres
--

COPY region_ca_west_1.requirement_projects (id, project_name, description, stream, target_region, traffic_scale, reliability, security_need, data_storage_gb, monthly_budget, tech_stack, operations, monitoring, architecture_tier, estimated_monthly_cost, cost_breakdown, service_rationales, cost_optimizations, profile_output, status, dispatched_to_m2, m2_graph_summary, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: sync_metadata; Type: TABLE DATA; Schema: region_ca_west_1; Owner: postgres
--

COPY region_ca_west_1.sync_metadata (id, region_code, last_sync_timestamp, status, records_synced, ec2_count, rds_count, generic_count, duration_ms, error_message) FROM stdin;
\.


--
-- Data for Name: admin_audit_logs; Type: TABLE DATA; Schema: region_mx_central_1; Owner: postgres
--

COPY region_mx_central_1.admin_audit_logs (id, username, action, target_resource, status, ip_address, details, created_at) FROM stdin;
\.


--
-- Data for Name: admin_users; Type: TABLE DATA; Schema: region_mx_central_1; Owner: postgres
--

COPY region_mx_central_1.admin_users (id, username, email, password_hash, role, is_active, failed_attempts, locked_until, last_login_at, created_at) FROM stdin;
\.


--
-- Data for Name: ec2_catalog; Type: TABLE DATA; Schema: region_mx_central_1; Owner: postgres
--

COPY region_mx_central_1.ec2_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, network_performance, category) FROM stdin;
\.


--
-- Data for Name: generic_service_catalog; Type: TABLE DATA; Schema: region_mx_central_1; Owner: postgres
--

COPY region_mx_central_1.generic_service_catalog (id, service, instance_type, vcpus, ram_gb, price_per_hour, unit, category, region, details) FROM stdin;
\.


--
-- Data for Name: rds_catalog; Type: TABLE DATA; Schema: region_mx_central_1; Owner: postgres
--

COPY region_mx_central_1.rds_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, category) FROM stdin;
\.


--
-- Data for Name: requirement_projects; Type: TABLE DATA; Schema: region_mx_central_1; Owner: postgres
--

COPY region_mx_central_1.requirement_projects (id, project_name, description, stream, target_region, traffic_scale, reliability, security_need, data_storage_gb, monthly_budget, tech_stack, operations, monitoring, architecture_tier, estimated_monthly_cost, cost_breakdown, service_rationales, cost_optimizations, profile_output, status, dispatched_to_m2, m2_graph_summary, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: sync_metadata; Type: TABLE DATA; Schema: region_mx_central_1; Owner: postgres
--

COPY region_mx_central_1.sync_metadata (id, region_code, last_sync_timestamp, status, records_synced, ec2_count, rds_count, generic_count, duration_ms, error_message) FROM stdin;
\.


--
-- Data for Name: admin_audit_logs; Type: TABLE DATA; Schema: region_sa_east_1; Owner: postgres
--

COPY region_sa_east_1.admin_audit_logs (id, username, action, target_resource, status, ip_address, details, created_at) FROM stdin;
\.


--
-- Data for Name: admin_users; Type: TABLE DATA; Schema: region_sa_east_1; Owner: postgres
--

COPY region_sa_east_1.admin_users (id, username, email, password_hash, role, is_active, failed_attempts, locked_until, last_login_at, created_at) FROM stdin;
\.


--
-- Data for Name: ec2_catalog; Type: TABLE DATA; Schema: region_sa_east_1; Owner: postgres
--

COPY region_sa_east_1.ec2_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, network_performance, category) FROM stdin;
\.


--
-- Data for Name: generic_service_catalog; Type: TABLE DATA; Schema: region_sa_east_1; Owner: postgres
--

COPY region_sa_east_1.generic_service_catalog (id, service, instance_type, vcpus, ram_gb, price_per_hour, unit, category, region, details) FROM stdin;
\.


--
-- Data for Name: rds_catalog; Type: TABLE DATA; Schema: region_sa_east_1; Owner: postgres
--

COPY region_sa_east_1.rds_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, category) FROM stdin;
\.


--
-- Data for Name: requirement_projects; Type: TABLE DATA; Schema: region_sa_east_1; Owner: postgres
--

COPY region_sa_east_1.requirement_projects (id, project_name, description, stream, target_region, traffic_scale, reliability, security_need, data_storage_gb, monthly_budget, tech_stack, operations, monitoring, architecture_tier, estimated_monthly_cost, cost_breakdown, service_rationales, cost_optimizations, profile_output, status, dispatched_to_m2, m2_graph_summary, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: sync_metadata; Type: TABLE DATA; Schema: region_sa_east_1; Owner: postgres
--

COPY region_sa_east_1.sync_metadata (id, region_code, last_sync_timestamp, status, records_synced, ec2_count, rds_count, generic_count, duration_ms, error_message) FROM stdin;
\.


--
-- Data for Name: admin_audit_logs; Type: TABLE DATA; Schema: region_us_east_1; Owner: postgres
--

COPY region_us_east_1.admin_audit_logs (id, username, action, target_resource, status, ip_address, details, created_at) FROM stdin;
\.


--
-- Data for Name: admin_users; Type: TABLE DATA; Schema: region_us_east_1; Owner: postgres
--

COPY region_us_east_1.admin_users (id, username, email, password_hash, role, is_active, failed_attempts, locked_until, last_login_at, created_at) FROM stdin;
\.


--
-- Data for Name: ec2_catalog; Type: TABLE DATA; Schema: region_us_east_1; Owner: postgres
--

COPY region_us_east_1.ec2_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, network_performance, category) FROM stdin;
\.


--
-- Data for Name: generic_service_catalog; Type: TABLE DATA; Schema: region_us_east_1; Owner: postgres
--

COPY region_us_east_1.generic_service_catalog (id, service, instance_type, vcpus, ram_gb, price_per_hour, unit, category, region, details) FROM stdin;
\.


--
-- Data for Name: rds_catalog; Type: TABLE DATA; Schema: region_us_east_1; Owner: postgres
--

COPY region_us_east_1.rds_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, category) FROM stdin;
\.


--
-- Data for Name: requirement_projects; Type: TABLE DATA; Schema: region_us_east_1; Owner: postgres
--

COPY region_us_east_1.requirement_projects (id, project_name, description, stream, target_region, traffic_scale, reliability, security_need, data_storage_gb, monthly_budget, tech_stack, operations, monitoring, architecture_tier, estimated_monthly_cost, cost_breakdown, service_rationales, cost_optimizations, profile_output, status, dispatched_to_m2, m2_graph_summary, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: sync_metadata; Type: TABLE DATA; Schema: region_us_east_1; Owner: postgres
--

COPY region_us_east_1.sync_metadata (id, region_code, last_sync_timestamp, status, records_synced, ec2_count, rds_count, generic_count, duration_ms, error_message) FROM stdin;
\.


--
-- Data for Name: admin_audit_logs; Type: TABLE DATA; Schema: region_us_east_2; Owner: postgres
--

COPY region_us_east_2.admin_audit_logs (id, username, action, target_resource, status, ip_address, details, created_at) FROM stdin;
\.


--
-- Data for Name: admin_users; Type: TABLE DATA; Schema: region_us_east_2; Owner: postgres
--

COPY region_us_east_2.admin_users (id, username, email, password_hash, role, is_active, failed_attempts, locked_until, last_login_at, created_at) FROM stdin;
\.


--
-- Data for Name: ec2_catalog; Type: TABLE DATA; Schema: region_us_east_2; Owner: postgres
--

COPY region_us_east_2.ec2_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, network_performance, category) FROM stdin;
\.


--
-- Data for Name: generic_service_catalog; Type: TABLE DATA; Schema: region_us_east_2; Owner: postgres
--

COPY region_us_east_2.generic_service_catalog (id, service, instance_type, vcpus, ram_gb, price_per_hour, unit, category, region, details) FROM stdin;
\.


--
-- Data for Name: rds_catalog; Type: TABLE DATA; Schema: region_us_east_2; Owner: postgres
--

COPY region_us_east_2.rds_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, category) FROM stdin;
\.


--
-- Data for Name: requirement_projects; Type: TABLE DATA; Schema: region_us_east_2; Owner: postgres
--

COPY region_us_east_2.requirement_projects (id, project_name, description, stream, target_region, traffic_scale, reliability, security_need, data_storage_gb, monthly_budget, tech_stack, operations, monitoring, architecture_tier, estimated_monthly_cost, cost_breakdown, service_rationales, cost_optimizations, profile_output, status, dispatched_to_m2, m2_graph_summary, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: sync_metadata; Type: TABLE DATA; Schema: region_us_east_2; Owner: postgres
--

COPY region_us_east_2.sync_metadata (id, region_code, last_sync_timestamp, status, records_synced, ec2_count, rds_count, generic_count, duration_ms, error_message) FROM stdin;
\.


--
-- Data for Name: admin_audit_logs; Type: TABLE DATA; Schema: region_us_gov_east_1; Owner: postgres
--

COPY region_us_gov_east_1.admin_audit_logs (id, username, action, target_resource, status, ip_address, details, created_at) FROM stdin;
\.


--
-- Data for Name: admin_users; Type: TABLE DATA; Schema: region_us_gov_east_1; Owner: postgres
--

COPY region_us_gov_east_1.admin_users (id, username, email, password_hash, role, is_active, failed_attempts, locked_until, last_login_at, created_at) FROM stdin;
\.


--
-- Data for Name: ec2_catalog; Type: TABLE DATA; Schema: region_us_gov_east_1; Owner: postgres
--

COPY region_us_gov_east_1.ec2_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, network_performance, category) FROM stdin;
\.


--
-- Data for Name: generic_service_catalog; Type: TABLE DATA; Schema: region_us_gov_east_1; Owner: postgres
--

COPY region_us_gov_east_1.generic_service_catalog (id, service, instance_type, vcpus, ram_gb, price_per_hour, unit, category, region, details) FROM stdin;
\.


--
-- Data for Name: rds_catalog; Type: TABLE DATA; Schema: region_us_gov_east_1; Owner: postgres
--

COPY region_us_gov_east_1.rds_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, category) FROM stdin;
\.


--
-- Data for Name: requirement_projects; Type: TABLE DATA; Schema: region_us_gov_east_1; Owner: postgres
--

COPY region_us_gov_east_1.requirement_projects (id, project_name, description, stream, target_region, traffic_scale, reliability, security_need, data_storage_gb, monthly_budget, tech_stack, operations, monitoring, architecture_tier, estimated_monthly_cost, cost_breakdown, service_rationales, cost_optimizations, profile_output, status, dispatched_to_m2, m2_graph_summary, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: sync_metadata; Type: TABLE DATA; Schema: region_us_gov_east_1; Owner: postgres
--

COPY region_us_gov_east_1.sync_metadata (id, region_code, last_sync_timestamp, status, records_synced, ec2_count, rds_count, generic_count, duration_ms, error_message) FROM stdin;
\.


--
-- Data for Name: admin_audit_logs; Type: TABLE DATA; Schema: region_us_gov_west_1; Owner: postgres
--

COPY region_us_gov_west_1.admin_audit_logs (id, username, action, target_resource, status, ip_address, details, created_at) FROM stdin;
\.


--
-- Data for Name: admin_users; Type: TABLE DATA; Schema: region_us_gov_west_1; Owner: postgres
--

COPY region_us_gov_west_1.admin_users (id, username, email, password_hash, role, is_active, failed_attempts, locked_until, last_login_at, created_at) FROM stdin;
\.


--
-- Data for Name: ec2_catalog; Type: TABLE DATA; Schema: region_us_gov_west_1; Owner: postgres
--

COPY region_us_gov_west_1.ec2_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, network_performance, category) FROM stdin;
\.


--
-- Data for Name: generic_service_catalog; Type: TABLE DATA; Schema: region_us_gov_west_1; Owner: postgres
--

COPY region_us_gov_west_1.generic_service_catalog (id, service, instance_type, vcpus, ram_gb, price_per_hour, unit, category, region, details) FROM stdin;
\.


--
-- Data for Name: rds_catalog; Type: TABLE DATA; Schema: region_us_gov_west_1; Owner: postgres
--

COPY region_us_gov_west_1.rds_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, category) FROM stdin;
\.


--
-- Data for Name: requirement_projects; Type: TABLE DATA; Schema: region_us_gov_west_1; Owner: postgres
--

COPY region_us_gov_west_1.requirement_projects (id, project_name, description, stream, target_region, traffic_scale, reliability, security_need, data_storage_gb, monthly_budget, tech_stack, operations, monitoring, architecture_tier, estimated_monthly_cost, cost_breakdown, service_rationales, cost_optimizations, profile_output, status, dispatched_to_m2, m2_graph_summary, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: sync_metadata; Type: TABLE DATA; Schema: region_us_gov_west_1; Owner: postgres
--

COPY region_us_gov_west_1.sync_metadata (id, region_code, last_sync_timestamp, status, records_synced, ec2_count, rds_count, generic_count, duration_ms, error_message) FROM stdin;
\.


--
-- Data for Name: admin_audit_logs; Type: TABLE DATA; Schema: region_us_west_1; Owner: postgres
--

COPY region_us_west_1.admin_audit_logs (id, username, action, target_resource, status, ip_address, details, created_at) FROM stdin;
\.


--
-- Data for Name: admin_users; Type: TABLE DATA; Schema: region_us_west_1; Owner: postgres
--

COPY region_us_west_1.admin_users (id, username, email, password_hash, role, is_active, failed_attempts, locked_until, last_login_at, created_at) FROM stdin;
\.


--
-- Data for Name: ec2_catalog; Type: TABLE DATA; Schema: region_us_west_1; Owner: postgres
--

COPY region_us_west_1.ec2_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, network_performance, category) FROM stdin;
\.


--
-- Data for Name: generic_service_catalog; Type: TABLE DATA; Schema: region_us_west_1; Owner: postgres
--

COPY region_us_west_1.generic_service_catalog (id, service, instance_type, vcpus, ram_gb, price_per_hour, unit, category, region, details) FROM stdin;
\.


--
-- Data for Name: rds_catalog; Type: TABLE DATA; Schema: region_us_west_1; Owner: postgres
--

COPY region_us_west_1.rds_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, category) FROM stdin;
\.


--
-- Data for Name: requirement_projects; Type: TABLE DATA; Schema: region_us_west_1; Owner: postgres
--

COPY region_us_west_1.requirement_projects (id, project_name, description, stream, target_region, traffic_scale, reliability, security_need, data_storage_gb, monthly_budget, tech_stack, operations, monitoring, architecture_tier, estimated_monthly_cost, cost_breakdown, service_rationales, cost_optimizations, profile_output, status, dispatched_to_m2, m2_graph_summary, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: sync_metadata; Type: TABLE DATA; Schema: region_us_west_1; Owner: postgres
--

COPY region_us_west_1.sync_metadata (id, region_code, last_sync_timestamp, status, records_synced, ec2_count, rds_count, generic_count, duration_ms, error_message) FROM stdin;
\.


--
-- Data for Name: admin_audit_logs; Type: TABLE DATA; Schema: region_us_west_2; Owner: postgres
--

COPY region_us_west_2.admin_audit_logs (id, username, action, target_resource, status, ip_address, details, created_at) FROM stdin;
\.


--
-- Data for Name: admin_users; Type: TABLE DATA; Schema: region_us_west_2; Owner: postgres
--

COPY region_us_west_2.admin_users (id, username, email, password_hash, role, is_active, failed_attempts, locked_until, last_login_at, created_at) FROM stdin;
\.


--
-- Data for Name: ec2_catalog; Type: TABLE DATA; Schema: region_us_west_2; Owner: postgres
--

COPY region_us_west_2.ec2_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, network_performance, category) FROM stdin;
\.


--
-- Data for Name: generic_service_catalog; Type: TABLE DATA; Schema: region_us_west_2; Owner: postgres
--

COPY region_us_west_2.generic_service_catalog (id, service, instance_type, vcpus, ram_gb, price_per_hour, unit, category, region, details) FROM stdin;
\.


--
-- Data for Name: rds_catalog; Type: TABLE DATA; Schema: region_us_west_2; Owner: postgres
--

COPY region_us_west_2.rds_catalog (id, instance_type, vcpus, ram_gb, price_per_hour, category) FROM stdin;
\.


--
-- Data for Name: requirement_projects; Type: TABLE DATA; Schema: region_us_west_2; Owner: postgres
--

COPY region_us_west_2.requirement_projects (id, project_name, description, stream, target_region, traffic_scale, reliability, security_need, data_storage_gb, monthly_budget, tech_stack, operations, monitoring, architecture_tier, estimated_monthly_cost, cost_breakdown, service_rationales, cost_optimizations, profile_output, status, dispatched_to_m2, m2_graph_summary, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: sync_metadata; Type: TABLE DATA; Schema: region_us_west_2; Owner: postgres
--

COPY region_us_west_2.sync_metadata (id, region_code, last_sync_timestamp, status, records_synced, ec2_count, rds_count, generic_count, duration_ms, error_message) FROM stdin;
\.


--
-- Data for Name: sc_admin_audit_logs; Type: TABLE DATA; Schema: source_connection; Owner: postgres
--

COPY source_connection.sc_admin_audit_logs (id, username, action, target_resource, status, ip_address, details, created_at) FROM stdin;
\.


--
-- Data for Name: sc_admin_users; Type: TABLE DATA; Schema: source_connection; Owner: postgres
--

COPY source_connection.sc_admin_users (id, uuid, username, email, password_hash, role, is_active, failed_attempts, locked_until, last_login_at, created_at) FROM stdin;
\.


--
-- Data for Name: sc_cloud_connections; Type: TABLE DATA; Schema: source_connection; Owner: postgres
--

COPY source_connection.sc_cloud_connections (id, project_id, environment_id, tenant_id, created_by_user_id, owner, provider, auth_type, aws_region, access_key_masked, access_key_id, secret_key_hash, encrypted_secret, encryption_nonce, encryption_tag, encryption_key_id, role_arn, external_id, account_id, caller_arn, caller_user_id, status, last_validated_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: sc_git_connections; Type: TABLE DATA; Schema: source_connection; Owner: postgres
--

COPY source_connection.sc_git_connections (id, project_id, environment_id, tenant_id, created_by_user_id, owner, repo_url, repo_name, branch, pat_label, pat_token_hash, encrypted_pat, pat_nonce, pat_tag, auth_type, github_user, default_branch, last_commit_sha, last_commit_msg, last_commit_author, last_commit_at, is_private, stars, language, status, created_at, updated_at) FROM stdin;
11f782f3-5318-469b-aa4d-df222ec60c50	6cb0ef5f-af3a-45d6-94d1-3fbf025a09b5	ca6c1cc4-670b-4aed-b485-c3283268b585	tenant-000000000002	00000000-0000-0000-0000-000000000002	user	https://github.com/prathap-32/aetherops	prathap-32/aetherops	main	\N	$2b$10$lGm5.xZQzfpavqH6Juo/A.y7Bwvvo0LuC4ztmV7Nk.E9WMAFC9PI2	d9tJOGzP53XRioL15hVLF+zyIz/GIaciGcaKNhFAx/nxhedKQvVy1Q==	WfQheGP3YmLkFRVI	EC2Kn83IzDDcuHwlg5nTsA==	PAT	prathap-32	main	a0654570cbaf83cbd1dc1689390f2fb74c0021f4	fix(services): add persistence and database models for architecture and iac generators	prathap-32	2026-11-09 16:55:59.456699	t	\N	Python	CONNECTED	2026-11-09 16:55:59.456703	2026-11-09 16:55:59.456704
c0998ec1-7f42-4b75-9882-1e94dc2dff78	f63ec5e5-d28a-46d6-bba6-9e20a4b24dfe	af34ff98-b6f3-4ad1-bcb1-d6f74fee54c3	tenant-eb8e04f5597a9283	f6c6bfd2-0ef4-40ec-9e4c-f3d838dca864	prathap-32	https://github.com/prathap-32/Docker_webApp_analogClock	prathap-32/Docker_webApp_analogClock	main	\N	$2b$10$li0d.x/RHc8RsFk.ogi7ZemnWtzEC/UjyWB.sdBV3I8jf3ImBFOwe	NlAIIr7osYwhCftF7KmGyZlMuqEdCy8JWjeAJNcTfhMwGHENJhbAfA==	7+1pG4fIEGKcdZnq	Z/5xqIDzR1krB6zwU2Ktww==	PAT	prathap-32	main	afc08649b4d73c7dc666decc44b4f3797b04146b	png file	prathap-32	2026-11-10 07:54:44.700628	f	\N	CSS	CONNECTED	2026-11-10 07:54:44.700633	2026-11-10 07:54:44.700633
\.


--
-- Data for Name: sc_source_snapshots; Type: TABLE DATA; Schema: source_connection; Owner: postgres
--

COPY source_connection.sc_source_snapshots (id, connection_id, project_id, environment_id, commit_sha, branch, file_tree, detected_files, language_hints, total_files, total_size_kb, created_at) FROM stdin;
3904dca9-715d-4404-8dd6-17e865cc8a10	86c3d612-a95f-449c-8750-f2a89040249b	6cb0ef5f-af3a-45d6-94d1-3fbf025a09b5	ca6c1cc4-670b-4aed-b485-c3283268b585	c7e8c6d322a094bd78a2925e6ee358c0990c94f6	main	[{"path": "README.md", "type": "file", "size": 1840}, {"path": ".gitignore", "type": "file", "size": 420}, {"path": "Dockerfile", "type": "file", "size": 950}, {"path": ".github", "type": "dir", "size": 0}, {"path": ".github/workflows", "type": "dir", "size": 0}, {"path": ".github/workflows/ci.yml", "type": "file", "size": 1280}, {"path": "requirements.txt", "type": "file", "size": 780}, {"path": "pyproject.toml", "type": "file", "size": 540}, {"path": "docker-compose.yml", "type": "file", "size": 1150}, {"path": "src", "type": "dir", "size": 0}, {"path": "src/__init__.py", "type": "file", "size": 40}, {"path": "src/main.py", "type": "file", "size": 3600}, {"path": "src/models.py", "type": "file", "size": 2400}, {"path": "src/services.py", "type": "file", "size": 4100}, {"path": "tests", "type": "dir", "size": 0}, {"path": "tests/test_main.py", "type": "file", "size": 1900}, {"path": "deploy", "type": "dir", "size": 0}, {"path": "deploy/service.yaml", "type": "file", "size": 1600}]	{"dockerfile": true, "docker_compose": true, "requirements_txt": true, "package_json": false, "github_actions": true, "makefile": false, "kubernetes": true, "terraform": false}	{"primary": "Python", "others": []}	13	21	2026-11-09 16:11:01.637508
a2f64a69-b468-48d8-9054-bbc7f09c3f69	eea7a4e6-d09d-406e-9b61-7357bb425580	6cb0ef5f-af3a-45d6-94d1-3fbf025a09b5	ca6c1cc4-670b-4aed-b485-c3283268b585	c7e8c6d322a094bd78a2925e6ee358c0990c94f6	main	[{"path": "README.md", "type": "file", "size": 1840}, {"path": ".gitignore", "type": "file", "size": 420}, {"path": "Dockerfile", "type": "file", "size": 950}, {"path": ".github", "type": "dir", "size": 0}, {"path": ".github/workflows", "type": "dir", "size": 0}, {"path": ".github/workflows/ci.yml", "type": "file", "size": 1280}, {"path": "requirements.txt", "type": "file", "size": 780}, {"path": "pyproject.toml", "type": "file", "size": 540}, {"path": "docker-compose.yml", "type": "file", "size": 1150}, {"path": "src", "type": "dir", "size": 0}, {"path": "src/__init__.py", "type": "file", "size": 40}, {"path": "src/main.py", "type": "file", "size": 3600}, {"path": "src/models.py", "type": "file", "size": 2400}, {"path": "src/services.py", "type": "file", "size": 4100}, {"path": "tests", "type": "dir", "size": 0}, {"path": "tests/test_main.py", "type": "file", "size": 1900}, {"path": "deploy", "type": "dir", "size": 0}, {"path": "deploy/service.yaml", "type": "file", "size": 1600}]	{"dockerfile": true, "docker_compose": true, "requirements_txt": true, "package_json": false, "github_actions": true, "makefile": false, "kubernetes": true, "terraform": false}	{"primary": "Python", "others": []}	13	21	2026-11-09 16:11:06.68491
a13687e6-740b-4666-80a4-77ea969e6816	4ab31a0c-40ef-494f-9056-fa9318b0b139	6cb0ef5f-af3a-45d6-94d1-3fbf025a09b5	ca6c1cc4-670b-4aed-b485-c3283268b585	c7e8c6d322a094bd78a2925e6ee358c0990c94f6	main	[{"path": "README.md", "type": "file", "size": 1840}, {"path": ".gitignore", "type": "file", "size": 420}, {"path": "Dockerfile", "type": "file", "size": 950}, {"path": ".github", "type": "dir", "size": 0}, {"path": ".github/workflows", "type": "dir", "size": 0}, {"path": ".github/workflows/ci.yml", "type": "file", "size": 1280}, {"path": "requirements.txt", "type": "file", "size": 780}, {"path": "pyproject.toml", "type": "file", "size": 540}, {"path": "docker-compose.yml", "type": "file", "size": 1150}, {"path": "src", "type": "dir", "size": 0}, {"path": "src/__init__.py", "type": "file", "size": 40}, {"path": "src/main.py", "type": "file", "size": 3600}, {"path": "src/models.py", "type": "file", "size": 2400}, {"path": "src/services.py", "type": "file", "size": 4100}, {"path": "tests", "type": "dir", "size": 0}, {"path": "tests/test_main.py", "type": "file", "size": 1900}, {"path": "deploy", "type": "dir", "size": 0}, {"path": "deploy/service.yaml", "type": "file", "size": 1600}]	{"dockerfile": true, "docker_compose": true, "requirements_txt": true, "package_json": false, "github_actions": true, "makefile": false, "kubernetes": true, "terraform": false}	{"primary": "Python", "others": []}	13	21	2026-11-09 16:11:26.731769
730c606f-1c62-4d0f-9d32-575aa5257179	1bd63e53-b6ce-4395-beb3-537ebf7de359	6cb0ef5f-af3a-45d6-94d1-3fbf025a09b5	ca6c1cc4-670b-4aed-b485-c3283268b585	c7e2d58a65f1a5b412079b88be6b763d683cf285	main	[{"path": "README.md", "type": "file", "size": 1840}, {"path": ".gitignore", "type": "file", "size": 420}, {"path": "Dockerfile", "type": "file", "size": 950}, {"path": ".github", "type": "dir", "size": 0}, {"path": ".github/workflows", "type": "dir", "size": 0}, {"path": ".github/workflows/ci.yml", "type": "file", "size": 1280}, {"path": "requirements.txt", "type": "file", "size": 780}, {"path": "pyproject.toml", "type": "file", "size": 540}, {"path": "docker-compose.yml", "type": "file", "size": 1150}, {"path": "src", "type": "dir", "size": 0}, {"path": "src/__init__.py", "type": "file", "size": 40}, {"path": "src/main.py", "type": "file", "size": 3600}, {"path": "src/models.py", "type": "file", "size": 2400}, {"path": "src/services.py", "type": "file", "size": 4100}, {"path": "tests", "type": "dir", "size": 0}, {"path": "tests/test_main.py", "type": "file", "size": 1900}, {"path": "deploy", "type": "dir", "size": 0}, {"path": "deploy/service.yaml", "type": "file", "size": 1600}]	{"dockerfile": true, "docker_compose": true, "requirements_txt": true, "package_json": false, "github_actions": true, "makefile": false, "kubernetes": true, "terraform": false}	{"primary": "Python", "others": []}	13	21	2026-11-09 16:14:45.904121
47c0e899-2db9-47cc-ae52-deea301018fc	66096f87-c642-4c43-94ca-2c560f08d320	6cb0ef5f-af3a-45d6-94d1-3fbf025a09b5	ca6c1cc4-670b-4aed-b485-c3283268b585	c7e2d58a65f1a5b412079b88be6b763d683cf285	main	[{"path": "README.md", "type": "file", "size": 1840}, {"path": ".gitignore", "type": "file", "size": 420}, {"path": "Dockerfile", "type": "file", "size": 950}, {"path": ".github", "type": "dir", "size": 0}, {"path": ".github/workflows", "type": "dir", "size": 0}, {"path": ".github/workflows/ci.yml", "type": "file", "size": 1280}, {"path": "requirements.txt", "type": "file", "size": 780}, {"path": "pyproject.toml", "type": "file", "size": 540}, {"path": "docker-compose.yml", "type": "file", "size": 1150}, {"path": "src", "type": "dir", "size": 0}, {"path": "src/__init__.py", "type": "file", "size": 40}, {"path": "src/main.py", "type": "file", "size": 3600}, {"path": "src/models.py", "type": "file", "size": 2400}, {"path": "src/services.py", "type": "file", "size": 4100}, {"path": "tests", "type": "dir", "size": 0}, {"path": "tests/test_main.py", "type": "file", "size": 1900}, {"path": "deploy", "type": "dir", "size": 0}, {"path": "deploy/service.yaml", "type": "file", "size": 1600}]	{"dockerfile": true, "docker_compose": true, "requirements_txt": true, "package_json": false, "github_actions": true, "makefile": false, "kubernetes": true, "terraform": false}	{"primary": "Python", "others": []}	13	21	2026-11-09 16:14:54.64766
31d9eed5-1265-41ab-9d5a-4d184854e7b6	d21fb010-d81b-4284-b4a4-e5db5a82f8da	6cb0ef5f-af3a-45d6-94d1-3fbf025a09b5	ca6c1cc4-670b-4aed-b485-c3283268b585	c7e43edc6cdcec5f59aab93f3ba91bb44209cabd	main	[{"path": "README.md", "type": "file", "size": 1840}, {"path": ".gitignore", "type": "file", "size": 420}, {"path": "Dockerfile", "type": "file", "size": 950}, {"path": ".github", "type": "dir", "size": 0}, {"path": ".github/workflows", "type": "dir", "size": 0}, {"path": ".github/workflows/ci.yml", "type": "file", "size": 1280}, {"path": "requirements.txt", "type": "file", "size": 780}, {"path": "pyproject.toml", "type": "file", "size": 540}, {"path": "docker-compose.yml", "type": "file", "size": 1150}, {"path": "src", "type": "dir", "size": 0}, {"path": "src/__init__.py", "type": "file", "size": 40}, {"path": "src/main.py", "type": "file", "size": 3600}, {"path": "src/models.py", "type": "file", "size": 2400}, {"path": "src/services.py", "type": "file", "size": 4100}, {"path": "tests", "type": "dir", "size": 0}, {"path": "tests/test_main.py", "type": "file", "size": 1900}, {"path": "deploy", "type": "dir", "size": 0}, {"path": "deploy/service.yaml", "type": "file", "size": 1600}]	{"dockerfile": true, "docker_compose": true, "requirements_txt": true, "package_json": false, "github_actions": true, "makefile": false, "kubernetes": true, "terraform": false}	{"primary": "Python", "others": []}	13	21	2026-11-09 16:24:29.227357
\.


--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE SET; Schema: admin_security; Owner: postgres
--

SELECT pg_catalog.setval('admin_security.admin_audit_logs_id_seq', 1, false);


--
-- Name: admin_users_id_seq; Type: SEQUENCE SET; Schema: admin_security; Owner: postgres
--

SELECT pg_catalog.setval('admin_security.admin_users_id_seq', 1, true);


--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE SET; Schema: admin_security; Owner: postgres
--

SELECT pg_catalog.setval('admin_security.ec2_catalog_id_seq', 1, false);


--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE SET; Schema: admin_security; Owner: postgres
--

SELECT pg_catalog.setval('admin_security.generic_service_catalog_id_seq', 1, false);


--
-- Name: rds_catalog_id_seq; Type: SEQUENCE SET; Schema: admin_security; Owner: postgres
--

SELECT pg_catalog.setval('admin_security.rds_catalog_id_seq', 1, false);


--
-- Name: sync_metadata_id_seq; Type: SEQUENCE SET; Schema: admin_security; Owner: postgres
--

SELECT pg_catalog.setval('admin_security.sync_metadata_id_seq', 1, false);


--
-- Name: pm_admin_audit_logs_id_seq; Type: SEQUENCE SET; Schema: project_manager; Owner: postgres
--

SELECT pg_catalog.setval('project_manager.pm_admin_audit_logs_id_seq', 1, false);


--
-- Name: pm_admin_users_id_seq; Type: SEQUENCE SET; Schema: project_manager; Owner: postgres
--

SELECT pg_catalog.setval('project_manager.pm_admin_users_id_seq', 1, true);


--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE SET; Schema: region_ca_central_1; Owner: postgres
--

SELECT pg_catalog.setval('region_ca_central_1.admin_audit_logs_id_seq', 1, false);


--
-- Name: admin_users_id_seq; Type: SEQUENCE SET; Schema: region_ca_central_1; Owner: postgres
--

SELECT pg_catalog.setval('region_ca_central_1.admin_users_id_seq', 1, false);


--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE SET; Schema: region_ca_central_1; Owner: postgres
--

SELECT pg_catalog.setval('region_ca_central_1.ec2_catalog_id_seq', 1, false);


--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE SET; Schema: region_ca_central_1; Owner: postgres
--

SELECT pg_catalog.setval('region_ca_central_1.generic_service_catalog_id_seq', 1, false);


--
-- Name: rds_catalog_id_seq; Type: SEQUENCE SET; Schema: region_ca_central_1; Owner: postgres
--

SELECT pg_catalog.setval('region_ca_central_1.rds_catalog_id_seq', 1, false);


--
-- Name: sync_metadata_id_seq; Type: SEQUENCE SET; Schema: region_ca_central_1; Owner: postgres
--

SELECT pg_catalog.setval('region_ca_central_1.sync_metadata_id_seq', 1, false);


--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE SET; Schema: region_ca_west_1; Owner: postgres
--

SELECT pg_catalog.setval('region_ca_west_1.admin_audit_logs_id_seq', 1, false);


--
-- Name: admin_users_id_seq; Type: SEQUENCE SET; Schema: region_ca_west_1; Owner: postgres
--

SELECT pg_catalog.setval('region_ca_west_1.admin_users_id_seq', 1, false);


--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE SET; Schema: region_ca_west_1; Owner: postgres
--

SELECT pg_catalog.setval('region_ca_west_1.ec2_catalog_id_seq', 1, false);


--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE SET; Schema: region_ca_west_1; Owner: postgres
--

SELECT pg_catalog.setval('region_ca_west_1.generic_service_catalog_id_seq', 1, false);


--
-- Name: rds_catalog_id_seq; Type: SEQUENCE SET; Schema: region_ca_west_1; Owner: postgres
--

SELECT pg_catalog.setval('region_ca_west_1.rds_catalog_id_seq', 1, false);


--
-- Name: sync_metadata_id_seq; Type: SEQUENCE SET; Schema: region_ca_west_1; Owner: postgres
--

SELECT pg_catalog.setval('region_ca_west_1.sync_metadata_id_seq', 1, false);


--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE SET; Schema: region_mx_central_1; Owner: postgres
--

SELECT pg_catalog.setval('region_mx_central_1.admin_audit_logs_id_seq', 1, false);


--
-- Name: admin_users_id_seq; Type: SEQUENCE SET; Schema: region_mx_central_1; Owner: postgres
--

SELECT pg_catalog.setval('region_mx_central_1.admin_users_id_seq', 1, false);


--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE SET; Schema: region_mx_central_1; Owner: postgres
--

SELECT pg_catalog.setval('region_mx_central_1.ec2_catalog_id_seq', 1, false);


--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE SET; Schema: region_mx_central_1; Owner: postgres
--

SELECT pg_catalog.setval('region_mx_central_1.generic_service_catalog_id_seq', 1, false);


--
-- Name: rds_catalog_id_seq; Type: SEQUENCE SET; Schema: region_mx_central_1; Owner: postgres
--

SELECT pg_catalog.setval('region_mx_central_1.rds_catalog_id_seq', 1, false);


--
-- Name: sync_metadata_id_seq; Type: SEQUENCE SET; Schema: region_mx_central_1; Owner: postgres
--

SELECT pg_catalog.setval('region_mx_central_1.sync_metadata_id_seq', 1, false);


--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE SET; Schema: region_sa_east_1; Owner: postgres
--

SELECT pg_catalog.setval('region_sa_east_1.admin_audit_logs_id_seq', 1, false);


--
-- Name: admin_users_id_seq; Type: SEQUENCE SET; Schema: region_sa_east_1; Owner: postgres
--

SELECT pg_catalog.setval('region_sa_east_1.admin_users_id_seq', 1, false);


--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE SET; Schema: region_sa_east_1; Owner: postgres
--

SELECT pg_catalog.setval('region_sa_east_1.ec2_catalog_id_seq', 1, false);


--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE SET; Schema: region_sa_east_1; Owner: postgres
--

SELECT pg_catalog.setval('region_sa_east_1.generic_service_catalog_id_seq', 1, false);


--
-- Name: rds_catalog_id_seq; Type: SEQUENCE SET; Schema: region_sa_east_1; Owner: postgres
--

SELECT pg_catalog.setval('region_sa_east_1.rds_catalog_id_seq', 1, false);


--
-- Name: sync_metadata_id_seq; Type: SEQUENCE SET; Schema: region_sa_east_1; Owner: postgres
--

SELECT pg_catalog.setval('region_sa_east_1.sync_metadata_id_seq', 1, false);


--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE SET; Schema: region_us_east_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_east_1.admin_audit_logs_id_seq', 1, false);


--
-- Name: admin_users_id_seq; Type: SEQUENCE SET; Schema: region_us_east_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_east_1.admin_users_id_seq', 1, false);


--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE SET; Schema: region_us_east_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_east_1.ec2_catalog_id_seq', 1, false);


--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE SET; Schema: region_us_east_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_east_1.generic_service_catalog_id_seq', 1, false);


--
-- Name: rds_catalog_id_seq; Type: SEQUENCE SET; Schema: region_us_east_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_east_1.rds_catalog_id_seq', 1, false);


--
-- Name: sync_metadata_id_seq; Type: SEQUENCE SET; Schema: region_us_east_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_east_1.sync_metadata_id_seq', 1, false);


--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE SET; Schema: region_us_east_2; Owner: postgres
--

SELECT pg_catalog.setval('region_us_east_2.admin_audit_logs_id_seq', 1, false);


--
-- Name: admin_users_id_seq; Type: SEQUENCE SET; Schema: region_us_east_2; Owner: postgres
--

SELECT pg_catalog.setval('region_us_east_2.admin_users_id_seq', 1, false);


--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE SET; Schema: region_us_east_2; Owner: postgres
--

SELECT pg_catalog.setval('region_us_east_2.ec2_catalog_id_seq', 1, false);


--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE SET; Schema: region_us_east_2; Owner: postgres
--

SELECT pg_catalog.setval('region_us_east_2.generic_service_catalog_id_seq', 1, false);


--
-- Name: rds_catalog_id_seq; Type: SEQUENCE SET; Schema: region_us_east_2; Owner: postgres
--

SELECT pg_catalog.setval('region_us_east_2.rds_catalog_id_seq', 1, false);


--
-- Name: sync_metadata_id_seq; Type: SEQUENCE SET; Schema: region_us_east_2; Owner: postgres
--

SELECT pg_catalog.setval('region_us_east_2.sync_metadata_id_seq', 1, false);


--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE SET; Schema: region_us_gov_east_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_gov_east_1.admin_audit_logs_id_seq', 1, false);


--
-- Name: admin_users_id_seq; Type: SEQUENCE SET; Schema: region_us_gov_east_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_gov_east_1.admin_users_id_seq', 1, false);


--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE SET; Schema: region_us_gov_east_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_gov_east_1.ec2_catalog_id_seq', 1, false);


--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE SET; Schema: region_us_gov_east_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_gov_east_1.generic_service_catalog_id_seq', 1, false);


--
-- Name: rds_catalog_id_seq; Type: SEQUENCE SET; Schema: region_us_gov_east_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_gov_east_1.rds_catalog_id_seq', 1, false);


--
-- Name: sync_metadata_id_seq; Type: SEQUENCE SET; Schema: region_us_gov_east_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_gov_east_1.sync_metadata_id_seq', 1, false);


--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE SET; Schema: region_us_gov_west_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_gov_west_1.admin_audit_logs_id_seq', 1, false);


--
-- Name: admin_users_id_seq; Type: SEQUENCE SET; Schema: region_us_gov_west_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_gov_west_1.admin_users_id_seq', 1, false);


--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE SET; Schema: region_us_gov_west_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_gov_west_1.ec2_catalog_id_seq', 1, false);


--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE SET; Schema: region_us_gov_west_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_gov_west_1.generic_service_catalog_id_seq', 1, false);


--
-- Name: rds_catalog_id_seq; Type: SEQUENCE SET; Schema: region_us_gov_west_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_gov_west_1.rds_catalog_id_seq', 1, false);


--
-- Name: sync_metadata_id_seq; Type: SEQUENCE SET; Schema: region_us_gov_west_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_gov_west_1.sync_metadata_id_seq', 1, false);


--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE SET; Schema: region_us_west_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_west_1.admin_audit_logs_id_seq', 1, false);


--
-- Name: admin_users_id_seq; Type: SEQUENCE SET; Schema: region_us_west_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_west_1.admin_users_id_seq', 1, false);


--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE SET; Schema: region_us_west_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_west_1.ec2_catalog_id_seq', 1, false);


--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE SET; Schema: region_us_west_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_west_1.generic_service_catalog_id_seq', 1, false);


--
-- Name: rds_catalog_id_seq; Type: SEQUENCE SET; Schema: region_us_west_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_west_1.rds_catalog_id_seq', 1, false);


--
-- Name: sync_metadata_id_seq; Type: SEQUENCE SET; Schema: region_us_west_1; Owner: postgres
--

SELECT pg_catalog.setval('region_us_west_1.sync_metadata_id_seq', 1, false);


--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE SET; Schema: region_us_west_2; Owner: postgres
--

SELECT pg_catalog.setval('region_us_west_2.admin_audit_logs_id_seq', 1, false);


--
-- Name: admin_users_id_seq; Type: SEQUENCE SET; Schema: region_us_west_2; Owner: postgres
--

SELECT pg_catalog.setval('region_us_west_2.admin_users_id_seq', 1, false);


--
-- Name: ec2_catalog_id_seq; Type: SEQUENCE SET; Schema: region_us_west_2; Owner: postgres
--

SELECT pg_catalog.setval('region_us_west_2.ec2_catalog_id_seq', 1, false);


--
-- Name: generic_service_catalog_id_seq; Type: SEQUENCE SET; Schema: region_us_west_2; Owner: postgres
--

SELECT pg_catalog.setval('region_us_west_2.generic_service_catalog_id_seq', 1, false);


--
-- Name: rds_catalog_id_seq; Type: SEQUENCE SET; Schema: region_us_west_2; Owner: postgres
--

SELECT pg_catalog.setval('region_us_west_2.rds_catalog_id_seq', 1, false);


--
-- Name: sync_metadata_id_seq; Type: SEQUENCE SET; Schema: region_us_west_2; Owner: postgres
--

SELECT pg_catalog.setval('region_us_west_2.sync_metadata_id_seq', 1, false);


--
-- Name: sc_admin_audit_logs_id_seq; Type: SEQUENCE SET; Schema: source_connection; Owner: postgres
--

SELECT pg_catalog.setval('source_connection.sc_admin_audit_logs_id_seq', 1, false);


--
-- Name: sc_admin_users_id_seq; Type: SEQUENCE SET; Schema: source_connection; Owner: postgres
--

SELECT pg_catalog.setval('source_connection.sc_admin_users_id_seq', 1, false);


--
-- Name: generic_service_catalog _service_instance_uc; Type: CONSTRAINT; Schema: admin_security; Owner: postgres
--

ALTER TABLE ONLY admin_security.generic_service_catalog
    ADD CONSTRAINT _service_instance_uc UNIQUE (service, instance_type);


--
-- Name: admin_audit_logs admin_audit_logs_pkey; Type: CONSTRAINT; Schema: admin_security; Owner: postgres
--

ALTER TABLE ONLY admin_security.admin_audit_logs
    ADD CONSTRAINT admin_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: admin_users admin_users_pkey; Type: CONSTRAINT; Schema: admin_security; Owner: postgres
--

ALTER TABLE ONLY admin_security.admin_users
    ADD CONSTRAINT admin_users_pkey PRIMARY KEY (id);


--
-- Name: ec2_catalog ec2_catalog_pkey; Type: CONSTRAINT; Schema: admin_security; Owner: postgres
--

ALTER TABLE ONLY admin_security.ec2_catalog
    ADD CONSTRAINT ec2_catalog_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog generic_service_catalog_pkey; Type: CONSTRAINT; Schema: admin_security; Owner: postgres
--

ALTER TABLE ONLY admin_security.generic_service_catalog
    ADD CONSTRAINT generic_service_catalog_pkey PRIMARY KEY (id);


--
-- Name: rds_catalog rds_catalog_pkey; Type: CONSTRAINT; Schema: admin_security; Owner: postgres
--

ALTER TABLE ONLY admin_security.rds_catalog
    ADD CONSTRAINT rds_catalog_pkey PRIMARY KEY (id);


--
-- Name: requirement_projects requirement_projects_pkey; Type: CONSTRAINT; Schema: admin_security; Owner: postgres
--

ALTER TABLE ONLY admin_security.requirement_projects
    ADD CONSTRAINT requirement_projects_pkey PRIMARY KEY (id);


--
-- Name: sync_metadata sync_metadata_pkey; Type: CONSTRAINT; Schema: admin_security; Owner: postgres
--

ALTER TABLE ONLY admin_security.sync_metadata
    ADD CONSTRAINT sync_metadata_pkey PRIMARY KEY (id);


--
-- Name: architecture_versions architecture_versions_pkey; Type: CONSTRAINT; Schema: architecture; Owner: postgres
--

ALTER TABLE ONLY architecture.architecture_versions
    ADD CONSTRAINT architecture_versions_pkey PRIMARY KEY (version_id);


--
-- Name: studio_sessions studio_sessions_pkey; Type: CONSTRAINT; Schema: architecture; Owner: postgres
--

ALTER TABLE ONLY architecture.studio_sessions
    ADD CONSTRAINT studio_sessions_pkey PRIMARY KEY (session_id);


--
-- Name: generated_iac_bundles generated_iac_bundles_pkey; Type: CONSTRAINT; Schema: iac; Owner: postgres
--

ALTER TABLE ONLY iac.generated_iac_bundles
    ADD CONSTRAINT generated_iac_bundles_pkey PRIMARY KEY (terraform_version_id);


--
-- Name: aether_environments _project_env_name_uc; Type: CONSTRAINT; Schema: project_manager; Owner: postgres
--

ALTER TABLE ONLY project_manager.aether_environments
    ADD CONSTRAINT _project_env_name_uc UNIQUE (project_id, name);


--
-- Name: aether_tenant_memberships _tenant_user_uc; Type: CONSTRAINT; Schema: project_manager; Owner: postgres
--

ALTER TABLE ONLY project_manager.aether_tenant_memberships
    ADD CONSTRAINT _tenant_user_uc UNIQUE (tenant_id, user_id);


--
-- Name: aether_dashboard_preferences aether_dashboard_preferences_pkey; Type: CONSTRAINT; Schema: project_manager; Owner: postgres
--

ALTER TABLE ONLY project_manager.aether_dashboard_preferences
    ADD CONSTRAINT aether_dashboard_preferences_pkey PRIMARY KEY (id);


--
-- Name: aether_environments aether_environments_pkey; Type: CONSTRAINT; Schema: project_manager; Owner: postgres
--

ALTER TABLE ONLY project_manager.aether_environments
    ADD CONSTRAINT aether_environments_pkey PRIMARY KEY (id);


--
-- Name: aether_projects aether_projects_pkey; Type: CONSTRAINT; Schema: project_manager; Owner: postgres
--

ALTER TABLE ONLY project_manager.aether_projects
    ADD CONSTRAINT aether_projects_pkey PRIMARY KEY (id);


--
-- Name: aether_tenant_memberships aether_tenant_memberships_pkey; Type: CONSTRAINT; Schema: project_manager; Owner: postgres
--

ALTER TABLE ONLY project_manager.aether_tenant_memberships
    ADD CONSTRAINT aether_tenant_memberships_pkey PRIMARY KEY (id);


--
-- Name: aether_tenants aether_tenants_pkey; Type: CONSTRAINT; Schema: project_manager; Owner: postgres
--

ALTER TABLE ONLY project_manager.aether_tenants
    ADD CONSTRAINT aether_tenants_pkey PRIMARY KEY (id);


--
-- Name: pm_admin_audit_logs pm_admin_audit_logs_pkey; Type: CONSTRAINT; Schema: project_manager; Owner: postgres
--

ALTER TABLE ONLY project_manager.pm_admin_audit_logs
    ADD CONSTRAINT pm_admin_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: pm_admin_users pm_admin_users_pkey; Type: CONSTRAINT; Schema: project_manager; Owner: postgres
--

ALTER TABLE ONLY project_manager.pm_admin_users
    ADD CONSTRAINT pm_admin_users_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog _service_instance_uc; Type: CONSTRAINT; Schema: region_ca_central_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_central_1.generic_service_catalog
    ADD CONSTRAINT _service_instance_uc UNIQUE (service, instance_type);


--
-- Name: admin_audit_logs admin_audit_logs_pkey; Type: CONSTRAINT; Schema: region_ca_central_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_central_1.admin_audit_logs
    ADD CONSTRAINT admin_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: admin_users admin_users_pkey; Type: CONSTRAINT; Schema: region_ca_central_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_central_1.admin_users
    ADD CONSTRAINT admin_users_pkey PRIMARY KEY (id);


--
-- Name: ec2_catalog ec2_catalog_pkey; Type: CONSTRAINT; Schema: region_ca_central_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_central_1.ec2_catalog
    ADD CONSTRAINT ec2_catalog_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog generic_service_catalog_pkey; Type: CONSTRAINT; Schema: region_ca_central_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_central_1.generic_service_catalog
    ADD CONSTRAINT generic_service_catalog_pkey PRIMARY KEY (id);


--
-- Name: rds_catalog rds_catalog_pkey; Type: CONSTRAINT; Schema: region_ca_central_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_central_1.rds_catalog
    ADD CONSTRAINT rds_catalog_pkey PRIMARY KEY (id);


--
-- Name: requirement_projects requirement_projects_pkey; Type: CONSTRAINT; Schema: region_ca_central_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_central_1.requirement_projects
    ADD CONSTRAINT requirement_projects_pkey PRIMARY KEY (id);


--
-- Name: sync_metadata sync_metadata_pkey; Type: CONSTRAINT; Schema: region_ca_central_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_central_1.sync_metadata
    ADD CONSTRAINT sync_metadata_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog _service_instance_uc; Type: CONSTRAINT; Schema: region_ca_west_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_west_1.generic_service_catalog
    ADD CONSTRAINT _service_instance_uc UNIQUE (service, instance_type);


--
-- Name: admin_audit_logs admin_audit_logs_pkey; Type: CONSTRAINT; Schema: region_ca_west_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_west_1.admin_audit_logs
    ADD CONSTRAINT admin_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: admin_users admin_users_pkey; Type: CONSTRAINT; Schema: region_ca_west_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_west_1.admin_users
    ADD CONSTRAINT admin_users_pkey PRIMARY KEY (id);


--
-- Name: ec2_catalog ec2_catalog_pkey; Type: CONSTRAINT; Schema: region_ca_west_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_west_1.ec2_catalog
    ADD CONSTRAINT ec2_catalog_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog generic_service_catalog_pkey; Type: CONSTRAINT; Schema: region_ca_west_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_west_1.generic_service_catalog
    ADD CONSTRAINT generic_service_catalog_pkey PRIMARY KEY (id);


--
-- Name: rds_catalog rds_catalog_pkey; Type: CONSTRAINT; Schema: region_ca_west_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_west_1.rds_catalog
    ADD CONSTRAINT rds_catalog_pkey PRIMARY KEY (id);


--
-- Name: requirement_projects requirement_projects_pkey; Type: CONSTRAINT; Schema: region_ca_west_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_west_1.requirement_projects
    ADD CONSTRAINT requirement_projects_pkey PRIMARY KEY (id);


--
-- Name: sync_metadata sync_metadata_pkey; Type: CONSTRAINT; Schema: region_ca_west_1; Owner: postgres
--

ALTER TABLE ONLY region_ca_west_1.sync_metadata
    ADD CONSTRAINT sync_metadata_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog _service_instance_uc; Type: CONSTRAINT; Schema: region_mx_central_1; Owner: postgres
--

ALTER TABLE ONLY region_mx_central_1.generic_service_catalog
    ADD CONSTRAINT _service_instance_uc UNIQUE (service, instance_type);


--
-- Name: admin_audit_logs admin_audit_logs_pkey; Type: CONSTRAINT; Schema: region_mx_central_1; Owner: postgres
--

ALTER TABLE ONLY region_mx_central_1.admin_audit_logs
    ADD CONSTRAINT admin_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: admin_users admin_users_pkey; Type: CONSTRAINT; Schema: region_mx_central_1; Owner: postgres
--

ALTER TABLE ONLY region_mx_central_1.admin_users
    ADD CONSTRAINT admin_users_pkey PRIMARY KEY (id);


--
-- Name: ec2_catalog ec2_catalog_pkey; Type: CONSTRAINT; Schema: region_mx_central_1; Owner: postgres
--

ALTER TABLE ONLY region_mx_central_1.ec2_catalog
    ADD CONSTRAINT ec2_catalog_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog generic_service_catalog_pkey; Type: CONSTRAINT; Schema: region_mx_central_1; Owner: postgres
--

ALTER TABLE ONLY region_mx_central_1.generic_service_catalog
    ADD CONSTRAINT generic_service_catalog_pkey PRIMARY KEY (id);


--
-- Name: rds_catalog rds_catalog_pkey; Type: CONSTRAINT; Schema: region_mx_central_1; Owner: postgres
--

ALTER TABLE ONLY region_mx_central_1.rds_catalog
    ADD CONSTRAINT rds_catalog_pkey PRIMARY KEY (id);


--
-- Name: requirement_projects requirement_projects_pkey; Type: CONSTRAINT; Schema: region_mx_central_1; Owner: postgres
--

ALTER TABLE ONLY region_mx_central_1.requirement_projects
    ADD CONSTRAINT requirement_projects_pkey PRIMARY KEY (id);


--
-- Name: sync_metadata sync_metadata_pkey; Type: CONSTRAINT; Schema: region_mx_central_1; Owner: postgres
--

ALTER TABLE ONLY region_mx_central_1.sync_metadata
    ADD CONSTRAINT sync_metadata_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog _service_instance_uc; Type: CONSTRAINT; Schema: region_sa_east_1; Owner: postgres
--

ALTER TABLE ONLY region_sa_east_1.generic_service_catalog
    ADD CONSTRAINT _service_instance_uc UNIQUE (service, instance_type);


--
-- Name: admin_audit_logs admin_audit_logs_pkey; Type: CONSTRAINT; Schema: region_sa_east_1; Owner: postgres
--

ALTER TABLE ONLY region_sa_east_1.admin_audit_logs
    ADD CONSTRAINT admin_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: admin_users admin_users_pkey; Type: CONSTRAINT; Schema: region_sa_east_1; Owner: postgres
--

ALTER TABLE ONLY region_sa_east_1.admin_users
    ADD CONSTRAINT admin_users_pkey PRIMARY KEY (id);


--
-- Name: ec2_catalog ec2_catalog_pkey; Type: CONSTRAINT; Schema: region_sa_east_1; Owner: postgres
--

ALTER TABLE ONLY region_sa_east_1.ec2_catalog
    ADD CONSTRAINT ec2_catalog_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog generic_service_catalog_pkey; Type: CONSTRAINT; Schema: region_sa_east_1; Owner: postgres
--

ALTER TABLE ONLY region_sa_east_1.generic_service_catalog
    ADD CONSTRAINT generic_service_catalog_pkey PRIMARY KEY (id);


--
-- Name: rds_catalog rds_catalog_pkey; Type: CONSTRAINT; Schema: region_sa_east_1; Owner: postgres
--

ALTER TABLE ONLY region_sa_east_1.rds_catalog
    ADD CONSTRAINT rds_catalog_pkey PRIMARY KEY (id);


--
-- Name: requirement_projects requirement_projects_pkey; Type: CONSTRAINT; Schema: region_sa_east_1; Owner: postgres
--

ALTER TABLE ONLY region_sa_east_1.requirement_projects
    ADD CONSTRAINT requirement_projects_pkey PRIMARY KEY (id);


--
-- Name: sync_metadata sync_metadata_pkey; Type: CONSTRAINT; Schema: region_sa_east_1; Owner: postgres
--

ALTER TABLE ONLY region_sa_east_1.sync_metadata
    ADD CONSTRAINT sync_metadata_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog _service_instance_uc; Type: CONSTRAINT; Schema: region_us_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_east_1.generic_service_catalog
    ADD CONSTRAINT _service_instance_uc UNIQUE (service, instance_type);


--
-- Name: admin_audit_logs admin_audit_logs_pkey; Type: CONSTRAINT; Schema: region_us_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_east_1.admin_audit_logs
    ADD CONSTRAINT admin_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: admin_users admin_users_pkey; Type: CONSTRAINT; Schema: region_us_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_east_1.admin_users
    ADD CONSTRAINT admin_users_pkey PRIMARY KEY (id);


--
-- Name: ec2_catalog ec2_catalog_pkey; Type: CONSTRAINT; Schema: region_us_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_east_1.ec2_catalog
    ADD CONSTRAINT ec2_catalog_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog generic_service_catalog_pkey; Type: CONSTRAINT; Schema: region_us_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_east_1.generic_service_catalog
    ADD CONSTRAINT generic_service_catalog_pkey PRIMARY KEY (id);


--
-- Name: rds_catalog rds_catalog_pkey; Type: CONSTRAINT; Schema: region_us_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_east_1.rds_catalog
    ADD CONSTRAINT rds_catalog_pkey PRIMARY KEY (id);


--
-- Name: requirement_projects requirement_projects_pkey; Type: CONSTRAINT; Schema: region_us_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_east_1.requirement_projects
    ADD CONSTRAINT requirement_projects_pkey PRIMARY KEY (id);


--
-- Name: sync_metadata sync_metadata_pkey; Type: CONSTRAINT; Schema: region_us_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_east_1.sync_metadata
    ADD CONSTRAINT sync_metadata_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog _service_instance_uc; Type: CONSTRAINT; Schema: region_us_east_2; Owner: postgres
--

ALTER TABLE ONLY region_us_east_2.generic_service_catalog
    ADD CONSTRAINT _service_instance_uc UNIQUE (service, instance_type);


--
-- Name: admin_audit_logs admin_audit_logs_pkey; Type: CONSTRAINT; Schema: region_us_east_2; Owner: postgres
--

ALTER TABLE ONLY region_us_east_2.admin_audit_logs
    ADD CONSTRAINT admin_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: admin_users admin_users_pkey; Type: CONSTRAINT; Schema: region_us_east_2; Owner: postgres
--

ALTER TABLE ONLY region_us_east_2.admin_users
    ADD CONSTRAINT admin_users_pkey PRIMARY KEY (id);


--
-- Name: ec2_catalog ec2_catalog_pkey; Type: CONSTRAINT; Schema: region_us_east_2; Owner: postgres
--

ALTER TABLE ONLY region_us_east_2.ec2_catalog
    ADD CONSTRAINT ec2_catalog_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog generic_service_catalog_pkey; Type: CONSTRAINT; Schema: region_us_east_2; Owner: postgres
--

ALTER TABLE ONLY region_us_east_2.generic_service_catalog
    ADD CONSTRAINT generic_service_catalog_pkey PRIMARY KEY (id);


--
-- Name: rds_catalog rds_catalog_pkey; Type: CONSTRAINT; Schema: region_us_east_2; Owner: postgres
--

ALTER TABLE ONLY region_us_east_2.rds_catalog
    ADD CONSTRAINT rds_catalog_pkey PRIMARY KEY (id);


--
-- Name: requirement_projects requirement_projects_pkey; Type: CONSTRAINT; Schema: region_us_east_2; Owner: postgres
--

ALTER TABLE ONLY region_us_east_2.requirement_projects
    ADD CONSTRAINT requirement_projects_pkey PRIMARY KEY (id);


--
-- Name: sync_metadata sync_metadata_pkey; Type: CONSTRAINT; Schema: region_us_east_2; Owner: postgres
--

ALTER TABLE ONLY region_us_east_2.sync_metadata
    ADD CONSTRAINT sync_metadata_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog _service_instance_uc; Type: CONSTRAINT; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_east_1.generic_service_catalog
    ADD CONSTRAINT _service_instance_uc UNIQUE (service, instance_type);


--
-- Name: admin_audit_logs admin_audit_logs_pkey; Type: CONSTRAINT; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_east_1.admin_audit_logs
    ADD CONSTRAINT admin_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: admin_users admin_users_pkey; Type: CONSTRAINT; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_east_1.admin_users
    ADD CONSTRAINT admin_users_pkey PRIMARY KEY (id);


--
-- Name: ec2_catalog ec2_catalog_pkey; Type: CONSTRAINT; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_east_1.ec2_catalog
    ADD CONSTRAINT ec2_catalog_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog generic_service_catalog_pkey; Type: CONSTRAINT; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_east_1.generic_service_catalog
    ADD CONSTRAINT generic_service_catalog_pkey PRIMARY KEY (id);


--
-- Name: rds_catalog rds_catalog_pkey; Type: CONSTRAINT; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_east_1.rds_catalog
    ADD CONSTRAINT rds_catalog_pkey PRIMARY KEY (id);


--
-- Name: requirement_projects requirement_projects_pkey; Type: CONSTRAINT; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_east_1.requirement_projects
    ADD CONSTRAINT requirement_projects_pkey PRIMARY KEY (id);


--
-- Name: sync_metadata sync_metadata_pkey; Type: CONSTRAINT; Schema: region_us_gov_east_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_east_1.sync_metadata
    ADD CONSTRAINT sync_metadata_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog _service_instance_uc; Type: CONSTRAINT; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_west_1.generic_service_catalog
    ADD CONSTRAINT _service_instance_uc UNIQUE (service, instance_type);


--
-- Name: admin_audit_logs admin_audit_logs_pkey; Type: CONSTRAINT; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_west_1.admin_audit_logs
    ADD CONSTRAINT admin_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: admin_users admin_users_pkey; Type: CONSTRAINT; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_west_1.admin_users
    ADD CONSTRAINT admin_users_pkey PRIMARY KEY (id);


--
-- Name: ec2_catalog ec2_catalog_pkey; Type: CONSTRAINT; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_west_1.ec2_catalog
    ADD CONSTRAINT ec2_catalog_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog generic_service_catalog_pkey; Type: CONSTRAINT; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_west_1.generic_service_catalog
    ADD CONSTRAINT generic_service_catalog_pkey PRIMARY KEY (id);


--
-- Name: rds_catalog rds_catalog_pkey; Type: CONSTRAINT; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_west_1.rds_catalog
    ADD CONSTRAINT rds_catalog_pkey PRIMARY KEY (id);


--
-- Name: requirement_projects requirement_projects_pkey; Type: CONSTRAINT; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_west_1.requirement_projects
    ADD CONSTRAINT requirement_projects_pkey PRIMARY KEY (id);


--
-- Name: sync_metadata sync_metadata_pkey; Type: CONSTRAINT; Schema: region_us_gov_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_gov_west_1.sync_metadata
    ADD CONSTRAINT sync_metadata_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog _service_instance_uc; Type: CONSTRAINT; Schema: region_us_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_west_1.generic_service_catalog
    ADD CONSTRAINT _service_instance_uc UNIQUE (service, instance_type);


--
-- Name: admin_audit_logs admin_audit_logs_pkey; Type: CONSTRAINT; Schema: region_us_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_west_1.admin_audit_logs
    ADD CONSTRAINT admin_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: admin_users admin_users_pkey; Type: CONSTRAINT; Schema: region_us_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_west_1.admin_users
    ADD CONSTRAINT admin_users_pkey PRIMARY KEY (id);


--
-- Name: ec2_catalog ec2_catalog_pkey; Type: CONSTRAINT; Schema: region_us_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_west_1.ec2_catalog
    ADD CONSTRAINT ec2_catalog_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog generic_service_catalog_pkey; Type: CONSTRAINT; Schema: region_us_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_west_1.generic_service_catalog
    ADD CONSTRAINT generic_service_catalog_pkey PRIMARY KEY (id);


--
-- Name: rds_catalog rds_catalog_pkey; Type: CONSTRAINT; Schema: region_us_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_west_1.rds_catalog
    ADD CONSTRAINT rds_catalog_pkey PRIMARY KEY (id);


--
-- Name: requirement_projects requirement_projects_pkey; Type: CONSTRAINT; Schema: region_us_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_west_1.requirement_projects
    ADD CONSTRAINT requirement_projects_pkey PRIMARY KEY (id);


--
-- Name: sync_metadata sync_metadata_pkey; Type: CONSTRAINT; Schema: region_us_west_1; Owner: postgres
--

ALTER TABLE ONLY region_us_west_1.sync_metadata
    ADD CONSTRAINT sync_metadata_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog _service_instance_uc; Type: CONSTRAINT; Schema: region_us_west_2; Owner: postgres
--

ALTER TABLE ONLY region_us_west_2.generic_service_catalog
    ADD CONSTRAINT _service_instance_uc UNIQUE (service, instance_type);


--
-- Name: admin_audit_logs admin_audit_logs_pkey; Type: CONSTRAINT; Schema: region_us_west_2; Owner: postgres
--

ALTER TABLE ONLY region_us_west_2.admin_audit_logs
    ADD CONSTRAINT admin_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: admin_users admin_users_pkey; Type: CONSTRAINT; Schema: region_us_west_2; Owner: postgres
--

ALTER TABLE ONLY region_us_west_2.admin_users
    ADD CONSTRAINT admin_users_pkey PRIMARY KEY (id);


--
-- Name: ec2_catalog ec2_catalog_pkey; Type: CONSTRAINT; Schema: region_us_west_2; Owner: postgres
--

ALTER TABLE ONLY region_us_west_2.ec2_catalog
    ADD CONSTRAINT ec2_catalog_pkey PRIMARY KEY (id);


--
-- Name: generic_service_catalog generic_service_catalog_pkey; Type: CONSTRAINT; Schema: region_us_west_2; Owner: postgres
--

ALTER TABLE ONLY region_us_west_2.generic_service_catalog
    ADD CONSTRAINT generic_service_catalog_pkey PRIMARY KEY (id);


--
-- Name: rds_catalog rds_catalog_pkey; Type: CONSTRAINT; Schema: region_us_west_2; Owner: postgres
--

ALTER TABLE ONLY region_us_west_2.rds_catalog
    ADD CONSTRAINT rds_catalog_pkey PRIMARY KEY (id);


--
-- Name: requirement_projects requirement_projects_pkey; Type: CONSTRAINT; Schema: region_us_west_2; Owner: postgres
--

ALTER TABLE ONLY region_us_west_2.requirement_projects
    ADD CONSTRAINT requirement_projects_pkey PRIMARY KEY (id);


--
-- Name: sync_metadata sync_metadata_pkey; Type: CONSTRAINT; Schema: region_us_west_2; Owner: postgres
--

ALTER TABLE ONLY region_us_west_2.sync_metadata
    ADD CONSTRAINT sync_metadata_pkey PRIMARY KEY (id);


--
-- Name: sc_cloud_connections _sc_cloud_proj_env_uc; Type: CONSTRAINT; Schema: source_connection; Owner: postgres
--

ALTER TABLE ONLY source_connection.sc_cloud_connections
    ADD CONSTRAINT _sc_cloud_proj_env_uc UNIQUE (project_id, environment_id);


--
-- Name: sc_git_connections _sc_proj_env_uc; Type: CONSTRAINT; Schema: source_connection; Owner: postgres
--

ALTER TABLE ONLY source_connection.sc_git_connections
    ADD CONSTRAINT _sc_proj_env_uc UNIQUE (project_id, environment_id);


--
-- Name: sc_admin_audit_logs sc_admin_audit_logs_pkey; Type: CONSTRAINT; Schema: source_connection; Owner: postgres
--

ALTER TABLE ONLY source_connection.sc_admin_audit_logs
    ADD CONSTRAINT sc_admin_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: sc_admin_users sc_admin_users_pkey; Type: CONSTRAINT; Schema: source_connection; Owner: postgres
--

ALTER TABLE ONLY source_connection.sc_admin_users
    ADD CONSTRAINT sc_admin_users_pkey PRIMARY KEY (id);


--
-- Name: sc_cloud_connections sc_cloud_connections_pkey; Type: CONSTRAINT; Schema: source_connection; Owner: postgres
--

ALTER TABLE ONLY source_connection.sc_cloud_connections
    ADD CONSTRAINT sc_cloud_connections_pkey PRIMARY KEY (id);


--
-- Name: sc_git_connections sc_git_connections_pkey; Type: CONSTRAINT; Schema: source_connection; Owner: postgres
--

ALTER TABLE ONLY source_connection.sc_git_connections
    ADD CONSTRAINT sc_git_connections_pkey PRIMARY KEY (id);


--
-- Name: sc_source_snapshots sc_source_snapshots_pkey; Type: CONSTRAINT; Schema: source_connection; Owner: postgres
--

ALTER TABLE ONLY source_connection.sc_source_snapshots
    ADD CONSTRAINT sc_source_snapshots_pkey PRIMARY KEY (id);


--
-- Name: ix_admin_audit_logs_id; Type: INDEX; Schema: admin_security; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_id ON admin_security.admin_audit_logs USING btree (id);


--
-- Name: ix_admin_audit_logs_username; Type: INDEX; Schema: admin_security; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_username ON admin_security.admin_audit_logs USING btree (username);


--
-- Name: ix_admin_users_email; Type: INDEX; Schema: admin_security; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_email ON admin_security.admin_users USING btree (email);


--
-- Name: ix_admin_users_id; Type: INDEX; Schema: admin_security; Owner: postgres
--

CREATE INDEX ix_admin_users_id ON admin_security.admin_users USING btree (id);


--
-- Name: ix_admin_users_username; Type: INDEX; Schema: admin_security; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_username ON admin_security.admin_users USING btree (username);


--
-- Name: ix_ec2_catalog_id; Type: INDEX; Schema: admin_security; Owner: postgres
--

CREATE INDEX ix_ec2_catalog_id ON admin_security.ec2_catalog USING btree (id);


--
-- Name: ix_ec2_catalog_instance_type; Type: INDEX; Schema: admin_security; Owner: postgres
--

CREATE UNIQUE INDEX ix_ec2_catalog_instance_type ON admin_security.ec2_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_id; Type: INDEX; Schema: admin_security; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_id ON admin_security.generic_service_catalog USING btree (id);


--
-- Name: ix_generic_service_catalog_instance_type; Type: INDEX; Schema: admin_security; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_instance_type ON admin_security.generic_service_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_service; Type: INDEX; Schema: admin_security; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_service ON admin_security.generic_service_catalog USING btree (service);


--
-- Name: ix_rds_catalog_id; Type: INDEX; Schema: admin_security; Owner: postgres
--

CREATE INDEX ix_rds_catalog_id ON admin_security.rds_catalog USING btree (id);


--
-- Name: ix_rds_catalog_instance_type; Type: INDEX; Schema: admin_security; Owner: postgres
--

CREATE UNIQUE INDEX ix_rds_catalog_instance_type ON admin_security.rds_catalog USING btree (instance_type);


--
-- Name: ix_requirement_projects_id; Type: INDEX; Schema: admin_security; Owner: postgres
--

CREATE INDEX ix_requirement_projects_id ON admin_security.requirement_projects USING btree (id);


--
-- Name: ix_requirement_projects_project_name; Type: INDEX; Schema: admin_security; Owner: postgres
--

CREATE INDEX ix_requirement_projects_project_name ON admin_security.requirement_projects USING btree (project_name);


--
-- Name: ix_sync_metadata_id; Type: INDEX; Schema: admin_security; Owner: postgres
--

CREATE INDEX ix_sync_metadata_id ON admin_security.sync_metadata USING btree (id);


--
-- Name: ix_sync_metadata_region_code; Type: INDEX; Schema: admin_security; Owner: postgres
--

CREATE UNIQUE INDEX ix_sync_metadata_region_code ON admin_security.sync_metadata USING btree (region_code);


--
-- Name: ix_architecture_versions_environment_id; Type: INDEX; Schema: architecture; Owner: postgres
--

CREATE INDEX ix_architecture_versions_environment_id ON architecture.architecture_versions USING btree (environment_id);


--
-- Name: ix_architecture_versions_project_id; Type: INDEX; Schema: architecture; Owner: postgres
--

CREATE INDEX ix_architecture_versions_project_id ON architecture.architecture_versions USING btree (project_id);


--
-- Name: ix_architecture_versions_tenant_id; Type: INDEX; Schema: architecture; Owner: postgres
--

CREATE INDEX ix_architecture_versions_tenant_id ON architecture.architecture_versions USING btree (tenant_id);


--
-- Name: ix_architecture_versions_user_id; Type: INDEX; Schema: architecture; Owner: postgres
--

CREATE INDEX ix_architecture_versions_user_id ON architecture.architecture_versions USING btree (user_id);


--
-- Name: ix_architecture_versions_version_id; Type: INDEX; Schema: architecture; Owner: postgres
--

CREATE INDEX ix_architecture_versions_version_id ON architecture.architecture_versions USING btree (version_id);


--
-- Name: ix_studio_sessions_session_id; Type: INDEX; Schema: architecture; Owner: postgres
--

CREATE INDEX ix_studio_sessions_session_id ON architecture.studio_sessions USING btree (session_id);


--
-- Name: ix_studio_sessions_tenant_id; Type: INDEX; Schema: architecture; Owner: postgres
--

CREATE INDEX ix_studio_sessions_tenant_id ON architecture.studio_sessions USING btree (tenant_id);


--
-- Name: ix_studio_sessions_user_id; Type: INDEX; Schema: architecture; Owner: postgres
--

CREATE INDEX ix_studio_sessions_user_id ON architecture.studio_sessions USING btree (user_id);


--
-- Name: ix_generated_iac_bundles_architecture_version_id; Type: INDEX; Schema: iac; Owner: postgres
--

CREATE INDEX ix_generated_iac_bundles_architecture_version_id ON iac.generated_iac_bundles USING btree (architecture_version_id);


--
-- Name: ix_generated_iac_bundles_project_name; Type: INDEX; Schema: iac; Owner: postgres
--

CREATE INDEX ix_generated_iac_bundles_project_name ON iac.generated_iac_bundles USING btree (project_name);


--
-- Name: ix_generated_iac_bundles_tenant_id; Type: INDEX; Schema: iac; Owner: postgres
--

CREATE INDEX ix_generated_iac_bundles_tenant_id ON iac.generated_iac_bundles USING btree (tenant_id);


--
-- Name: ix_generated_iac_bundles_terraform_version_id; Type: INDEX; Schema: iac; Owner: postgres
--

CREATE INDEX ix_generated_iac_bundles_terraform_version_id ON iac.generated_iac_bundles USING btree (terraform_version_id);


--
-- Name: ix_generated_iac_bundles_user_id; Type: INDEX; Schema: iac; Owner: postgres
--

CREATE INDEX ix_generated_iac_bundles_user_id ON iac.generated_iac_bundles USING btree (user_id);


--
-- Name: ix_aether_dashboard_preferences_id; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_aether_dashboard_preferences_id ON project_manager.aether_dashboard_preferences USING btree (id);


--
-- Name: ix_aether_dashboard_preferences_tenant_id; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_aether_dashboard_preferences_tenant_id ON project_manager.aether_dashboard_preferences USING btree (tenant_id);


--
-- Name: ix_aether_dashboard_preferences_user_id; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE UNIQUE INDEX ix_aether_dashboard_preferences_user_id ON project_manager.aether_dashboard_preferences USING btree (user_id);


--
-- Name: ix_aether_environments_account_id; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_aether_environments_account_id ON project_manager.aether_environments USING btree (account_id);


--
-- Name: ix_aether_environments_created_by_user_id; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_aether_environments_created_by_user_id ON project_manager.aether_environments USING btree (created_by_user_id);


--
-- Name: ix_aether_environments_id; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_aether_environments_id ON project_manager.aether_environments USING btree (id);


--
-- Name: ix_aether_environments_project_id; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_aether_environments_project_id ON project_manager.aether_environments USING btree (project_id);


--
-- Name: ix_aether_environments_tenant_id; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_aether_environments_tenant_id ON project_manager.aether_environments USING btree (tenant_id);


--
-- Name: ix_aether_projects_account_id; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_aether_projects_account_id ON project_manager.aether_projects USING btree (account_id);


--
-- Name: ix_aether_projects_created_by_user_id; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_aether_projects_created_by_user_id ON project_manager.aether_projects USING btree (created_by_user_id);


--
-- Name: ix_aether_projects_id; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_aether_projects_id ON project_manager.aether_projects USING btree (id);


--
-- Name: ix_aether_projects_name; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_aether_projects_name ON project_manager.aether_projects USING btree (name);


--
-- Name: ix_aether_projects_owner; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_aether_projects_owner ON project_manager.aether_projects USING btree (owner);


--
-- Name: ix_aether_projects_tenant_id; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_aether_projects_tenant_id ON project_manager.aether_projects USING btree (tenant_id);


--
-- Name: ix_aether_tenant_memberships_id; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_aether_tenant_memberships_id ON project_manager.aether_tenant_memberships USING btree (id);


--
-- Name: ix_aether_tenant_memberships_tenant_id; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_aether_tenant_memberships_tenant_id ON project_manager.aether_tenant_memberships USING btree (tenant_id);


--
-- Name: ix_aether_tenant_memberships_user_id; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_aether_tenant_memberships_user_id ON project_manager.aether_tenant_memberships USING btree (user_id);


--
-- Name: ix_aether_tenants_id; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_aether_tenants_id ON project_manager.aether_tenants USING btree (id);


--
-- Name: ix_aether_tenants_slug; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE UNIQUE INDEX ix_aether_tenants_slug ON project_manager.aether_tenants USING btree (slug);


--
-- Name: ix_pm_admin_audit_logs_id; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_pm_admin_audit_logs_id ON project_manager.pm_admin_audit_logs USING btree (id);


--
-- Name: ix_pm_admin_audit_logs_username; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_pm_admin_audit_logs_username ON project_manager.pm_admin_audit_logs USING btree (username);


--
-- Name: ix_pm_admin_users_email; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE UNIQUE INDEX ix_pm_admin_users_email ON project_manager.pm_admin_users USING btree (email);


--
-- Name: ix_pm_admin_users_id; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE INDEX ix_pm_admin_users_id ON project_manager.pm_admin_users USING btree (id);


--
-- Name: ix_pm_admin_users_username; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE UNIQUE INDEX ix_pm_admin_users_username ON project_manager.pm_admin_users USING btree (username);


--
-- Name: ix_pm_admin_users_uuid; Type: INDEX; Schema: project_manager; Owner: postgres
--

CREATE UNIQUE INDEX ix_pm_admin_users_uuid ON project_manager.pm_admin_users USING btree (uuid);


--
-- Name: ix_admin_audit_logs_id; Type: INDEX; Schema: region_ca_central_1; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_id ON region_ca_central_1.admin_audit_logs USING btree (id);


--
-- Name: ix_admin_audit_logs_username; Type: INDEX; Schema: region_ca_central_1; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_username ON region_ca_central_1.admin_audit_logs USING btree (username);


--
-- Name: ix_admin_users_email; Type: INDEX; Schema: region_ca_central_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_email ON region_ca_central_1.admin_users USING btree (email);


--
-- Name: ix_admin_users_id; Type: INDEX; Schema: region_ca_central_1; Owner: postgres
--

CREATE INDEX ix_admin_users_id ON region_ca_central_1.admin_users USING btree (id);


--
-- Name: ix_admin_users_username; Type: INDEX; Schema: region_ca_central_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_username ON region_ca_central_1.admin_users USING btree (username);


--
-- Name: ix_ec2_catalog_id; Type: INDEX; Schema: region_ca_central_1; Owner: postgres
--

CREATE INDEX ix_ec2_catalog_id ON region_ca_central_1.ec2_catalog USING btree (id);


--
-- Name: ix_ec2_catalog_instance_type; Type: INDEX; Schema: region_ca_central_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_ec2_catalog_instance_type ON region_ca_central_1.ec2_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_id; Type: INDEX; Schema: region_ca_central_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_id ON region_ca_central_1.generic_service_catalog USING btree (id);


--
-- Name: ix_generic_service_catalog_instance_type; Type: INDEX; Schema: region_ca_central_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_instance_type ON region_ca_central_1.generic_service_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_service; Type: INDEX; Schema: region_ca_central_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_service ON region_ca_central_1.generic_service_catalog USING btree (service);


--
-- Name: ix_rds_catalog_id; Type: INDEX; Schema: region_ca_central_1; Owner: postgres
--

CREATE INDEX ix_rds_catalog_id ON region_ca_central_1.rds_catalog USING btree (id);


--
-- Name: ix_rds_catalog_instance_type; Type: INDEX; Schema: region_ca_central_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_rds_catalog_instance_type ON region_ca_central_1.rds_catalog USING btree (instance_type);


--
-- Name: ix_requirement_projects_id; Type: INDEX; Schema: region_ca_central_1; Owner: postgres
--

CREATE INDEX ix_requirement_projects_id ON region_ca_central_1.requirement_projects USING btree (id);


--
-- Name: ix_requirement_projects_project_name; Type: INDEX; Schema: region_ca_central_1; Owner: postgres
--

CREATE INDEX ix_requirement_projects_project_name ON region_ca_central_1.requirement_projects USING btree (project_name);


--
-- Name: ix_sync_metadata_id; Type: INDEX; Schema: region_ca_central_1; Owner: postgres
--

CREATE INDEX ix_sync_metadata_id ON region_ca_central_1.sync_metadata USING btree (id);


--
-- Name: ix_sync_metadata_region_code; Type: INDEX; Schema: region_ca_central_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_sync_metadata_region_code ON region_ca_central_1.sync_metadata USING btree (region_code);


--
-- Name: ix_admin_audit_logs_id; Type: INDEX; Schema: region_ca_west_1; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_id ON region_ca_west_1.admin_audit_logs USING btree (id);


--
-- Name: ix_admin_audit_logs_username; Type: INDEX; Schema: region_ca_west_1; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_username ON region_ca_west_1.admin_audit_logs USING btree (username);


--
-- Name: ix_admin_users_email; Type: INDEX; Schema: region_ca_west_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_email ON region_ca_west_1.admin_users USING btree (email);


--
-- Name: ix_admin_users_id; Type: INDEX; Schema: region_ca_west_1; Owner: postgres
--

CREATE INDEX ix_admin_users_id ON region_ca_west_1.admin_users USING btree (id);


--
-- Name: ix_admin_users_username; Type: INDEX; Schema: region_ca_west_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_username ON region_ca_west_1.admin_users USING btree (username);


--
-- Name: ix_ec2_catalog_id; Type: INDEX; Schema: region_ca_west_1; Owner: postgres
--

CREATE INDEX ix_ec2_catalog_id ON region_ca_west_1.ec2_catalog USING btree (id);


--
-- Name: ix_ec2_catalog_instance_type; Type: INDEX; Schema: region_ca_west_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_ec2_catalog_instance_type ON region_ca_west_1.ec2_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_id; Type: INDEX; Schema: region_ca_west_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_id ON region_ca_west_1.generic_service_catalog USING btree (id);


--
-- Name: ix_generic_service_catalog_instance_type; Type: INDEX; Schema: region_ca_west_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_instance_type ON region_ca_west_1.generic_service_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_service; Type: INDEX; Schema: region_ca_west_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_service ON region_ca_west_1.generic_service_catalog USING btree (service);


--
-- Name: ix_rds_catalog_id; Type: INDEX; Schema: region_ca_west_1; Owner: postgres
--

CREATE INDEX ix_rds_catalog_id ON region_ca_west_1.rds_catalog USING btree (id);


--
-- Name: ix_rds_catalog_instance_type; Type: INDEX; Schema: region_ca_west_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_rds_catalog_instance_type ON region_ca_west_1.rds_catalog USING btree (instance_type);


--
-- Name: ix_requirement_projects_id; Type: INDEX; Schema: region_ca_west_1; Owner: postgres
--

CREATE INDEX ix_requirement_projects_id ON region_ca_west_1.requirement_projects USING btree (id);


--
-- Name: ix_requirement_projects_project_name; Type: INDEX; Schema: region_ca_west_1; Owner: postgres
--

CREATE INDEX ix_requirement_projects_project_name ON region_ca_west_1.requirement_projects USING btree (project_name);


--
-- Name: ix_sync_metadata_id; Type: INDEX; Schema: region_ca_west_1; Owner: postgres
--

CREATE INDEX ix_sync_metadata_id ON region_ca_west_1.sync_metadata USING btree (id);


--
-- Name: ix_sync_metadata_region_code; Type: INDEX; Schema: region_ca_west_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_sync_metadata_region_code ON region_ca_west_1.sync_metadata USING btree (region_code);


--
-- Name: ix_admin_audit_logs_id; Type: INDEX; Schema: region_mx_central_1; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_id ON region_mx_central_1.admin_audit_logs USING btree (id);


--
-- Name: ix_admin_audit_logs_username; Type: INDEX; Schema: region_mx_central_1; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_username ON region_mx_central_1.admin_audit_logs USING btree (username);


--
-- Name: ix_admin_users_email; Type: INDEX; Schema: region_mx_central_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_email ON region_mx_central_1.admin_users USING btree (email);


--
-- Name: ix_admin_users_id; Type: INDEX; Schema: region_mx_central_1; Owner: postgres
--

CREATE INDEX ix_admin_users_id ON region_mx_central_1.admin_users USING btree (id);


--
-- Name: ix_admin_users_username; Type: INDEX; Schema: region_mx_central_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_username ON region_mx_central_1.admin_users USING btree (username);


--
-- Name: ix_ec2_catalog_id; Type: INDEX; Schema: region_mx_central_1; Owner: postgres
--

CREATE INDEX ix_ec2_catalog_id ON region_mx_central_1.ec2_catalog USING btree (id);


--
-- Name: ix_ec2_catalog_instance_type; Type: INDEX; Schema: region_mx_central_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_ec2_catalog_instance_type ON region_mx_central_1.ec2_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_id; Type: INDEX; Schema: region_mx_central_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_id ON region_mx_central_1.generic_service_catalog USING btree (id);


--
-- Name: ix_generic_service_catalog_instance_type; Type: INDEX; Schema: region_mx_central_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_instance_type ON region_mx_central_1.generic_service_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_service; Type: INDEX; Schema: region_mx_central_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_service ON region_mx_central_1.generic_service_catalog USING btree (service);


--
-- Name: ix_rds_catalog_id; Type: INDEX; Schema: region_mx_central_1; Owner: postgres
--

CREATE INDEX ix_rds_catalog_id ON region_mx_central_1.rds_catalog USING btree (id);


--
-- Name: ix_rds_catalog_instance_type; Type: INDEX; Schema: region_mx_central_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_rds_catalog_instance_type ON region_mx_central_1.rds_catalog USING btree (instance_type);


--
-- Name: ix_requirement_projects_id; Type: INDEX; Schema: region_mx_central_1; Owner: postgres
--

CREATE INDEX ix_requirement_projects_id ON region_mx_central_1.requirement_projects USING btree (id);


--
-- Name: ix_requirement_projects_project_name; Type: INDEX; Schema: region_mx_central_1; Owner: postgres
--

CREATE INDEX ix_requirement_projects_project_name ON region_mx_central_1.requirement_projects USING btree (project_name);


--
-- Name: ix_sync_metadata_id; Type: INDEX; Schema: region_mx_central_1; Owner: postgres
--

CREATE INDEX ix_sync_metadata_id ON region_mx_central_1.sync_metadata USING btree (id);


--
-- Name: ix_sync_metadata_region_code; Type: INDEX; Schema: region_mx_central_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_sync_metadata_region_code ON region_mx_central_1.sync_metadata USING btree (region_code);


--
-- Name: ix_admin_audit_logs_id; Type: INDEX; Schema: region_sa_east_1; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_id ON region_sa_east_1.admin_audit_logs USING btree (id);


--
-- Name: ix_admin_audit_logs_username; Type: INDEX; Schema: region_sa_east_1; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_username ON region_sa_east_1.admin_audit_logs USING btree (username);


--
-- Name: ix_admin_users_email; Type: INDEX; Schema: region_sa_east_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_email ON region_sa_east_1.admin_users USING btree (email);


--
-- Name: ix_admin_users_id; Type: INDEX; Schema: region_sa_east_1; Owner: postgres
--

CREATE INDEX ix_admin_users_id ON region_sa_east_1.admin_users USING btree (id);


--
-- Name: ix_admin_users_username; Type: INDEX; Schema: region_sa_east_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_username ON region_sa_east_1.admin_users USING btree (username);


--
-- Name: ix_ec2_catalog_id; Type: INDEX; Schema: region_sa_east_1; Owner: postgres
--

CREATE INDEX ix_ec2_catalog_id ON region_sa_east_1.ec2_catalog USING btree (id);


--
-- Name: ix_ec2_catalog_instance_type; Type: INDEX; Schema: region_sa_east_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_ec2_catalog_instance_type ON region_sa_east_1.ec2_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_id; Type: INDEX; Schema: region_sa_east_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_id ON region_sa_east_1.generic_service_catalog USING btree (id);


--
-- Name: ix_generic_service_catalog_instance_type; Type: INDEX; Schema: region_sa_east_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_instance_type ON region_sa_east_1.generic_service_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_service; Type: INDEX; Schema: region_sa_east_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_service ON region_sa_east_1.generic_service_catalog USING btree (service);


--
-- Name: ix_rds_catalog_id; Type: INDEX; Schema: region_sa_east_1; Owner: postgres
--

CREATE INDEX ix_rds_catalog_id ON region_sa_east_1.rds_catalog USING btree (id);


--
-- Name: ix_rds_catalog_instance_type; Type: INDEX; Schema: region_sa_east_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_rds_catalog_instance_type ON region_sa_east_1.rds_catalog USING btree (instance_type);


--
-- Name: ix_requirement_projects_id; Type: INDEX; Schema: region_sa_east_1; Owner: postgres
--

CREATE INDEX ix_requirement_projects_id ON region_sa_east_1.requirement_projects USING btree (id);


--
-- Name: ix_requirement_projects_project_name; Type: INDEX; Schema: region_sa_east_1; Owner: postgres
--

CREATE INDEX ix_requirement_projects_project_name ON region_sa_east_1.requirement_projects USING btree (project_name);


--
-- Name: ix_sync_metadata_id; Type: INDEX; Schema: region_sa_east_1; Owner: postgres
--

CREATE INDEX ix_sync_metadata_id ON region_sa_east_1.sync_metadata USING btree (id);


--
-- Name: ix_sync_metadata_region_code; Type: INDEX; Schema: region_sa_east_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_sync_metadata_region_code ON region_sa_east_1.sync_metadata USING btree (region_code);


--
-- Name: ix_admin_audit_logs_id; Type: INDEX; Schema: region_us_east_1; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_id ON region_us_east_1.admin_audit_logs USING btree (id);


--
-- Name: ix_admin_audit_logs_username; Type: INDEX; Schema: region_us_east_1; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_username ON region_us_east_1.admin_audit_logs USING btree (username);


--
-- Name: ix_admin_users_email; Type: INDEX; Schema: region_us_east_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_email ON region_us_east_1.admin_users USING btree (email);


--
-- Name: ix_admin_users_id; Type: INDEX; Schema: region_us_east_1; Owner: postgres
--

CREATE INDEX ix_admin_users_id ON region_us_east_1.admin_users USING btree (id);


--
-- Name: ix_admin_users_username; Type: INDEX; Schema: region_us_east_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_username ON region_us_east_1.admin_users USING btree (username);


--
-- Name: ix_ec2_catalog_id; Type: INDEX; Schema: region_us_east_1; Owner: postgres
--

CREATE INDEX ix_ec2_catalog_id ON region_us_east_1.ec2_catalog USING btree (id);


--
-- Name: ix_ec2_catalog_instance_type; Type: INDEX; Schema: region_us_east_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_ec2_catalog_instance_type ON region_us_east_1.ec2_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_id; Type: INDEX; Schema: region_us_east_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_id ON region_us_east_1.generic_service_catalog USING btree (id);


--
-- Name: ix_generic_service_catalog_instance_type; Type: INDEX; Schema: region_us_east_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_instance_type ON region_us_east_1.generic_service_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_service; Type: INDEX; Schema: region_us_east_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_service ON region_us_east_1.generic_service_catalog USING btree (service);


--
-- Name: ix_rds_catalog_id; Type: INDEX; Schema: region_us_east_1; Owner: postgres
--

CREATE INDEX ix_rds_catalog_id ON region_us_east_1.rds_catalog USING btree (id);


--
-- Name: ix_rds_catalog_instance_type; Type: INDEX; Schema: region_us_east_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_rds_catalog_instance_type ON region_us_east_1.rds_catalog USING btree (instance_type);


--
-- Name: ix_requirement_projects_id; Type: INDEX; Schema: region_us_east_1; Owner: postgres
--

CREATE INDEX ix_requirement_projects_id ON region_us_east_1.requirement_projects USING btree (id);


--
-- Name: ix_requirement_projects_project_name; Type: INDEX; Schema: region_us_east_1; Owner: postgres
--

CREATE INDEX ix_requirement_projects_project_name ON region_us_east_1.requirement_projects USING btree (project_name);


--
-- Name: ix_sync_metadata_id; Type: INDEX; Schema: region_us_east_1; Owner: postgres
--

CREATE INDEX ix_sync_metadata_id ON region_us_east_1.sync_metadata USING btree (id);


--
-- Name: ix_sync_metadata_region_code; Type: INDEX; Schema: region_us_east_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_sync_metadata_region_code ON region_us_east_1.sync_metadata USING btree (region_code);


--
-- Name: ix_admin_audit_logs_id; Type: INDEX; Schema: region_us_east_2; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_id ON region_us_east_2.admin_audit_logs USING btree (id);


--
-- Name: ix_admin_audit_logs_username; Type: INDEX; Schema: region_us_east_2; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_username ON region_us_east_2.admin_audit_logs USING btree (username);


--
-- Name: ix_admin_users_email; Type: INDEX; Schema: region_us_east_2; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_email ON region_us_east_2.admin_users USING btree (email);


--
-- Name: ix_admin_users_id; Type: INDEX; Schema: region_us_east_2; Owner: postgres
--

CREATE INDEX ix_admin_users_id ON region_us_east_2.admin_users USING btree (id);


--
-- Name: ix_admin_users_username; Type: INDEX; Schema: region_us_east_2; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_username ON region_us_east_2.admin_users USING btree (username);


--
-- Name: ix_ec2_catalog_id; Type: INDEX; Schema: region_us_east_2; Owner: postgres
--

CREATE INDEX ix_ec2_catalog_id ON region_us_east_2.ec2_catalog USING btree (id);


--
-- Name: ix_ec2_catalog_instance_type; Type: INDEX; Schema: region_us_east_2; Owner: postgres
--

CREATE UNIQUE INDEX ix_ec2_catalog_instance_type ON region_us_east_2.ec2_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_id; Type: INDEX; Schema: region_us_east_2; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_id ON region_us_east_2.generic_service_catalog USING btree (id);


--
-- Name: ix_generic_service_catalog_instance_type; Type: INDEX; Schema: region_us_east_2; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_instance_type ON region_us_east_2.generic_service_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_service; Type: INDEX; Schema: region_us_east_2; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_service ON region_us_east_2.generic_service_catalog USING btree (service);


--
-- Name: ix_rds_catalog_id; Type: INDEX; Schema: region_us_east_2; Owner: postgres
--

CREATE INDEX ix_rds_catalog_id ON region_us_east_2.rds_catalog USING btree (id);


--
-- Name: ix_rds_catalog_instance_type; Type: INDEX; Schema: region_us_east_2; Owner: postgres
--

CREATE UNIQUE INDEX ix_rds_catalog_instance_type ON region_us_east_2.rds_catalog USING btree (instance_type);


--
-- Name: ix_requirement_projects_id; Type: INDEX; Schema: region_us_east_2; Owner: postgres
--

CREATE INDEX ix_requirement_projects_id ON region_us_east_2.requirement_projects USING btree (id);


--
-- Name: ix_requirement_projects_project_name; Type: INDEX; Schema: region_us_east_2; Owner: postgres
--

CREATE INDEX ix_requirement_projects_project_name ON region_us_east_2.requirement_projects USING btree (project_name);


--
-- Name: ix_sync_metadata_id; Type: INDEX; Schema: region_us_east_2; Owner: postgres
--

CREATE INDEX ix_sync_metadata_id ON region_us_east_2.sync_metadata USING btree (id);


--
-- Name: ix_sync_metadata_region_code; Type: INDEX; Schema: region_us_east_2; Owner: postgres
--

CREATE UNIQUE INDEX ix_sync_metadata_region_code ON region_us_east_2.sync_metadata USING btree (region_code);


--
-- Name: ix_admin_audit_logs_id; Type: INDEX; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_id ON region_us_gov_east_1.admin_audit_logs USING btree (id);


--
-- Name: ix_admin_audit_logs_username; Type: INDEX; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_username ON region_us_gov_east_1.admin_audit_logs USING btree (username);


--
-- Name: ix_admin_users_email; Type: INDEX; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_email ON region_us_gov_east_1.admin_users USING btree (email);


--
-- Name: ix_admin_users_id; Type: INDEX; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE INDEX ix_admin_users_id ON region_us_gov_east_1.admin_users USING btree (id);


--
-- Name: ix_admin_users_username; Type: INDEX; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_username ON region_us_gov_east_1.admin_users USING btree (username);


--
-- Name: ix_ec2_catalog_id; Type: INDEX; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE INDEX ix_ec2_catalog_id ON region_us_gov_east_1.ec2_catalog USING btree (id);


--
-- Name: ix_ec2_catalog_instance_type; Type: INDEX; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_ec2_catalog_instance_type ON region_us_gov_east_1.ec2_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_id; Type: INDEX; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_id ON region_us_gov_east_1.generic_service_catalog USING btree (id);


--
-- Name: ix_generic_service_catalog_instance_type; Type: INDEX; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_instance_type ON region_us_gov_east_1.generic_service_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_service; Type: INDEX; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_service ON region_us_gov_east_1.generic_service_catalog USING btree (service);


--
-- Name: ix_rds_catalog_id; Type: INDEX; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE INDEX ix_rds_catalog_id ON region_us_gov_east_1.rds_catalog USING btree (id);


--
-- Name: ix_rds_catalog_instance_type; Type: INDEX; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_rds_catalog_instance_type ON region_us_gov_east_1.rds_catalog USING btree (instance_type);


--
-- Name: ix_requirement_projects_id; Type: INDEX; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE INDEX ix_requirement_projects_id ON region_us_gov_east_1.requirement_projects USING btree (id);


--
-- Name: ix_requirement_projects_project_name; Type: INDEX; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE INDEX ix_requirement_projects_project_name ON region_us_gov_east_1.requirement_projects USING btree (project_name);


--
-- Name: ix_sync_metadata_id; Type: INDEX; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE INDEX ix_sync_metadata_id ON region_us_gov_east_1.sync_metadata USING btree (id);


--
-- Name: ix_sync_metadata_region_code; Type: INDEX; Schema: region_us_gov_east_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_sync_metadata_region_code ON region_us_gov_east_1.sync_metadata USING btree (region_code);


--
-- Name: ix_admin_audit_logs_id; Type: INDEX; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_id ON region_us_gov_west_1.admin_audit_logs USING btree (id);


--
-- Name: ix_admin_audit_logs_username; Type: INDEX; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_username ON region_us_gov_west_1.admin_audit_logs USING btree (username);


--
-- Name: ix_admin_users_email; Type: INDEX; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_email ON region_us_gov_west_1.admin_users USING btree (email);


--
-- Name: ix_admin_users_id; Type: INDEX; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE INDEX ix_admin_users_id ON region_us_gov_west_1.admin_users USING btree (id);


--
-- Name: ix_admin_users_username; Type: INDEX; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_username ON region_us_gov_west_1.admin_users USING btree (username);


--
-- Name: ix_ec2_catalog_id; Type: INDEX; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE INDEX ix_ec2_catalog_id ON region_us_gov_west_1.ec2_catalog USING btree (id);


--
-- Name: ix_ec2_catalog_instance_type; Type: INDEX; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_ec2_catalog_instance_type ON region_us_gov_west_1.ec2_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_id; Type: INDEX; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_id ON region_us_gov_west_1.generic_service_catalog USING btree (id);


--
-- Name: ix_generic_service_catalog_instance_type; Type: INDEX; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_instance_type ON region_us_gov_west_1.generic_service_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_service; Type: INDEX; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_service ON region_us_gov_west_1.generic_service_catalog USING btree (service);


--
-- Name: ix_rds_catalog_id; Type: INDEX; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE INDEX ix_rds_catalog_id ON region_us_gov_west_1.rds_catalog USING btree (id);


--
-- Name: ix_rds_catalog_instance_type; Type: INDEX; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_rds_catalog_instance_type ON region_us_gov_west_1.rds_catalog USING btree (instance_type);


--
-- Name: ix_requirement_projects_id; Type: INDEX; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE INDEX ix_requirement_projects_id ON region_us_gov_west_1.requirement_projects USING btree (id);


--
-- Name: ix_requirement_projects_project_name; Type: INDEX; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE INDEX ix_requirement_projects_project_name ON region_us_gov_west_1.requirement_projects USING btree (project_name);


--
-- Name: ix_sync_metadata_id; Type: INDEX; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE INDEX ix_sync_metadata_id ON region_us_gov_west_1.sync_metadata USING btree (id);


--
-- Name: ix_sync_metadata_region_code; Type: INDEX; Schema: region_us_gov_west_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_sync_metadata_region_code ON region_us_gov_west_1.sync_metadata USING btree (region_code);


--
-- Name: ix_admin_audit_logs_id; Type: INDEX; Schema: region_us_west_1; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_id ON region_us_west_1.admin_audit_logs USING btree (id);


--
-- Name: ix_admin_audit_logs_username; Type: INDEX; Schema: region_us_west_1; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_username ON region_us_west_1.admin_audit_logs USING btree (username);


--
-- Name: ix_admin_users_email; Type: INDEX; Schema: region_us_west_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_email ON region_us_west_1.admin_users USING btree (email);


--
-- Name: ix_admin_users_id; Type: INDEX; Schema: region_us_west_1; Owner: postgres
--

CREATE INDEX ix_admin_users_id ON region_us_west_1.admin_users USING btree (id);


--
-- Name: ix_admin_users_username; Type: INDEX; Schema: region_us_west_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_username ON region_us_west_1.admin_users USING btree (username);


--
-- Name: ix_ec2_catalog_id; Type: INDEX; Schema: region_us_west_1; Owner: postgres
--

CREATE INDEX ix_ec2_catalog_id ON region_us_west_1.ec2_catalog USING btree (id);


--
-- Name: ix_ec2_catalog_instance_type; Type: INDEX; Schema: region_us_west_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_ec2_catalog_instance_type ON region_us_west_1.ec2_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_id; Type: INDEX; Schema: region_us_west_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_id ON region_us_west_1.generic_service_catalog USING btree (id);


--
-- Name: ix_generic_service_catalog_instance_type; Type: INDEX; Schema: region_us_west_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_instance_type ON region_us_west_1.generic_service_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_service; Type: INDEX; Schema: region_us_west_1; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_service ON region_us_west_1.generic_service_catalog USING btree (service);


--
-- Name: ix_rds_catalog_id; Type: INDEX; Schema: region_us_west_1; Owner: postgres
--

CREATE INDEX ix_rds_catalog_id ON region_us_west_1.rds_catalog USING btree (id);


--
-- Name: ix_rds_catalog_instance_type; Type: INDEX; Schema: region_us_west_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_rds_catalog_instance_type ON region_us_west_1.rds_catalog USING btree (instance_type);


--
-- Name: ix_requirement_projects_id; Type: INDEX; Schema: region_us_west_1; Owner: postgres
--

CREATE INDEX ix_requirement_projects_id ON region_us_west_1.requirement_projects USING btree (id);


--
-- Name: ix_requirement_projects_project_name; Type: INDEX; Schema: region_us_west_1; Owner: postgres
--

CREATE INDEX ix_requirement_projects_project_name ON region_us_west_1.requirement_projects USING btree (project_name);


--
-- Name: ix_sync_metadata_id; Type: INDEX; Schema: region_us_west_1; Owner: postgres
--

CREATE INDEX ix_sync_metadata_id ON region_us_west_1.sync_metadata USING btree (id);


--
-- Name: ix_sync_metadata_region_code; Type: INDEX; Schema: region_us_west_1; Owner: postgres
--

CREATE UNIQUE INDEX ix_sync_metadata_region_code ON region_us_west_1.sync_metadata USING btree (region_code);


--
-- Name: ix_admin_audit_logs_id; Type: INDEX; Schema: region_us_west_2; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_id ON region_us_west_2.admin_audit_logs USING btree (id);


--
-- Name: ix_admin_audit_logs_username; Type: INDEX; Schema: region_us_west_2; Owner: postgres
--

CREATE INDEX ix_admin_audit_logs_username ON region_us_west_2.admin_audit_logs USING btree (username);


--
-- Name: ix_admin_users_email; Type: INDEX; Schema: region_us_west_2; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_email ON region_us_west_2.admin_users USING btree (email);


--
-- Name: ix_admin_users_id; Type: INDEX; Schema: region_us_west_2; Owner: postgres
--

CREATE INDEX ix_admin_users_id ON region_us_west_2.admin_users USING btree (id);


--
-- Name: ix_admin_users_username; Type: INDEX; Schema: region_us_west_2; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_users_username ON region_us_west_2.admin_users USING btree (username);


--
-- Name: ix_ec2_catalog_id; Type: INDEX; Schema: region_us_west_2; Owner: postgres
--

CREATE INDEX ix_ec2_catalog_id ON region_us_west_2.ec2_catalog USING btree (id);


--
-- Name: ix_ec2_catalog_instance_type; Type: INDEX; Schema: region_us_west_2; Owner: postgres
--

CREATE UNIQUE INDEX ix_ec2_catalog_instance_type ON region_us_west_2.ec2_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_id; Type: INDEX; Schema: region_us_west_2; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_id ON region_us_west_2.generic_service_catalog USING btree (id);


--
-- Name: ix_generic_service_catalog_instance_type; Type: INDEX; Schema: region_us_west_2; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_instance_type ON region_us_west_2.generic_service_catalog USING btree (instance_type);


--
-- Name: ix_generic_service_catalog_service; Type: INDEX; Schema: region_us_west_2; Owner: postgres
--

CREATE INDEX ix_generic_service_catalog_service ON region_us_west_2.generic_service_catalog USING btree (service);


--
-- Name: ix_rds_catalog_id; Type: INDEX; Schema: region_us_west_2; Owner: postgres
--

CREATE INDEX ix_rds_catalog_id ON region_us_west_2.rds_catalog USING btree (id);


--
-- Name: ix_rds_catalog_instance_type; Type: INDEX; Schema: region_us_west_2; Owner: postgres
--

CREATE UNIQUE INDEX ix_rds_catalog_instance_type ON region_us_west_2.rds_catalog USING btree (instance_type);


--
-- Name: ix_requirement_projects_id; Type: INDEX; Schema: region_us_west_2; Owner: postgres
--

CREATE INDEX ix_requirement_projects_id ON region_us_west_2.requirement_projects USING btree (id);


--
-- Name: ix_requirement_projects_project_name; Type: INDEX; Schema: region_us_west_2; Owner: postgres
--

CREATE INDEX ix_requirement_projects_project_name ON region_us_west_2.requirement_projects USING btree (project_name);


--
-- Name: ix_sync_metadata_id; Type: INDEX; Schema: region_us_west_2; Owner: postgres
--

CREATE INDEX ix_sync_metadata_id ON region_us_west_2.sync_metadata USING btree (id);


--
-- Name: ix_sync_metadata_region_code; Type: INDEX; Schema: region_us_west_2; Owner: postgres
--

CREATE UNIQUE INDEX ix_sync_metadata_region_code ON region_us_west_2.sync_metadata USING btree (region_code);


--
-- Name: ix_sc_admin_audit_logs_id; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE INDEX ix_sc_admin_audit_logs_id ON source_connection.sc_admin_audit_logs USING btree (id);


--
-- Name: ix_sc_admin_audit_logs_username; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE INDEX ix_sc_admin_audit_logs_username ON source_connection.sc_admin_audit_logs USING btree (username);


--
-- Name: ix_sc_admin_users_email; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE UNIQUE INDEX ix_sc_admin_users_email ON source_connection.sc_admin_users USING btree (email);


--
-- Name: ix_sc_admin_users_id; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE INDEX ix_sc_admin_users_id ON source_connection.sc_admin_users USING btree (id);


--
-- Name: ix_sc_admin_users_username; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE UNIQUE INDEX ix_sc_admin_users_username ON source_connection.sc_admin_users USING btree (username);


--
-- Name: ix_sc_admin_users_uuid; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE UNIQUE INDEX ix_sc_admin_users_uuid ON source_connection.sc_admin_users USING btree (uuid);


--
-- Name: ix_sc_cloud_connections_created_by_user_id; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE INDEX ix_sc_cloud_connections_created_by_user_id ON source_connection.sc_cloud_connections USING btree (created_by_user_id);


--
-- Name: ix_sc_cloud_connections_environment_id; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE INDEX ix_sc_cloud_connections_environment_id ON source_connection.sc_cloud_connections USING btree (environment_id);


--
-- Name: ix_sc_cloud_connections_id; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE INDEX ix_sc_cloud_connections_id ON source_connection.sc_cloud_connections USING btree (id);


--
-- Name: ix_sc_cloud_connections_owner; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE INDEX ix_sc_cloud_connections_owner ON source_connection.sc_cloud_connections USING btree (owner);


--
-- Name: ix_sc_cloud_connections_project_id; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE INDEX ix_sc_cloud_connections_project_id ON source_connection.sc_cloud_connections USING btree (project_id);


--
-- Name: ix_sc_cloud_connections_tenant_id; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE INDEX ix_sc_cloud_connections_tenant_id ON source_connection.sc_cloud_connections USING btree (tenant_id);


--
-- Name: ix_sc_git_connections_created_by_user_id; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE INDEX ix_sc_git_connections_created_by_user_id ON source_connection.sc_git_connections USING btree (created_by_user_id);


--
-- Name: ix_sc_git_connections_environment_id; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE INDEX ix_sc_git_connections_environment_id ON source_connection.sc_git_connections USING btree (environment_id);


--
-- Name: ix_sc_git_connections_id; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE INDEX ix_sc_git_connections_id ON source_connection.sc_git_connections USING btree (id);


--
-- Name: ix_sc_git_connections_owner; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE INDEX ix_sc_git_connections_owner ON source_connection.sc_git_connections USING btree (owner);


--
-- Name: ix_sc_git_connections_project_id; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE INDEX ix_sc_git_connections_project_id ON source_connection.sc_git_connections USING btree (project_id);


--
-- Name: ix_sc_git_connections_tenant_id; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE INDEX ix_sc_git_connections_tenant_id ON source_connection.sc_git_connections USING btree (tenant_id);


--
-- Name: ix_sc_source_snapshots_connection_id; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE INDEX ix_sc_source_snapshots_connection_id ON source_connection.sc_source_snapshots USING btree (connection_id);


--
-- Name: ix_sc_source_snapshots_environment_id; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE INDEX ix_sc_source_snapshots_environment_id ON source_connection.sc_source_snapshots USING btree (environment_id);


--
-- Name: ix_sc_source_snapshots_id; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE INDEX ix_sc_source_snapshots_id ON source_connection.sc_source_snapshots USING btree (id);


--
-- Name: ix_sc_source_snapshots_project_id; Type: INDEX; Schema: source_connection; Owner: postgres
--

CREATE INDEX ix_sc_source_snapshots_project_id ON source_connection.sc_source_snapshots USING btree (project_id);


--
-- PostgreSQL database dump complete
--

\unrestrict 5b1VA1buUbkX8XgRss6D0Ld57nUYOXLCsFW5wBGAyqNdABqv2iBbWiGDXd3H9a8

--
-- Database "postgres" dump
--

\connect postgres

--
-- PostgreSQL database dump
--

\restrict UZZxyJ48nM0nWvRPomDfaUE7CKUqJtcMu89KRiLYWN6FCMuz1XdGypWpUxRWasj

-- Dumped from database version 15.19
-- Dumped by pg_dump version 15.19

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- PostgreSQL database dump complete
--

\unrestrict UZZxyJ48nM0nWvRPomDfaUE7CKUqJtcMu89KRiLYWN6FCMuz1XdGypWpUxRWasj

--
-- PostgreSQL database cluster dump complete
--

