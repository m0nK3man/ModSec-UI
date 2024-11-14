--
-- PostgreSQL database dump
--

-- Dumped from database version 14.13 (Ubuntu 14.13-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.13 (Ubuntu 14.13-0ubuntu0.22.04.1)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: modsec_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.modsec_users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    password character varying(255) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.modsec_users OWNER TO postgres;

--
-- Name: modsec_users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.modsec_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.modsec_users_id_seq OWNER TO postgres;

--
-- Name: modsec_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.modsec_users_id_seq OWNED BY public.modsec_users.id;


--
-- Name: modsec_users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modsec_users ALTER COLUMN id SET DEFAULT nextval('public.modsec_users_id_seq'::regclass);


--
-- Data for Name: modsec_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.modsec_users (id, username, password, created_at) FROM stdin;
1	admin	123	2024-11-08 11:13:43.63895
\.


--
-- Name: modsec_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.modsec_users_id_seq', 1, true);


--
-- Name: modsec_users modsec_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modsec_users
    ADD CONSTRAINT modsec_users_pkey PRIMARY KEY (id);


--
-- Name: modsec_users modsec_users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modsec_users
    ADD CONSTRAINT modsec_users_username_key UNIQUE (username);


--
-- Name: TABLE modsec_users; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.modsec_users TO modsec_admin;


--
-- Name: SEQUENCE modsec_users_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.modsec_users_id_seq TO modsec_admin;


--
-- PostgreSQL database dump complete
--

