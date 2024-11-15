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
-- Name: modsec_rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.modsec_rules (
    id integer NOT NULL,
    rule_code text NOT NULL,
    rule_name text NOT NULL,
    rule_path text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    content_hash text NOT NULL,
    is_modified boolean NOT NULL,
    last_modified timestamp with time zone NOT NULL,
    is_enabled boolean NOT NULL,
    is_content_change boolean DEFAULT false
);


ALTER TABLE public.modsec_rules OWNER TO postgres;

--
-- Name: modsec_rules_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.modsec_rules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.modsec_rules_id_seq OWNER TO postgres;

--
-- Name: modsec_rules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.modsec_rules_id_seq OWNED BY public.modsec_rules.id;


--
-- Name: modsec_rules id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modsec_rules ALTER COLUMN id SET DEFAULT nextval('public.modsec_rules_id_seq'::regclass);


--
-- Data for Name: modsec_rules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.modsec_rules (id, rule_code, rule_name, rule_path, created_at, content_hash, is_modified, last_modified, is_enabled, is_content_change) FROM stdin;
5	941	Application Attack Xss	REQUEST-941-APPLICATION-ATTACK-XSS.conf	2024-11-07 11:22:00.510231	4941037e41d391c07ebec4ece87acc71	f	2024-11-07 11:22:00.510231+07	t	f
6	942	Application Attack Sqli	REQUEST-942-APPLICATION-ATTACK-SQLI.conf	2024-11-07 11:22:00.510618	20864b6a9fdbfce311a8d61ef19a58d0	f	2024-11-07 11:22:00.510618+07	t	f
7	943	Application Attack Session Fixation	REQUEST-943-APPLICATION-ATTACK-SESSION-FIXATION.conf	2024-11-07 11:22:00.511188	1fad307b172feae9463cc791cefc4535	f	2024-11-07 11:22:00.511188+07	t	f
12	944	Application Attack Java	REQUEST-944-APPLICATION-ATTACK-JAVA.conf	2024-11-07 11:22:00.511621	3ee57b4f9438af6a7f56f89c455e61b6	f	2024-11-07 11:22:00.511621+07	t	f
13	922	Multipart Attack	REQUEST-922-MULTIPART-ATTACK.conf	2024-11-07 11:22:00.50749	60f7af8cc580cf8627932c305dcda63a	f	2024-11-07 11:22:00.50749+07	t	f
15	931	Application Attack Rfi	REQUEST-931-APPLICATION-ATTACK-RFI.conf	2024-11-07 11:22:00.50868	c1cc87fa430b42088bc0dfce661a6bcc	f	2024-11-07 11:22:00.50868+07	t	f
16	932	Application Attack Rce	REQUEST-932-APPLICATION-ATTACK-RCE.conf	2024-11-07 11:22:00.509079	564b5468365c51e0b2be9c7ea72d5b18	f	2024-11-07 11:22:00.509079+07	t	f
17	949	Blocking Evaluation	REQUEST-949-BLOCKING-EVALUATION.conf	2024-11-07 11:22:00.511997	11fa467f05a97d5d821d3b46e7244f08	f	2024-11-07 11:22:00.511997+07	t	f
18	951	Data Leakages Sql	RESPONSE-951-DATA-LEAKAGES-SQL.conf	2024-11-07 11:22:00.512765	cf517720778838e63c24970ab64d65fb	f	2024-11-07 11:22:00.512765+07	t	f
19	952	Data Leakages Java	RESPONSE-952-DATA-LEAKAGES-JAVA.conf	2024-11-07 11:22:00.513164	44be41d89b7f581892fd0973712bafc0	f	2024-11-07 11:22:00.513164+07	t	f
20	953	Data Leakages Php	RESPONSE-953-DATA-LEAKAGES-PHP.conf	2024-11-07 11:22:00.513711	415a9d89ddf3a1b3d8fed9304bf8b2c7	f	2024-11-07 11:22:00.513711+07	t	f
21	954	Data Leakages Iis	RESPONSE-954-DATA-LEAKAGES-IIS.conf	2024-11-07 11:22:00.514088	51d036076ef3fadcd4c3ceeb28a7105e	f	2024-11-07 11:22:00.514088+07	t	f
26	959	Blocking Evaluation	RESPONSE-959-BLOCKING-EVALUATION.conf	2024-11-07 11:22:00.514882	f177ae40a0c7c9fba9b60a3c7ff83231	f	2024-11-07 11:22:00.514882+07	t	f
27	980	Correlation	RESPONSE-980-CORRELATION.conf	2024-11-07 11:22:00.515311	e28f9394286c8ef45a80c04aa2fb47f8	f	2024-11-07 11:22:00.515311+07	t	f
28	999	Exclusion Rules After Crs	RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf	2024-11-07 11:22:00.515726	684ce3182cb569b21e118791d0c75333	f	2024-11-07 11:22:00.515726+07	t	f
11	920	Protocol Enforcement	REQUEST-920-PROTOCOL-ENFORCEMENT.conf	2024-11-07 11:22:00.506286	38fe7f443a5f1cb7a28d96b89631a9be	f	2024-11-07 11:22:00.506286+07	t	f
14	930	Application Attack Lfi	REQUEST-930-APPLICATION-ATTACK-LFI.conf	2024-11-07 11:22:00.508189	1873d512ea0d9ac404095e6d4980fbb0	f	2024-11-07 11:22:00.508189+07	t	f
1	933	Application Attack Php	REQUEST-933-APPLICATION-ATTACK-PHP.conf	2024-11-07 11:22:00.509458	8e1382c74beddad0dbec64c92b56089a	f	2024-11-07 11:22:00.509458+07	t	f
3	934	Application Attack Generic	REQUEST-934-APPLICATION-ATTACK-GENERIC.conf	2024-11-07 11:22:00.509864	0de43628698a32bfc4f3f08b5472672c	f	2024-11-07 11:22:00.509864+07	t	f
9	911	Method Enforcement	REQUEST-911-METHOD-ENFORCEMENT.conf	2024-11-07 11:22:00.505408	51b8fc07a0516e94d581d775dfbec2d9	f	2024-11-07 11:22:00.505408+07	t	f
22	901	Initialization	REQUEST-901-INITIALIZATION.conf	2024-11-07 11:22:00.504047	d0a50f90a3740174637b2ec0f2619b20	f	2024-11-11 14:48:45.993456+07	t	f
10	913	Scanner Detection	REQUEST-913-SCANNER-DETECTION.conf	2024-11-07 11:22:00.505912	dca99889523543188ac48e68c84c63d8	f	2024-11-07 11:22:00.505912+07	t	f
31	CONFIG_MODSEC	Modsecurity Configuration	../../modsecurity.conf	2024-11-07 13:16:24.107794	6bb4f91de81e8745d0fc9d5a5340aeb8	f	2024-11-07 22:37:26.420076+07	t	f
25	900	Exclusion Rules Before Crs	REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf	2024-11-07 11:22:00.501399	bb2f70d1e96a1061b60125a6c20b81df	f	2024-11-11 14:48:36.212342+07	t	f
30	CONFIG_CRS	Crs Configuration	../crs-setup.conf	2024-11-07 13:18:41.305888	9131f7ca0fd5fcc04717d186bd7a0970	f	2024-11-07 22:37:26.420076+07	t	f
8	905	Common Exceptions	REQUEST-905-COMMON-EXCEPTIONS.conf	2024-11-07 11:22:00.504895	542dc66877b195664f2bd27cb1cedf00	f	2024-11-07 11:22:00.504895+07	t	f
2	950	Data Leakages	RESPONSE-950-DATA-LEAKAGES.conf	2024-11-07 11:22:00.512398	da4b3c9a673ca5122863159c577182f0	f	2024-11-07 11:22:00.512398+07	t	f
23	955	Web Shells	RESPONSE-955-WEB-SHELLS.conf	2024-11-07 11:22:00.514498	d3c96677381b8ca049f1f4ea044b1d12	f	2024-11-07 11:22:00.514498+07	t	f
4	921	Protocol Attack	REQUEST-921-PROTOCOL-ATTACK.conf	2024-11-07 11:22:00.506932	c546f56121a62b38d86a0e9c24b23744	f	2024-11-07 11:22:00.506932+07	t	f
\.


--
-- Name: modsec_rules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.modsec_rules_id_seq', 31, true);


--
-- Name: modsec_rules modsec_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modsec_rules
    ADD CONSTRAINT modsec_rules_pkey PRIMARY KEY (id);


--
-- Name: TABLE modsec_rules; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.modsec_rules TO modsec_admin;


--
-- Name: SEQUENCE modsec_rules_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.modsec_rules_id_seq TO modsec_admin;


--
-- PostgreSQL database dump complete
--

