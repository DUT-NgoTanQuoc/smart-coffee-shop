--
-- PostgreSQL database dump
--

\restrict QfPKcsc9ul4plcu6bprIaT4GCnvfQtirnOMQnhp7jVQpQMKTjrKQChMdHdgV63x

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

-- Started on 2026-03-08 15:25:18

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 255 (class 1255 OID 16787)
-- Name: update_points(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_points() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Chỉ xử lý khi đơn mới hoàn thành
    IF NEW.order_status = 'COMPLETED' AND 
       (OLD.order_status IS NULL OR OLD.order_status != 'COMPLETED') THEN
        
        -- Tính điểm được tích (1 điểm = 10,000đ)
        NEW.points_earned = FLOOR(NEW.total / 10000);
        
        -- Cập nhật điểm + hạng cho khách
        UPDATE customers 
        SET 
            -- Cộng điểm (earned - used)
            total_points = total_points + NEW.points_earned - NEW.points_used,
            
            -- Tự động nâng hạng
            tier = CASE 
                WHEN total_points + NEW.points_earned - NEW.points_used >= 5000 THEN 'Kim cương'
                WHEN total_points + NEW.points_earned - NEW.points_used >= 2000 THEN 'Vàng'
                WHEN total_points + NEW.points_earned - NEW.points_used >= 500 THEN 'Bạc'
                ELSE 'Đồng'
            END
        WHERE customer_id = NEW.customer_id;
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_points() OWNER TO postgres;

--
-- TOC entry 5163 (class 0 OID 0)
-- Dependencies: 255
-- Name: FUNCTION update_points(); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.update_points() IS 'Tự động tích điểm + nâng hạng khi đơn hoàn thành';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 250 (class 1259 OID 17521)
-- Name: accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.accounts (
    id integer NOT NULL,
    staff_id integer,
    username character varying(50) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role_id integer,
    is_active boolean DEFAULT true,
    is_locked boolean DEFAULT false,
    failed_attempts smallint DEFAULT 0,
    last_login timestamp without time zone,
    last_password_change timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.accounts OWNER TO postgres;

--
-- TOC entry 249 (class 1259 OID 17520)
-- Name: accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.accounts_id_seq OWNER TO postgres;

--
-- TOC entry 5164 (class 0 OID 0)
-- Dependencies: 249
-- Name: accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.accounts_id_seq OWNED BY public.accounts.id;


--
-- TOC entry 254 (class 1259 OID 17563)
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_logs (
    id bigint NOT NULL,
    account_id integer,
    action character varying(100) NOT NULL,
    module character varying(50),
    target_id integer,
    old_data jsonb,
    new_data jsonb,
    ip_address character varying(45),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.audit_logs OWNER TO postgres;

--
-- TOC entry 253 (class 1259 OID 17562)
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_logs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_logs_id_seq OWNER TO postgres;

--
-- TOC entry 5165 (class 0 OID 0)
-- Dependencies: 253
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- TOC entry 218 (class 1259 OID 17086)
-- Name: categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.categories OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 17085)
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_id_seq OWNER TO postgres;

--
-- TOC entry 5166 (class 0 OID 0)
-- Dependencies: 217
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- TOC entry 226 (class 1259 OID 17149)
-- Name: customers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customers (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    phone character varying(20) NOT NULL,
    email character varying(100),
    points integer DEFAULT 0,
    tier character varying(20) DEFAULT 'Đồng'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.customers OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 17148)
-- Name: customers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.customers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customers_id_seq OWNER TO postgres;

--
-- TOC entry 5167 (class 0 OID 0)
-- Dependencies: 225
-- Name: customers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.customers_id_seq OWNED BY public.customers.id;


--
-- TOC entry 224 (class 1259 OID 17140)
-- Name: customizations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customizations (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    price numeric(10,2) DEFAULT 0 NOT NULL,
    category character varying(50),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.customizations OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 17139)
-- Name: customizations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.customizations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customizations_id_seq OWNER TO postgres;

--
-- TOC entry 5168 (class 0 OID 0)
-- Dependencies: 223
-- Name: customizations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.customizations_id_seq OWNED BY public.customizations.id;


--
-- TOC entry 240 (class 1259 OID 17260)
-- Name: daily_stats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.daily_stats (
    id integer NOT NULL,
    stat_date date NOT NULL,
    total_revenue numeric(10,2) DEFAULT 0,
    total_orders integer DEFAULT 0,
    total_customers integer DEFAULT 0,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.daily_stats OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 17259)
-- Name: daily_stats_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.daily_stats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.daily_stats_id_seq OWNER TO postgres;

--
-- TOC entry 5169 (class 0 OID 0)
-- Dependencies: 239
-- Name: daily_stats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.daily_stats_id_seq OWNED BY public.daily_stats.id;


--
-- TOC entry 228 (class 1259 OID 17161)
-- Name: favorite_drinks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.favorite_drinks (
    id integer NOT NULL,
    customer_id integer,
    product_id integer,
    size character varying(10),
    customizations jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.favorite_drinks OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 17160)
-- Name: favorite_drinks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.favorite_drinks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.favorite_drinks_id_seq OWNER TO postgres;

--
-- TOC entry 5170 (class 0 OID 0)
-- Dependencies: 227
-- Name: favorite_drinks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.favorite_drinks_id_seq OWNED BY public.favorite_drinks.id;


--
-- TOC entry 222 (class 1259 OID 17112)
-- Name: ingredients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ingredients (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    unit character varying(20) NOT NULL,
    quantity numeric(10,2) DEFAULT 0 NOT NULL,
    min_quantity numeric(10,2) DEFAULT 0 NOT NULL,
    price_per_unit numeric(10,2) NOT NULL,
    supplier character varying(100),
    last_restock_date date,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.ingredients OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 17111)
-- Name: ingredients_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ingredients_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ingredients_id_seq OWNER TO postgres;

--
-- TOC entry 5171 (class 0 OID 0)
-- Dependencies: 221
-- Name: ingredients_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ingredients_id_seq OWNED BY public.ingredients.id;


--
-- TOC entry 236 (class 1259 OID 17227)
-- Name: order_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_items (
    id integer NOT NULL,
    order_id integer,
    product_id integer,
    size character varying(10) NOT NULL,
    quantity integer NOT NULL,
    price numeric(10,2) NOT NULL,
    customizations jsonb,
    subtotal numeric(10,2) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.order_items OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 17226)
-- Name: order_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.order_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_items_id_seq OWNER TO postgres;

--
-- TOC entry 5172 (class 0 OID 0)
-- Dependencies: 235
-- Name: order_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.order_items_id_seq OWNED BY public.order_items.id;


--
-- TOC entry 234 (class 1259 OID 17205)
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    id integer NOT NULL,
    order_number character varying(20) NOT NULL,
    customer_id integer,
    staff_id integer,
    total_amount numeric(10,2) NOT NULL,
    discount numeric(10,2) DEFAULT 0,
    final_amount numeric(10,2) NOT NULL,
    status character varying(20) DEFAULT 'pending'::character varying,
    order_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 17204)
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.orders_id_seq OWNER TO postgres;

--
-- TOC entry 5173 (class 0 OID 0)
-- Dependencies: 233
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_id_seq OWNED BY public.orders.id;


--
-- TOC entry 238 (class 1259 OID 17247)
-- Name: payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payments (
    id integer NOT NULL,
    order_id integer,
    payment_method character varying(20) NOT NULL,
    amount numeric(10,2) NOT NULL,
    payment_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.payments OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 17246)
-- Name: payments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payments_id_seq OWNER TO postgres;

--
-- TOC entry 5174 (class 0 OID 0)
-- Dependencies: 237
-- Name: payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.payments_id_seq OWNED BY public.payments.id;


--
-- TOC entry 246 (class 1259 OID 17492)
-- Name: permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permissions (
    id integer NOT NULL,
    code character varying(100) NOT NULL,
    name character varying(150) NOT NULL,
    module character varying(50) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.permissions OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 17491)
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.permissions_id_seq OWNER TO postgres;

--
-- TOC entry 5175 (class 0 OID 0)
-- Dependencies: 245
-- Name: permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.permissions_id_seq OWNED BY public.permissions.id;


--
-- TOC entry 220 (class 1259 OID 17096)
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    id integer NOT NULL,
    category_id integer,
    name character varying(100) NOT NULL,
    description text,
    price_small numeric(10,2),
    price_medium numeric(10,2),
    price_large numeric(10,2),
    image character varying(255),
    is_available boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.products OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 17095)
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_id_seq OWNER TO postgres;

--
-- TOC entry 5176 (class 0 OID 0)
-- Dependencies: 219
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- TOC entry 242 (class 1259 OID 17460)
-- Name: recipes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recipes (
    id integer NOT NULL,
    product_id integer,
    ingredient_id integer,
    quantity_small numeric(10,2) NOT NULL,
    quantity_medium numeric(10,2) NOT NULL,
    quantity_large numeric(10,2) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.recipes OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 17459)
-- Name: recipes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.recipes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recipes_id_seq OWNER TO postgres;

--
-- TOC entry 5177 (class 0 OID 0)
-- Dependencies: 241
-- Name: recipes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.recipes_id_seq OWNED BY public.recipes.id;


--
-- TOC entry 252 (class 1259 OID 17547)
-- Name: refresh_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.refresh_tokens (
    id integer NOT NULL,
    account_id integer,
    token_hash character varying(255) NOT NULL,
    device_info character varying(255),
    ip_address character varying(45),
    expires_at timestamp without time zone NOT NULL,
    is_revoked boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.refresh_tokens OWNER TO postgres;

--
-- TOC entry 251 (class 1259 OID 17546)
-- Name: refresh_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.refresh_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.refresh_tokens_id_seq OWNER TO postgres;

--
-- TOC entry 5178 (class 0 OID 0)
-- Dependencies: 251
-- Name: refresh_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.refresh_tokens_id_seq OWNED BY public.refresh_tokens.id;


--
-- TOC entry 248 (class 1259 OID 17502)
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role_permissions (
    id integer NOT NULL,
    role_id integer,
    permission_id integer
);


ALTER TABLE public.role_permissions OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 17501)
-- Name: role_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.role_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.role_permissions_id_seq OWNER TO postgres;

--
-- TOC entry 5179 (class 0 OID 0)
-- Dependencies: 247
-- Name: role_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.role_permissions_id_seq OWNED BY public.role_permissions.id;


--
-- TOC entry 244 (class 1259 OID 17480)
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    display_name character varying(100) NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 17479)
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO postgres;

--
-- TOC entry 5180 (class 0 OID 0)
-- Dependencies: 243
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- TOC entry 230 (class 1259 OID 17181)
-- Name: staff; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.staff (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    phone character varying(20) NOT NULL,
    email character varying(100),
    role character varying(50) NOT NULL,
    salary numeric(10,2),
    hire_date date NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.staff OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 17180)
-- Name: staff_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.staff_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.staff_id_seq OWNER TO postgres;

--
-- TOC entry 5181 (class 0 OID 0)
-- Dependencies: 229
-- Name: staff_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.staff_id_seq OWNED BY public.staff.id;


--
-- TOC entry 232 (class 1259 OID 17192)
-- Name: work_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.work_logs (
    id integer NOT NULL,
    staff_id integer,
    work_date date NOT NULL,
    check_in time without time zone,
    check_out time without time zone,
    hours_worked numeric(4,2),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.work_logs OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 17191)
-- Name: work_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.work_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.work_logs_id_seq OWNER TO postgres;

--
-- TOC entry 5182 (class 0 OID 0)
-- Dependencies: 231
-- Name: work_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.work_logs_id_seq OWNED BY public.work_logs.id;


--
-- TOC entry 4876 (class 2604 OID 17524)
-- Name: accounts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts ALTER COLUMN id SET DEFAULT nextval('public.accounts_id_seq'::regclass);


--
-- TOC entry 4885 (class 2604 OID 17566)
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- TOC entry 4833 (class 2604 OID 17089)
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- TOC entry 4845 (class 2604 OID 17152)
-- Name: customers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers ALTER COLUMN id SET DEFAULT nextval('public.customers_id_seq'::regclass);


--
-- TOC entry 4842 (class 2604 OID 17143)
-- Name: customizations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customizations ALTER COLUMN id SET DEFAULT nextval('public.customizations_id_seq'::regclass);


--
-- TOC entry 4864 (class 2604 OID 17263)
-- Name: daily_stats id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_stats ALTER COLUMN id SET DEFAULT nextval('public.daily_stats_id_seq'::regclass);


--
-- TOC entry 4849 (class 2604 OID 17164)
-- Name: favorite_drinks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorite_drinks ALTER COLUMN id SET DEFAULT nextval('public.favorite_drinks_id_seq'::regclass);


--
-- TOC entry 4838 (class 2604 OID 17115)
-- Name: ingredients id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ingredients ALTER COLUMN id SET DEFAULT nextval('public.ingredients_id_seq'::regclass);


--
-- TOC entry 4860 (class 2604 OID 17230)
-- Name: order_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items ALTER COLUMN id SET DEFAULT nextval('public.order_items_id_seq'::regclass);


--
-- TOC entry 4856 (class 2604 OID 17208)
-- Name: orders id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders ALTER COLUMN id SET DEFAULT nextval('public.orders_id_seq'::regclass);


--
-- TOC entry 4862 (class 2604 OID 17250)
-- Name: payments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments ALTER COLUMN id SET DEFAULT nextval('public.payments_id_seq'::regclass);


--
-- TOC entry 4873 (class 2604 OID 17495)
-- Name: permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions ALTER COLUMN id SET DEFAULT nextval('public.permissions_id_seq'::regclass);


--
-- TOC entry 4835 (class 2604 OID 17099)
-- Name: products id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- TOC entry 4869 (class 2604 OID 17463)
-- Name: recipes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipes ALTER COLUMN id SET DEFAULT nextval('public.recipes_id_seq'::regclass);


--
-- TOC entry 4882 (class 2604 OID 17550)
-- Name: refresh_tokens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.refresh_tokens ALTER COLUMN id SET DEFAULT nextval('public.refresh_tokens_id_seq'::regclass);


--
-- TOC entry 4875 (class 2604 OID 17505)
-- Name: role_permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions ALTER COLUMN id SET DEFAULT nextval('public.role_permissions_id_seq'::regclass);


--
-- TOC entry 4871 (class 2604 OID 17483)
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- TOC entry 4851 (class 2604 OID 17184)
-- Name: staff id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.staff ALTER COLUMN id SET DEFAULT nextval('public.staff_id_seq'::regclass);


--
-- TOC entry 4854 (class 2604 OID 17195)
-- Name: work_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_logs ALTER COLUMN id SET DEFAULT nextval('public.work_logs_id_seq'::regclass);


--
-- TOC entry 5153 (class 0 OID 17521)
-- Dependencies: 250
-- Data for Name: accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accounts (id, staff_id, username, password_hash, role_id, is_active, is_locked, failed_attempts, last_login, last_password_change, created_at) FROM stdin;
1	1	quan_ly	$md5$22272c3fa2aa3308998cf2928b2c455a	1	t	f	0	\N	2026-03-08 14:53:10.423826	2026-03-08 14:53:10.423826
2	2	cashier1	$md5$90c6738b0c4808882b637c9573b4ff71	2	t	f	0	\N	2026-03-08 14:53:10.423826	2026-03-08 14:53:10.423826
3	3	cashier2	$md5$b55bcab2ef4729c837735645d5c0c421	2	t	f	0	\N	2026-03-08 14:53:10.423826	2026-03-08 14:53:10.423826
4	4	barista1	$md5$2e8e2a382ea8bcd7e78c2ccac339ebb8	3	t	f	0	\N	2026-03-08 14:53:10.423826	2026-03-08 14:53:10.423826
5	5	barista2	$md5$e8ed660927f9841644baa5ec77b8f195	3	t	f	0	\N	2026-03-08 14:53:10.423826	2026-03-08 14:53:10.423826
6	6	barista3	$md5$1aa894b355a9f428317fd1357c708e7c	3	t	f	0	\N	2026-03-08 14:53:10.423826	2026-03-08 14:53:10.423826
7	7	barista4	$md5$6ced658854f1505e4cf340b7aed5fed3	3	t	f	0	\N	2026-03-08 14:53:10.423826	2026-03-08 14:53:10.423826
8	8	parttime	$md5$fce19e68ef090a44d0e73ba2698c07b1	4	t	f	0	\N	2026-03-08 14:53:10.423826	2026-03-08 14:53:10.423826
\.


--
-- TOC entry 5157 (class 0 OID 17563)
-- Dependencies: 254
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_logs (id, account_id, action, module, target_id, old_data, new_data, ip_address, created_at) FROM stdin;
\.


--
-- TOC entry 5121 (class 0 OID 17086)
-- Dependencies: 218
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categories (id, name, description, created_at) FROM stdin;
1	Cà phê	Các loại cà phê espresso và pha phin	2026-03-07 01:47:31.196239
2	Trà & Matcha	Trà truyền thống và matcha Nhật Bản	2026-03-07 01:47:31.196239
3	Sinh tố & Nước ép	Sinh tố trái cây và nước ép tươi	2026-03-07 01:47:31.196239
4	Bánh & Snack	Bánh ngọt, bánh mặn và đồ ăn nhẹ	2026-03-07 01:47:31.196239
\.


--
-- TOC entry 5129 (class 0 OID 17149)
-- Dependencies: 226
-- Data for Name: customers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customers (id, name, phone, email, points, tier, created_at) FROM stdin;
1	Nguyễn Văn An	0901234567	an@email.com	5200	Kim cương	2026-03-07 01:47:31.196239
2	Trần Thị Bình	0902345678	binh@email.com	4800	Kim cương	2026-03-07 01:47:31.196239
3	Lê Hoàng Cường	0903456789	cuong@email.com	3500	Vàng	2026-03-07 01:47:31.196239
4	Phạm Thị Dung	0904567890	dung@email.com	3200	Vàng	2026-03-07 01:47:31.196239
5	Hoàng Văn Em	0905678901	em@email.com	2800	Vàng	2026-03-07 01:47:31.196239
6	Võ Thị Phương	0906789012	phuong@email.com	2500	Vàng	2026-03-07 01:47:31.196239
7	Đặng Văn Giang	0907890123	giang@email.com	2200	Vàng	2026-03-07 01:47:31.196239
8	Bùi Thị Hoa	0908901234	hoa@email.com	2000	Vàng	2026-03-07 01:47:31.196239
9	Trương Văn Inh	0909012345	inh@email.com	5500	Kim cương	2026-03-07 01:47:31.196239
10	Phan Thị Kim	0910123456	kim@email.com	4200	Kim cương	2026-03-07 01:47:31.196239
11	Ngô Văn Long	0911234567	long@email.com	1800	Bạc	2026-03-07 01:47:31.196239
12	Đinh Thị Mai	0912345678	mai@email.com	1600	Bạc	2026-03-07 01:47:31.196239
13	Lý Văn Nam	0913456789	nam@email.com	1400	Bạc	2026-03-07 01:47:31.196239
14	Tô Thị Oanh	0914567890	oanh@email.com	1200	Bạc	2026-03-07 01:47:31.196239
15	Dương Văn Phú	0915678901	phu@email.com	1100	Bạc	2026-03-07 01:47:31.196239
16	Hồ Thị Quỳnh	0916789012	quynh@email.com	1000	Bạc	2026-03-07 01:47:31.196239
17	Mai Văn Rộng	0917890123	rong@email.com	950	Bạc	2026-03-07 01:47:31.196239
18	Cao Thị Sang	0918901234	sang@email.com	900	Bạc	2026-03-07 01:47:31.196239
19	Huỳnh Văn Tài	0919012345	tai@email.com	850	Bạc	2026-03-07 01:47:31.196239
20	Lâm Thị Uyên	0920123456	uyen@email.com	800	Bạc	2026-03-07 01:47:31.196239
21	Tạ Văn Vinh	0921234567	vinh@email.com	750	Bạc	2026-03-07 01:47:31.196239
22	Ông Thị Xuân	0922345678	xuan@email.com	700	Bạc	2026-03-07 01:47:31.196239
23	Từ Văn Yên	0923456789	yen@email.com	650	Bạc	2026-03-07 01:47:31.196239
24	La Thị Ánh	0924567890	anh@email.com	600	Bạc	2026-03-07 01:47:31.196239
25	Xa Văn Bảo	0925678901	bao@email.com	550	Bạc	2026-03-07 01:47:31.196239
26	Nguyễn Thị Cẩm	0926789012	cam@email.com	450	Đồng	2026-03-07 01:47:31.196239
27	Trần Văn Đức	0927890123	duc@email.com	400	Đồng	2026-03-07 01:47:31.196239
28	Lê Thị Én	0928901234	en@email.com	380	Đồng	2026-03-07 01:47:31.196239
29	Phạm Văn Phong	0929012345	phong@email.com	350	Đồng	2026-03-07 01:47:31.196239
30	Hoàng Thị Giang	0930123456	giang2@email.com	320	Đồng	2026-03-07 01:47:31.196239
31	Võ Văn Hải	0931234567	hai@email.com	300	Đồng	2026-03-07 01:47:31.196239
32	Đặng Thị Ivy	0932345678	ivy@email.com	280	Đồng	2026-03-07 01:47:31.196239
33	Bùi Văn Khánh	0933456789	khanh@email.com	260	Đồng	2026-03-07 01:47:31.196239
34	Trương Thị Linh	0934567890	linh@email.com	240	Đồng	2026-03-07 01:47:31.196239
35	Phan Văn Minh	0935678901	minh@email.com	220	Đồng	2026-03-07 01:47:31.196239
36	Ngô Thị Nga	0936789012	nga@email.com	200	Đồng	2026-03-07 01:47:31.196239
37	Đinh Văn Ổn	0937890123	on@email.com	180	Đồng	2026-03-07 01:47:31.196239
38	Lý Thị Phấn	0938901234	phan@email.com	160	Đồng	2026-03-07 01:47:31.196239
39	Tô Văn Quang	0939012345	quang@email.com	140	Đồng	2026-03-07 01:47:31.196239
40	Dương Thị Rạng	0940123456	rang@email.com	120	Đồng	2026-03-07 01:47:31.196239
41	Hồ Văn Sơn	0941234567	son@email.com	100	Đồng	2026-03-07 01:47:31.196239
42	Mai Thị Tâm	0942345678	tam@email.com	90	Đồng	2026-03-07 01:47:31.196239
43	Cao Văn Uy	0943456789	uy@email.com	80	Đồng	2026-03-07 01:47:31.196239
44	Huỳnh Thị Vân	0944567890	van@email.com	70	Đồng	2026-03-07 01:47:31.196239
45	Lâm Văn Xuân	0945678901	xuan2@email.com	60	Đồng	2026-03-07 01:47:31.196239
46	Tạ Thị Yến	0946789012	yen2@email.com	50	Đồng	2026-03-07 01:47:31.196239
47	Ông Văn Zũng	0947890123	zung@email.com	40	Đồng	2026-03-07 01:47:31.196239
48	Từ Thị An	0948901234	an2@email.com	30	Đồng	2026-03-07 01:47:31.196239
49	La Văn Bình	0949012345	binh2@email.com	20	Đồng	2026-03-07 01:47:31.196239
50	Xa Thị Chi	0950123456	chi@email.com	10	Đồng	2026-03-07 01:47:31.196239
\.


--
-- TOC entry 5127 (class 0 OID 17140)
-- Dependencies: 224
-- Data for Name: customizations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customizations (id, name, price, category, created_at) FROM stdin;
1	Không đường	0.00	Đường	2026-03-07 01:47:31.196239
2	Ít đường (50%)	0.00	Đường	2026-03-07 01:47:31.196239
3	Vừa đường (75%)	0.00	Đường	2026-03-07 01:47:31.196239
4	Nhiều đường (100%)	0.00	Đường	2026-03-07 01:47:31.196239
5	Không đá	0.00	Đá	2026-03-07 01:47:31.196239
6	Ít đá	0.00	Đá	2026-03-07 01:47:31.196239
7	Đá bình thường	0.00	Đá	2026-03-07 01:47:31.196239
8	Nhiều đá	0.00	Đá	2026-03-07 01:47:31.196239
9	Sữa yến mạch	5000.00	Sữa	2026-03-07 01:47:31.196239
10	Sữa hạnh nhân	5000.00	Sữa	2026-03-07 01:47:31.196239
11	Sữa đậu nành	3000.00	Sữa	2026-03-07 01:47:31.196239
12	Shot thêm	10000.00	Extra	2026-03-07 01:47:31.196239
13	Whipped cream	8000.00	Topping	2026-03-07 01:47:31.196239
14	Caramel drizzle	5000.00	Topping	2026-03-07 01:47:31.196239
15	Trân châu thêm	7000.00	Topping	2026-03-07 01:47:31.196239
\.


--
-- TOC entry 5143 (class 0 OID 17260)
-- Dependencies: 240
-- Data for Name: daily_stats; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.daily_stats (id, stat_date, total_revenue, total_orders, total_customers, created_at) FROM stdin;
1	2024-12-01	88250.00	2	1	2026-03-07 01:47:31.196239
2	2024-12-02	225000.00	2	2	2026-03-07 01:47:31.196239
3	2024-12-03	170000.00	2	2	2026-03-07 01:47:31.196239
4	2024-12-04	159000.00	2	2	2026-03-07 01:47:31.196239
5	2024-12-05	70000.00	2	1	2026-03-07 01:47:31.196239
6	2024-12-06	194500.00	2	0	2026-03-07 01:47:31.196239
7	2024-12-07	101500.00	2	1	2026-03-07 01:47:31.196239
8	2024-12-08	140000.00	2	2	2026-03-07 01:47:31.196239
9	2024-12-09	185000.00	2	0	2026-03-07 01:47:31.196239
10	2024-12-10	133000.00	2	2	2026-03-07 01:47:31.196239
11	2024-12-11	170000.00	2	2	2026-03-07 01:47:31.196239
12	2024-12-12	120500.00	2	2	2026-03-07 01:47:31.196239
13	2024-12-13	215000.00	2	1	2026-03-07 01:47:31.196239
14	2024-12-14	188250.00	2	1	2026-03-07 01:47:31.196239
15	2024-12-15	235000.00	2	1	2026-03-07 01:47:31.196239
16	2024-12-16	100000.00	2	1	2026-03-07 01:47:31.196239
17	2024-12-17	125000.00	2	1	2026-03-07 01:47:31.196239
18	2024-12-18	215000.00	2	2	2026-03-07 01:47:31.196239
19	2024-12-19	110000.00	2	1	2026-03-07 01:47:31.196239
20	2024-12-20	205000.00	2	1	2026-03-07 01:47:31.196239
21	2024-12-21	176500.00	2	1	2026-03-07 01:47:31.196239
22	2024-12-22	105000.00	2	2	2026-03-07 01:47:31.196239
23	2024-12-23	50000.00	1	0	2026-03-07 01:47:31.196239
24	2024-12-24	45000.00	1	1	2026-03-07 01:47:31.196239
25	2024-12-25	110000.00	1	1	2026-03-07 01:47:31.196239
26	2024-12-26	35000.00	1	1	2026-03-07 01:47:31.196239
27	2024-12-27	45000.00	1	1	2026-03-07 01:47:31.196239
28	2024-12-28	90250.00	1	1	2026-03-07 01:47:31.196239
29	2025-01-01	110000.00	2	2	2026-03-07 01:47:31.196239
30	2025-01-02	70000.00	2	1	2026-03-07 01:47:31.196239
31	2025-01-03	255000.00	2	2	2026-03-07 01:47:31.196239
32	2025-01-04	48250.00	2	2	2026-03-07 01:47:31.196239
33	2025-01-05	237250.00	2	2	2026-03-07 01:47:31.196239
34	2025-01-06	220000.00	2	2	2026-03-07 01:47:31.196239
35	2025-01-07	263750.00	2	1	2026-03-07 01:47:31.196239
36	2025-01-08	165000.00	2	0	2026-03-07 01:47:31.196239
37	2025-01-09	190000.00	2	2	2026-03-07 01:47:31.196239
38	2025-01-10	130000.00	2	1	2026-03-07 01:47:31.196239
39	2025-01-11	120000.00	2	2	2026-03-07 01:47:31.196239
40	2025-01-12	140000.00	2	2	2026-03-07 01:47:31.196239
41	2025-01-13	75000.00	2	2	2026-03-07 01:47:31.196239
42	2025-01-14	150000.00	2	2	2026-03-07 01:47:31.196239
43	2025-01-15	106250.00	2	1	2026-03-07 01:47:31.196239
44	2025-01-16	190000.00	2	2	2026-03-07 01:47:31.196239
45	2025-01-17	102750.00	2	0	2026-03-07 01:47:31.196239
46	2025-01-18	58250.00	2	2	2026-03-07 01:47:31.196239
47	2025-01-19	82750.00	2	2	2026-03-07 01:47:31.196239
48	2025-01-20	160000.00	2	2	2026-03-07 01:47:31.196239
49	2025-01-21	40000.00	2	1	2026-03-07 01:47:31.196239
50	2025-01-22	105000.00	2	1	2026-03-07 01:47:31.196239
51	2025-01-23	15000.00	1	1	2026-03-07 01:47:31.196239
52	2025-01-24	50000.00	1	1	2026-03-07 01:47:31.196239
53	2025-01-25	90000.00	1	0	2026-03-07 01:47:31.196239
54	2025-01-26	100000.00	1	0	2026-03-07 01:47:31.196239
55	2025-01-27	65000.00	1	1	2026-03-07 01:47:31.196239
56	2025-01-28	125000.00	1	1	2026-03-07 01:47:31.196239
57	2025-02-01	450500.00	7	5	2026-03-07 01:47:31.196239
58	2025-02-02	678250.00	7	6	2026-03-07 01:47:31.196239
59	2025-02-03	420500.00	6	5	2026-03-07 01:47:31.196239
60	2025-02-04	398250.00	6	6	2026-03-07 01:47:31.196239
61	2025-02-05	218250.00	6	4	2026-03-07 01:47:31.196239
62	2025-02-06	595250.00	6	4	2026-03-07 01:47:31.196239
63	2025-02-07	442000.00	6	5	2026-03-07 01:47:31.196239
64	2025-02-08	600000.00	6	3	2026-03-07 01:47:31.196239
\.


--
-- TOC entry 5131 (class 0 OID 17161)
-- Dependencies: 228
-- Data for Name: favorite_drinks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.favorite_drinks (id, customer_id, product_id, size, customizations, created_at) FROM stdin;
1	1	3	M	{"milk": "oat", "sugar": "50%"}	2026-03-07 01:47:31.196239
2	1	4	L	{"extra": "shot", "sugar": "0%"}	2026-03-07 01:47:31.196239
3	2	12	M	{"sugar": "75%"}	2026-03-07 01:47:31.196239
4	2	11	L	{"topping": "pearl"}	2026-03-07 01:47:31.196239
5	3	6	L	{"milk": "almond"}	2026-03-07 01:47:31.196239
6	3	5	M	{"topping": "whipped"}	2026-03-07 01:47:31.196239
7	4	4	M	{"sugar": "100%"}	2026-03-07 01:47:31.196239
8	4	14	L	{"sugar": "50%"}	2026-03-07 01:47:31.196239
9	5	7	S	{"sugar": "0%"}	2026-03-07 01:47:31.196239
10	5	3	M	{"milk": "oat"}	2026-03-07 01:47:31.196239
11	6	10	L	{"ice": "extra"}	2026-03-07 01:47:31.196239
12	6	4	M	{"sugar": "75%"}	2026-03-07 01:47:31.196239
13	7	8	M	{"ice": "less"}	2026-03-07 01:47:31.196239
14	7	15	L	{}	2026-03-07 01:47:31.196239
15	8	11	L	{"topping": "pearl"}	2026-03-07 01:47:31.196239
16	8	3	M	{"sugar": "50%"}	2026-03-07 01:47:31.196239
17	9	6	L	{"extra": "shot"}	2026-03-07 01:47:31.196239
18	9	5	M	{"topping": "whipped"}	2026-03-07 01:47:31.196239
19	10	4	L	{"milk": "oat"}	2026-03-07 01:47:31.196239
20	10	12	M	{"sugar": "50%"}	2026-03-07 01:47:31.196239
\.


--
-- TOC entry 5125 (class 0 OID 17112)
-- Dependencies: 222
-- Data for Name: ingredients; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ingredients (id, name, unit, quantity, min_quantity, price_per_unit, supplier, last_restock_date, created_at) FROM stdin;
1	Hạt cà phê Arabica	g	8000.00	2000.00	0.60	Highlands Coffee	2025-02-01	2026-03-07 01:47:31.196239
2	Hạt cà phê Robusta	g	6000.00	1500.00	0.40	Highlands Coffee	2025-02-01	2026-03-07 01:47:31.196239
3	Bột cà phê phin	g	5000.00	1000.00	0.50	Trung Nguyên	2025-02-05	2026-03-07 01:47:31.196239
4	Sữa tươi	ml	15000.00	3000.00	0.04	Vinamilk	2025-02-08	2026-03-07 01:47:31.196239
5	Sữa đặc	ml	5000.00	1000.00	0.08	Vinamilk	2025-02-08	2026-03-07 01:47:31.196239
6	Sữa yến mạch	ml	4000.00	800.00	0.06	Oatside	2025-02-06	2026-03-07 01:47:31.196239
7	Sữa hạnh nhân	ml	3000.00	600.00	0.07	Alpro	2025-02-06	2026-03-07 01:47:31.196239
8	Kem tươi	ml	3000.00	600.00	0.12	Anchor	2025-02-07	2026-03-07 01:47:31.196239
9	Sữa chua	ml	4000.00	800.00	0.04	Vinamilk	2025-02-08	2026-03-07 01:47:31.196239
10	Whipped cream	ml	2000.00	400.00	0.15	Rich Products	2025-02-05	2026-03-07 01:47:31.196239
11	Caramel syrup	ml	2000.00	400.00	0.18	Monin	2025-02-03	2026-03-07 01:47:31.196239
12	Vanilla syrup	ml	2000.00	400.00	0.16	Monin	2025-02-03	2026-03-07 01:47:31.196239
13	Chocolate sauce	ml	2000.00	400.00	0.20	Hershey	2025-02-04	2026-03-07 01:47:31.196239
14	Trân châu đen	g	3000.00	600.00	0.08	Foodstuff	2025-02-07	2026-03-07 01:47:31.196239
15	Trà xanh	g	2500.00	500.00	0.25	Chè TN	2025-02-02	2026-03-07 01:47:31.196239
16	Trà đen	g	3000.00	600.00	0.20	Lipton	2025-02-02	2026-03-07 01:47:31.196239
17	Bột matcha	g	1000.00	200.00	0.80	Matcha Master	2025-02-01	2026-03-07 01:47:31.196239
18	Hồng trà	g	2000.00	400.00	0.22	Lipton	2025-02-02	2026-03-07 01:47:31.196239
19	Dâu tây	g	4000.00	800.00	0.12	Dalat Farm	2025-02-09	2026-03-07 01:47:31.196239
20	Đào	g	3500.00	700.00	0.10	Chợ đầu mối	2025-02-08	2026-03-07 01:47:31.196239
21	Xoài	g	5000.00	1000.00	0.08	Chợ đầu mối	2025-02-07	2026-03-07 01:47:31.196239
22	Cam	g	6000.00	1200.00	0.06	Chợ đầu mối	2025-02-09	2026-03-07 01:47:31.196239
23	Bơ	g	3000.00	600.00	0.15	Chợ đầu mối	2025-02-08	2026-03-07 01:47:31.196239
24	Đường	g	10000.00	2000.00	0.02	Biên Hòa Sugar	2025-02-01	2026-03-07 01:47:31.196239
25	Đá viên	g	50000.00	10000.00	0.00	Nhà máy đá	2025-02-09	2026-03-07 01:47:31.196239
26	Sả	g	1000.00	200.00	0.05	Chợ đầu mối	2025-02-07	2026-03-07 01:47:31.196239
\.


--
-- TOC entry 5139 (class 0 OID 17227)
-- Dependencies: 236
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_items (id, order_id, product_id, size, quantity, price, customizations, subtotal, created_at) FROM stdin;
1	1	7	L	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
2	2	5	L	1	60000.00	{"sugar": "50%"}	60000.00	2026-03-07 01:47:31.196239
3	2	17	S	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
4	2	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
5	3	15	M	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
6	3	6	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
7	3	17	S	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
8	4	3	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
9	5	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
10	6	5	M	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
11	6	5	L	1	60000.00	{"sugar": "50%"}	60000.00	2026-03-07 01:47:31.196239
12	7	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
13	7	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
14	8	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
15	9	11	L	1	60000.00	{"sugar": "50%"}	60000.00	2026-03-07 01:47:31.196239
16	9	14	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
17	9	1	M	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
18	10	16	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
19	11	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
20	11	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
21	12	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
22	12	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
23	13	9	M	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
24	13	15	M	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
25	14	16	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
26	14	9	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
27	15	4	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
28	15	8	L	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
29	15	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
30	16	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
31	17	13	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
32	17	2	M	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
33	18	12	L	1	65000.00	{"sugar": "50%"}	65000.00	2026-03-07 01:47:31.196239
34	18	4	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
35	19	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
36	19	10	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
37	19	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
38	20	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
39	20	12	L	1	65000.00	{"sugar": "50%"}	65000.00	2026-03-07 01:47:31.196239
40	20	10	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
41	21	1	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
42	21	7	M	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
43	21	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
44	22	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
45	23	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
46	23	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
47	24	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
48	25	1	L	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
49	25	6	L	1	65000.00	{"sugar": "50%"}	65000.00	2026-03-07 01:47:31.196239
50	26	13	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
51	27	6	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
52	28	8	S	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
53	28	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
54	28	5	S	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
55	29	4	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
56	30	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
57	30	8	L	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
58	30	12	L	1	65000.00	{"sugar": "50%"}	65000.00	2026-03-07 01:47:31.196239
59	31	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
60	31	8	S	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
61	32	1	L	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
62	32	7	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
63	32	17	L	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
64	33	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
65	34	12	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
66	34	2	S	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
67	34	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
68	35	14	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
69	36	15	S	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
70	36	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
71	36	17	S	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
72	37	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
73	37	8	S	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
74	38	12	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
75	38	6	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
76	38	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
77	39	8	S	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
78	39	14	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
79	39	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
80	40	7	L	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
81	41	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
82	41	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
83	41	16	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
84	42	3	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
85	42	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
86	42	14	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
87	43	11	M	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
88	43	13	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
89	43	11	M	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
90	44	16	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
91	45	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
92	45	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
93	46	6	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
94	46	10	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
95	47	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
96	48	10	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
97	48	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
98	49	3	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
99	49	7	L	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
100	49	17	S	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
101	50	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
102	50	3	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
103	51	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
104	51	10	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
105	52	10	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
106	53	15	M	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
107	53	1	L	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
108	53	14	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
109	54	13	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
110	55	5	S	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
111	55	11	M	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
112	56	12	M	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
113	56	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
114	56	3	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
115	57	2	L	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
116	57	15	M	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
117	57	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
118	58	12	M	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
119	58	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
120	58	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
121	59	17	M	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
122	60	15	M	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
123	60	4	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
124	61	2	S	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
125	61	2	S	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
126	62	17	L	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
127	62	14	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
128	63	7	L	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
129	64	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
130	64	10	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
131	65	9	L	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
132	66	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
133	66	14	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
134	66	13	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
135	67	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
136	68	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
137	69	10	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
138	70	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
139	70	15	L	1	60000.00	{"sugar": "50%"}	60000.00	2026-03-07 01:47:31.196239
140	71	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
141	72	11	S	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
142	73	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
143	74	17	L	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
144	75	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
145	75	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
146	76	3	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
147	76	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
148	77	5	M	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
149	77	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
150	78	15	L	1	60000.00	{"sugar": "50%"}	60000.00	2026-03-07 01:47:31.196239
151	78	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
152	78	17	M	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
153	79	8	S	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
154	80	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
155	81	10	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
156	81	9	L	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
157	81	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
158	82	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
159	83	16	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
160	83	1	L	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
161	83	4	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
162	84	15	S	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
163	84	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
164	85	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
165	85	6	M	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
166	85	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
167	86	11	S	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
168	87	1	L	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
169	87	13	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
170	87	5	M	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
171	88	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
172	89	16	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
173	89	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
174	90	16	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
175	91	5	S	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
176	92	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
177	92	4	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
178	93	12	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
179	93	7	M	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
180	94	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
181	94	8	M	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
182	94	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
183	95	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
184	95	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
185	96	10	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
186	97	11	S	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
187	98	13	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
188	98	7	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
189	98	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
190	99	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
191	100	12	L	1	65000.00	{"sugar": "50%"}	65000.00	2026-03-07 01:47:31.196239
192	101	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
193	101	16	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
194	102	10	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
195	103	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
196	103	4	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
197	104	2	L	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
198	105	3	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
199	106	7	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
200	106	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
201	106	8	L	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
202	107	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
203	107	2	M	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
204	108	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
205	108	8	M	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
206	108	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
207	109	9	L	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
208	110	17	L	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
209	110	8	S	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
210	111	10	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
211	112	7	M	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
212	113	1	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
213	114	2	S	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
214	114	16	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
215	114	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
216	115	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
217	115	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
218	115	9	L	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
219	116	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
220	116	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
221	116	12	M	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
222	117	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
223	118	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
224	118	8	M	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
225	118	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
226	119	5	L	1	60000.00	{"sugar": "50%"}	60000.00	2026-03-07 01:47:31.196239
227	119	7	L	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
228	119	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
229	120	1	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
230	121	16	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
231	122	12	M	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
232	123	16	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
233	124	17	S	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
234	124	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
235	124	1	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
236	125	16	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
237	125	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
238	125	2	L	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
239	126	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
240	126	9	L	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
241	126	13	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
242	127	5	L	1	60000.00	{"sugar": "50%"}	60000.00	2026-03-07 01:47:31.196239
243	127	17	S	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
244	128	13	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
245	129	14	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
246	130	9	M	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
247	130	12	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
248	130	6	L	1	65000.00	{"sugar": "50%"}	65000.00	2026-03-07 01:47:31.196239
249	131	8	S	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
250	131	13	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
251	131	8	L	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
252	132	7	M	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
253	132	14	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
254	133	5	S	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
255	133	7	L	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
256	133	3	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
257	134	17	M	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
258	134	10	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
259	134	12	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
260	135	19	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
261	136	4	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
262	136	4	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
263	136	2	L	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
264	137	9	L	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
265	138	15	S	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
266	139	11	M	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
267	140	4	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
268	140	9	M	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
269	141	5	S	1	40000.00	{"sugar": "50%"}	40000.00	2026-03-07 01:47:31.196239
270	141	8	S	1	30000.00	{"sugar": "50%"}	30000.00	2026-03-07 01:47:31.196239
271	142	4	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
272	142	4	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
273	142	1	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
274	143	13	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
275	144	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
276	144	6	S	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
277	144	15	L	1	60000.00	{"sugar": "50%"}	60000.00	2026-03-07 01:47:31.196239
278	145	14	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
279	146	4	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
280	146	16	L	1	55000.00	{"sugar": "50%"}	55000.00	2026-03-07 01:47:31.196239
281	146	11	M	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
282	147	4	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
283	148	16	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
284	148	14	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
285	148	11	M	1	50000.00	{"sugar": "50%"}	50000.00	2026-03-07 01:47:31.196239
286	149	20	S	1	15000.00	{"sugar": "50%"}	15000.00	2026-03-07 01:47:31.196239
287	149	18	S	1	25000.00	{"sugar": "50%"}	25000.00	2026-03-07 01:47:31.196239
288	150	5	L	1	60000.00	{"sugar": "50%"}	60000.00	2026-03-07 01:47:31.196239
289	150	10	M	1	45000.00	{"sugar": "50%"}	45000.00	2026-03-07 01:47:31.196239
290	150	16	S	1	35000.00	{"sugar": "50%"}	35000.00	2026-03-07 01:47:31.196239
\.


--
-- TOC entry 5137 (class 0 OID 17205)
-- Dependencies: 234
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.orders (id, order_number, customer_id, staff_id, total_amount, discount, final_amount, status, order_date) FROM stdin;
1	ORD20241201001	\N	3	35000.00	1750.00	33250.00	completed	2024-12-01 08:00:00
2	ORD20241202002	18	6	105000.00	0.00	105000.00	completed	2024-12-02 09:00:00
3	ORD20241203003	46	3	125000.00	0.00	125000.00	completed	2024-12-03 10:00:00
4	ORD20241204004	3	3	45000.00	0.00	45000.00	completed	2024-12-04 11:00:00
5	ORD20241205005	\N	3	45000.00	0.00	45000.00	completed	2024-12-05 12:00:00
6	ORD20241206006	\N	5	110000.00	5500.00	104500.00	completed	2024-12-06 13:00:00
7	ORD20241207007	\N	7	70000.00	3500.00	66500.00	completed	2024-12-07 14:00:00
8	ORD20241208008	4	3	45000.00	0.00	45000.00	completed	2024-12-08 15:00:00
9	ORD20241209009	\N	7	140000.00	0.00	140000.00	completed	2024-12-09 16:00:00
10	ORD20241210010	22	6	35000.00	1750.00	33250.00	completed	2024-12-10 17:00:00
11	ORD20241211011	17	2	60000.00	0.00	60000.00	completed	2024-12-11 18:00:00
12	ORD20241212012	33	5	90000.00	4500.00	85500.00	completed	2024-12-12 19:00:00
13	ORD20241213013	39	2	80000.00	0.00	80000.00	completed	2024-12-13 20:00:00
14	ORD20241214014	9	2	60000.00	0.00	60000.00	completed	2024-12-14 07:00:00
15	ORD20241215015	8	2	90000.00	0.00	90000.00	completed	2024-12-15 08:00:00
16	ORD20241216016	\N	3	45000.00	0.00	45000.00	completed	2024-12-16 09:00:00
17	ORD20241217017	21	6	85000.00	0.00	85000.00	completed	2024-12-17 10:00:00
18	ORD20241218018	37	5	120000.00	0.00	120000.00	completed	2024-12-18 11:00:00
19	ORD20241219019	\N	6	85000.00	0.00	85000.00	completed	2024-12-19 12:00:00
20	ORD20241220020	\N	3	135000.00	0.00	135000.00	completed	2024-12-20 13:00:00
21	ORD20241221021	11	3	70000.00	3500.00	66500.00	completed	2024-12-21 14:00:00
22	ORD20241222022	5	6	45000.00	0.00	45000.00	completed	2024-12-22 15:00:00
23	ORD20241223023	\N	7	50000.00	0.00	50000.00	completed	2024-12-23 16:00:00
24	ORD20241224024	17	6	45000.00	0.00	45000.00	completed	2024-12-24 17:00:00
25	ORD20241225025	44	3	110000.00	0.00	110000.00	completed	2024-12-25 18:00:00
26	ORD20241226026	2	7	35000.00	0.00	35000.00	completed	2024-12-26 19:00:00
27	ORD20241227027	43	7	45000.00	0.00	45000.00	completed	2024-12-27 20:00:00
28	ORD20241228028	19	4	95000.00	4750.00	90250.00	completed	2024-12-28 07:00:00
29	ORD20241201029	20	5	55000.00	0.00	55000.00	completed	2024-12-01 08:00:00
30	ORD20241202030	33	6	120000.00	0.00	120000.00	completed	2024-12-02 09:00:00
31	ORD20241203031	40	3	45000.00	0.00	45000.00	completed	2024-12-03 10:00:00
32	ORD20241204032	18	7	120000.00	6000.00	114000.00	completed	2024-12-04 11:00:00
33	ORD20241205033	16	5	25000.00	0.00	25000.00	completed	2024-12-05 12:00:00
34	ORD20241206034	\N	5	90000.00	0.00	90000.00	completed	2024-12-06 13:00:00
35	ORD20241207035	25	6	35000.00	0.00	35000.00	completed	2024-12-07 14:00:00
36	ORD20241208036	24	5	95000.00	0.00	95000.00	completed	2024-12-08 15:00:00
37	ORD20241209037	\N	5	45000.00	0.00	45000.00	completed	2024-12-09 16:00:00
38	ORD20241210038	2	6	105000.00	5250.00	99750.00	completed	2024-12-10 17:00:00
39	ORD20241211039	22	2	110000.00	0.00	110000.00	completed	2024-12-11 18:00:00
40	ORD20241212040	10	6	35000.00	0.00	35000.00	completed	2024-12-12 19:00:00
41	ORD20241213041	\N	7	135000.00	0.00	135000.00	completed	2024-12-13 20:00:00
42	ORD20241214042	\N	6	135000.00	6750.00	128250.00	completed	2024-12-14 07:00:00
43	ORD20241215043	\N	2	145000.00	0.00	145000.00	completed	2024-12-15 08:00:00
44	ORD20241216044	12	6	55000.00	0.00	55000.00	completed	2024-12-16 09:00:00
45	ORD20241217045	\N	2	40000.00	0.00	40000.00	completed	2024-12-17 10:00:00
46	ORD20241218046	36	5	100000.00	5000.00	95000.00	completed	2024-12-18 11:00:00
47	ORD20241219047	14	5	25000.00	0.00	25000.00	completed	2024-12-19 12:00:00
48	ORD20241220048	7	5	70000.00	0.00	70000.00	completed	2024-12-20 13:00:00
49	ORD20241221049	\N	6	110000.00	0.00	110000.00	completed	2024-12-21 14:00:00
50	ORD20241222050	4	6	60000.00	0.00	60000.00	completed	2024-12-22 15:00:00
51	ORD20250101051	15	5	80000.00	0.00	80000.00	completed	2025-01-01 16:00:00
52	ORD20250102052	\N	5	45000.00	0.00	45000.00	completed	2025-01-02 17:00:00
53	ORD20250103053	7	7	150000.00	0.00	150000.00	completed	2025-01-03 18:00:00
54	ORD20250104054	5	7	35000.00	1750.00	33250.00	completed	2025-01-04 19:00:00
55	ORD20250105055	13	4	90000.00	0.00	90000.00	completed	2025-01-05 20:00:00
56	ORD20250106056	33	6	135000.00	0.00	135000.00	completed	2025-01-06 07:00:00
57	ORD20250107057	3	2	145000.00	0.00	145000.00	completed	2025-01-07 08:00:00
58	ORD20250108058	\N	6	125000.00	0.00	125000.00	completed	2025-01-08 09:00:00
59	ORD20250109059	14	3	40000.00	0.00	40000.00	completed	2025-01-09 10:00:00
60	ORD20250110060	37	7	85000.00	0.00	85000.00	completed	2025-01-10 11:00:00
61	ORD20250111061	28	7	60000.00	0.00	60000.00	completed	2025-01-11 12:00:00
62	ORD20250112062	4	5	85000.00	0.00	85000.00	completed	2025-01-12 13:00:00
63	ORD20250113063	36	5	35000.00	0.00	35000.00	completed	2025-01-13 14:00:00
64	ORD20250114064	40	7	90000.00	0.00	90000.00	completed	2025-01-14 15:00:00
65	ORD20250115065	49	2	35000.00	0.00	35000.00	completed	2025-01-15 16:00:00
66	ORD20250116066	21	4	125000.00	6250.00	118750.00	completed	2025-01-16 17:00:00
67	ORD20250117067	\N	2	45000.00	2250.00	42750.00	completed	2025-01-17 18:00:00
68	ORD20250118068	17	5	25000.00	0.00	25000.00	completed	2025-01-18 19:00:00
69	ORD20250119069	30	6	45000.00	2250.00	42750.00	completed	2025-01-19 20:00:00
70	ORD20250120070	47	2	75000.00	0.00	75000.00	completed	2025-01-20 07:00:00
71	ORD20250121071	25	4	25000.00	0.00	25000.00	completed	2025-01-21 08:00:00
72	ORD20250122072	2	3	40000.00	0.00	40000.00	completed	2025-01-22 09:00:00
73	ORD20250123073	38	5	15000.00	0.00	15000.00	completed	2025-01-23 10:00:00
74	ORD20250124074	18	5	50000.00	0.00	50000.00	completed	2025-01-24 11:00:00
75	ORD20250125075	\N	5	90000.00	0.00	90000.00	completed	2025-01-25 12:00:00
76	ORD20250126076	\N	4	100000.00	0.00	100000.00	completed	2025-01-26 13:00:00
77	ORD20250127077	2	7	65000.00	0.00	65000.00	completed	2025-01-27 14:00:00
78	ORD20250128078	34	3	125000.00	0.00	125000.00	completed	2025-01-28 15:00:00
79	ORD20250101079	26	6	30000.00	0.00	30000.00	completed	2025-01-01 16:00:00
80	ORD20250102080	5	4	25000.00	0.00	25000.00	completed	2025-01-02 17:00:00
81	ORD20250103081	31	2	105000.00	0.00	105000.00	completed	2025-01-03 18:00:00
82	ORD20250104082	17	5	15000.00	0.00	15000.00	completed	2025-01-04 19:00:00
83	ORD20250105083	42	2	155000.00	7750.00	147250.00	completed	2025-01-05 20:00:00
84	ORD20250106084	14	7	85000.00	0.00	85000.00	completed	2025-01-06 07:00:00
85	ORD20250107085	\N	2	125000.00	6250.00	118750.00	completed	2025-01-07 08:00:00
86	ORD20250108086	\N	7	40000.00	0.00	40000.00	completed	2025-01-08 09:00:00
87	ORD20250109087	13	2	150000.00	0.00	150000.00	completed	2025-01-09 10:00:00
88	ORD20250110088	\N	3	45000.00	0.00	45000.00	completed	2025-01-10 11:00:00
89	ORD20250111089	12	5	60000.00	0.00	60000.00	completed	2025-01-11 12:00:00
90	ORD20250112090	42	7	55000.00	0.00	55000.00	completed	2025-01-12 13:00:00
91	ORD20250113091	21	3	40000.00	0.00	40000.00	completed	2025-01-13 14:00:00
92	ORD20250114092	23	7	60000.00	0.00	60000.00	completed	2025-01-14 15:00:00
93	ORD20250115093	\N	5	75000.00	3750.00	71250.00	completed	2025-01-15 16:00:00
94	ORD20250116094	13	4	75000.00	3750.00	71250.00	completed	2025-01-16 17:00:00
95	ORD20250117095	\N	3	60000.00	0.00	60000.00	completed	2025-01-17 18:00:00
96	ORD20250118096	4	6	35000.00	1750.00	33250.00	completed	2025-01-18 19:00:00
97	ORD20250119097	4	4	40000.00	0.00	40000.00	completed	2025-01-19 20:00:00
98	ORD20250120098	49	7	85000.00	0.00	85000.00	completed	2025-01-20 07:00:00
99	ORD20250121099	\N	7	15000.00	0.00	15000.00	completed	2025-01-21 08:00:00
100	ORD20250122100	\N	4	65000.00	0.00	65000.00	completed	2025-01-22 09:00:00
101	ORD20250201101	23	5	70000.00	3500.00	66500.00	completed	2025-02-01 10:00:00
102	ORD20250202102	47	6	35000.00	0.00	35000.00	completed	2025-02-02 11:00:00
103	ORD20250203103	10	7	70000.00	0.00	70000.00	completed	2025-02-03 12:00:00
104	ORD20250204104	41	6	50000.00	2500.00	47500.00	completed	2025-02-04 13:00:00
105	ORD20250205105	16	2	35000.00	0.00	35000.00	completed	2025-02-05 14:00:00
106	ORD20250206106	\N	4	110000.00	0.00	110000.00	completed	2025-02-06 15:00:00
107	ORD20250207107	4	4	85000.00	4250.00	80750.00	completed	2025-02-07 16:00:00
108	ORD20250208108	\N	3	105000.00	0.00	105000.00	completed	2025-02-08 17:00:00
109	ORD20250201109	\N	7	35000.00	0.00	35000.00	completed	2025-02-01 18:00:00
110	ORD20250202110	6	5	80000.00	0.00	80000.00	completed	2025-02-02 19:00:00
111	ORD20250203111	\N	7	55000.00	0.00	55000.00	completed	2025-02-03 20:00:00
112	ORD20250204112	19	6	30000.00	1500.00	28500.00	completed	2025-02-04 07:00:00
113	ORD20250205113	32	7	25000.00	0.00	25000.00	completed	2025-02-05 08:00:00
114	ORD20250206114	36	7	110000.00	0.00	110000.00	completed	2025-02-06 09:00:00
115	ORD20250207115	31	6	105000.00	0.00	105000.00	completed	2025-02-07 10:00:00
116	ORD20250208116	28	2	115000.00	0.00	115000.00	completed	2025-02-08 11:00:00
117	ORD20250201117	19	6	15000.00	0.00	15000.00	completed	2025-02-01 12:00:00
118	ORD20250202118	3	7	105000.00	0.00	105000.00	completed	2025-02-02 13:00:00
119	ORD20250203119	18	4	120000.00	0.00	120000.00	completed	2025-02-03 14:00:00
120	ORD20250204120	49	7	25000.00	1250.00	23750.00	completed	2025-02-04 15:00:00
121	ORD20250205121	27	6	35000.00	0.00	35000.00	completed	2025-02-05 16:00:00
122	ORD20250206122	27	4	55000.00	2750.00	52250.00	completed	2025-02-06 17:00:00
123	ORD20250207123	16	6	55000.00	0.00	55000.00	completed	2025-02-07 18:00:00
124	ORD20250208124	\N	5	100000.00	0.00	100000.00	completed	2025-02-08 19:00:00
125	ORD20250201125	40	3	110000.00	0.00	110000.00	completed	2025-02-01 20:00:00
126	ORD20250202126	48	2	95000.00	4750.00	90250.00	completed	2025-02-02 07:00:00
127	ORD20250203127	29	7	90000.00	4500.00	85500.00	completed	2025-02-03 08:00:00
128	ORD20250204128	40	7	45000.00	0.00	45000.00	completed	2025-02-04 09:00:00
129	ORD20250205129	\N	7	35000.00	1750.00	33250.00	completed	2025-02-05 10:00:00
130	ORD20250206130	\N	3	140000.00	7000.00	133000.00	completed	2025-02-06 11:00:00
131	ORD20250207131	\N	5	125000.00	6250.00	118750.00	completed	2025-02-07 12:00:00
132	ORD20250208132	27	2	85000.00	0.00	85000.00	completed	2025-02-08 13:00:00
133	ORD20250201133	36	4	120000.00	6000.00	114000.00	completed	2025-02-01 14:00:00
134	ORD20250202134	\N	3	120000.00	0.00	120000.00	completed	2025-02-02 15:00:00
135	ORD20250203135	42	5	45000.00	0.00	45000.00	completed	2025-02-03 16:00:00
136	ORD20250204136	48	7	130000.00	0.00	130000.00	completed	2025-02-04 17:00:00
137	ORD20250205137	20	3	35000.00	0.00	35000.00	completed	2025-02-05 18:00:00
138	ORD20250206138	41	7	40000.00	0.00	40000.00	completed	2025-02-06 19:00:00
139	ORD20250207139	36	4	50000.00	2500.00	47500.00	completed	2025-02-07 20:00:00
140	ORD20250208140	\N	5	65000.00	0.00	65000.00	completed	2025-02-08 07:00:00
141	ORD20250201141	34	2	70000.00	0.00	70000.00	completed	2025-02-01 08:00:00
142	ORD20250202142	36	6	115000.00	0.00	115000.00	completed	2025-02-02 09:00:00
143	ORD20250203143	38	4	45000.00	0.00	45000.00	completed	2025-02-03 10:00:00
144	ORD20250204144	32	7	130000.00	6500.00	123500.00	completed	2025-02-04 11:00:00
145	ORD20250205145	\N	5	55000.00	0.00	55000.00	completed	2025-02-05 12:00:00
146	ORD20250206146	9	5	150000.00	0.00	150000.00	completed	2025-02-06 13:00:00
147	ORD20250207147	41	5	35000.00	0.00	35000.00	completed	2025-02-07 14:00:00
148	ORD20250208148	10	7	130000.00	0.00	130000.00	completed	2025-02-08 15:00:00
149	ORD20250201149	\N	4	40000.00	0.00	40000.00	completed	2025-02-01 16:00:00
150	ORD20250202150	49	7	140000.00	7000.00	133000.00	completed	2025-02-02 17:00:00
\.


--
-- TOC entry 5141 (class 0 OID 17247)
-- Dependencies: 238
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payments (id, order_id, payment_method, amount, payment_date) FROM stdin;
1	1	cash	33250.00	2026-03-07 01:47:31.196239
2	2	cash	105000.00	2026-03-07 01:47:31.196239
3	3	momo	125000.00	2026-03-07 01:47:31.196239
4	4	cash	45000.00	2026-03-07 01:47:31.196239
5	5	momo	45000.00	2026-03-07 01:47:31.196239
6	6	cash	104500.00	2026-03-07 01:47:31.196239
7	7	card	66500.00	2026-03-07 01:47:31.196239
8	8	momo	45000.00	2026-03-07 01:47:31.196239
9	9	cash	140000.00	2026-03-07 01:47:31.196239
10	10	cash	33250.00	2026-03-07 01:47:31.196239
11	11	momo	60000.00	2026-03-07 01:47:31.196239
12	12	momo	85500.00	2026-03-07 01:47:31.196239
13	13	cash	80000.00	2026-03-07 01:47:31.196239
14	14	momo	60000.00	2026-03-07 01:47:31.196239
15	15	card	90000.00	2026-03-07 01:47:31.196239
16	16	cash	45000.00	2026-03-07 01:47:31.196239
17	17	cash	85000.00	2026-03-07 01:47:31.196239
18	18	card	120000.00	2026-03-07 01:47:31.196239
19	19	momo	85000.00	2026-03-07 01:47:31.196239
20	20	cash	135000.00	2026-03-07 01:47:31.196239
21	21	momo	66500.00	2026-03-07 01:47:31.196239
22	22	momo	45000.00	2026-03-07 01:47:31.196239
23	23	card	50000.00	2026-03-07 01:47:31.196239
24	24	momo	45000.00	2026-03-07 01:47:31.196239
25	25	momo	110000.00	2026-03-07 01:47:31.196239
26	26	momo	35000.00	2026-03-07 01:47:31.196239
27	27	momo	45000.00	2026-03-07 01:47:31.196239
28	28	card	90250.00	2026-03-07 01:47:31.196239
29	29	card	55000.00	2026-03-07 01:47:31.196239
30	30	cash	120000.00	2026-03-07 01:47:31.196239
31	31	momo	45000.00	2026-03-07 01:47:31.196239
32	32	card	114000.00	2026-03-07 01:47:31.196239
33	33	card	25000.00	2026-03-07 01:47:31.196239
34	34	cash	90000.00	2026-03-07 01:47:31.196239
35	35	momo	35000.00	2026-03-07 01:47:31.196239
36	36	momo	95000.00	2026-03-07 01:47:31.196239
37	37	momo	45000.00	2026-03-07 01:47:31.196239
38	38	card	99750.00	2026-03-07 01:47:31.196239
39	39	momo	110000.00	2026-03-07 01:47:31.196239
40	40	card	35000.00	2026-03-07 01:47:31.196239
41	41	cash	135000.00	2026-03-07 01:47:31.196239
42	42	cash	128250.00	2026-03-07 01:47:31.196239
43	43	momo	145000.00	2026-03-07 01:47:31.196239
44	44	cash	55000.00	2026-03-07 01:47:31.196239
45	45	card	40000.00	2026-03-07 01:47:31.196239
46	46	card	95000.00	2026-03-07 01:47:31.196239
47	47	card	25000.00	2026-03-07 01:47:31.196239
48	48	momo	70000.00	2026-03-07 01:47:31.196239
49	49	card	110000.00	2026-03-07 01:47:31.196239
50	50	card	60000.00	2026-03-07 01:47:31.196239
51	51	cash	80000.00	2026-03-07 01:47:31.196239
52	52	card	45000.00	2026-03-07 01:47:31.196239
53	53	card	150000.00	2026-03-07 01:47:31.196239
54	54	card	33250.00	2026-03-07 01:47:31.196239
55	55	card	90000.00	2026-03-07 01:47:31.196239
56	56	cash	135000.00	2026-03-07 01:47:31.196239
57	57	card	145000.00	2026-03-07 01:47:31.196239
58	58	card	125000.00	2026-03-07 01:47:31.196239
59	59	cash	40000.00	2026-03-07 01:47:31.196239
60	60	cash	85000.00	2026-03-07 01:47:31.196239
61	61	cash	60000.00	2026-03-07 01:47:31.196239
62	62	card	85000.00	2026-03-07 01:47:31.196239
63	63	momo	35000.00	2026-03-07 01:47:31.196239
64	64	card	90000.00	2026-03-07 01:47:31.196239
65	65	cash	35000.00	2026-03-07 01:47:31.196239
66	66	momo	118750.00	2026-03-07 01:47:31.196239
67	67	cash	42750.00	2026-03-07 01:47:31.196239
68	68	momo	25000.00	2026-03-07 01:47:31.196239
69	69	momo	42750.00	2026-03-07 01:47:31.196239
70	70	card	75000.00	2026-03-07 01:47:31.196239
71	71	momo	25000.00	2026-03-07 01:47:31.196239
72	72	momo	40000.00	2026-03-07 01:47:31.196239
73	73	cash	15000.00	2026-03-07 01:47:31.196239
74	74	card	50000.00	2026-03-07 01:47:31.196239
75	75	momo	90000.00	2026-03-07 01:47:31.196239
76	76	card	100000.00	2026-03-07 01:47:31.196239
77	77	card	65000.00	2026-03-07 01:47:31.196239
78	78	card	125000.00	2026-03-07 01:47:31.196239
79	79	card	30000.00	2026-03-07 01:47:31.196239
80	80	momo	25000.00	2026-03-07 01:47:31.196239
81	81	cash	105000.00	2026-03-07 01:47:31.196239
82	82	momo	15000.00	2026-03-07 01:47:31.196239
83	83	card	147250.00	2026-03-07 01:47:31.196239
84	84	momo	85000.00	2026-03-07 01:47:31.196239
85	85	card	118750.00	2026-03-07 01:47:31.196239
86	86	cash	40000.00	2026-03-07 01:47:31.196239
87	87	card	150000.00	2026-03-07 01:47:31.196239
88	88	card	45000.00	2026-03-07 01:47:31.196239
89	89	momo	60000.00	2026-03-07 01:47:31.196239
90	90	cash	55000.00	2026-03-07 01:47:31.196239
91	91	card	40000.00	2026-03-07 01:47:31.196239
92	92	momo	60000.00	2026-03-07 01:47:31.196239
93	93	card	71250.00	2026-03-07 01:47:31.196239
94	94	card	71250.00	2026-03-07 01:47:31.196239
95	95	momo	60000.00	2026-03-07 01:47:31.196239
96	96	momo	33250.00	2026-03-07 01:47:31.196239
97	97	card	40000.00	2026-03-07 01:47:31.196239
98	98	momo	85000.00	2026-03-07 01:47:31.196239
99	99	card	15000.00	2026-03-07 01:47:31.196239
100	100	momo	65000.00	2026-03-07 01:47:31.196239
101	101	cash	66500.00	2026-03-07 01:47:31.196239
102	102	momo	35000.00	2026-03-07 01:47:31.196239
103	103	cash	70000.00	2026-03-07 01:47:31.196239
104	104	momo	47500.00	2026-03-07 01:47:31.196239
105	105	momo	35000.00	2026-03-07 01:47:31.196239
106	106	cash	110000.00	2026-03-07 01:47:31.196239
107	107	momo	80750.00	2026-03-07 01:47:31.196239
108	108	card	105000.00	2026-03-07 01:47:31.196239
109	109	cash	35000.00	2026-03-07 01:47:31.196239
110	110	cash	80000.00	2026-03-07 01:47:31.196239
111	111	card	55000.00	2026-03-07 01:47:31.196239
112	112	card	28500.00	2026-03-07 01:47:31.196239
113	113	card	25000.00	2026-03-07 01:47:31.196239
114	114	momo	110000.00	2026-03-07 01:47:31.196239
115	115	momo	105000.00	2026-03-07 01:47:31.196239
116	116	momo	115000.00	2026-03-07 01:47:31.196239
117	117	card	15000.00	2026-03-07 01:47:31.196239
118	118	card	105000.00	2026-03-07 01:47:31.196239
119	119	momo	120000.00	2026-03-07 01:47:31.196239
120	120	card	23750.00	2026-03-07 01:47:31.196239
121	121	momo	35000.00	2026-03-07 01:47:31.196239
122	122	cash	52250.00	2026-03-07 01:47:31.196239
123	123	cash	55000.00	2026-03-07 01:47:31.196239
124	124	momo	100000.00	2026-03-07 01:47:31.196239
125	125	card	110000.00	2026-03-07 01:47:31.196239
126	126	cash	90250.00	2026-03-07 01:47:31.196239
127	127	momo	85500.00	2026-03-07 01:47:31.196239
128	128	momo	45000.00	2026-03-07 01:47:31.196239
129	129	card	33250.00	2026-03-07 01:47:31.196239
130	130	card	133000.00	2026-03-07 01:47:31.196239
131	131	momo	118750.00	2026-03-07 01:47:31.196239
132	132	momo	85000.00	2026-03-07 01:47:31.196239
133	133	card	114000.00	2026-03-07 01:47:31.196239
134	134	cash	120000.00	2026-03-07 01:47:31.196239
135	135	card	45000.00	2026-03-07 01:47:31.196239
136	136	momo	130000.00	2026-03-07 01:47:31.196239
137	137	cash	35000.00	2026-03-07 01:47:31.196239
138	138	card	40000.00	2026-03-07 01:47:31.196239
139	139	momo	47500.00	2026-03-07 01:47:31.196239
140	140	card	65000.00	2026-03-07 01:47:31.196239
141	141	cash	70000.00	2026-03-07 01:47:31.196239
142	142	momo	115000.00	2026-03-07 01:47:31.196239
143	143	cash	45000.00	2026-03-07 01:47:31.196239
144	144	cash	123500.00	2026-03-07 01:47:31.196239
145	145	momo	55000.00	2026-03-07 01:47:31.196239
146	146	card	150000.00	2026-03-07 01:47:31.196239
147	147	cash	35000.00	2026-03-07 01:47:31.196239
148	148	card	130000.00	2026-03-07 01:47:31.196239
149	149	cash	40000.00	2026-03-07 01:47:31.196239
150	150	cash	133000.00	2026-03-07 01:47:31.196239
\.


--
-- TOC entry 5149 (class 0 OID 17492)
-- Dependencies: 246
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.permissions (id, code, name, module, created_at) FROM stdin;
1	order.view	Xem danh sách đơn hàng	order	2026-03-08 14:53:10.423826
2	order.create	Tạo đơn hàng mới	order	2026-03-08 14:53:10.423826
3	order.update	Cập nhật đơn hàng	order	2026-03-08 14:53:10.423826
4	order.delete	Huỷ/xoá đơn hàng	order	2026-03-08 14:53:10.423826
5	order.discount	Áp dụng giảm giá	order	2026-03-08 14:53:10.423826
6	product.view	Xem danh sách sản phẩm	product	2026-03-08 14:53:10.423826
7	product.create	Thêm sản phẩm mới	product	2026-03-08 14:53:10.423826
8	product.update	Sửa thông tin sản phẩm/giá	product	2026-03-08 14:53:10.423826
9	product.delete	Xoá sản phẩm	product	2026-03-08 14:53:10.423826
10	product.toggle	Bật/tắt hiển thị sản phẩm	product	2026-03-08 14:53:10.423826
11	ingredient.view	Xem tồn kho nguyên liệu	ingredient	2026-03-08 14:53:10.423826
12	ingredient.update	Cập nhật số lượng nguyên liệu	ingredient	2026-03-08 14:53:10.423826
13	ingredient.restock	Nhập kho nguyên liệu	ingredient	2026-03-08 14:53:10.423826
14	recipe.view	Xem công thức pha chế	ingredient	2026-03-08 14:53:10.423826
15	recipe.update	Sửa công thức pha chế	ingredient	2026-03-08 14:53:10.423826
16	customer.view	Xem danh sách khách hàng	customer	2026-03-08 14:53:10.423826
17	customer.create	Thêm khách hàng mới	customer	2026-03-08 14:53:10.423826
18	customer.update	Sửa thông tin khách hàng	customer	2026-03-08 14:53:10.423826
19	customer.points	Điều chỉnh điểm tích lũy	customer	2026-03-08 14:53:10.423826
20	staff.view	Xem danh sách nhân viên	staff	2026-03-08 14:53:10.423826
21	staff.create	Thêm nhân viên mới	staff	2026-03-08 14:53:10.423826
22	staff.update	Sửa thông tin nhân viên	staff	2026-03-08 14:53:10.423826
23	staff.delete	Xoá/vô hiệu hoá nhân viên	staff	2026-03-08 14:53:10.423826
24	staff.salary	Xem và sửa lương	staff	2026-03-08 14:53:10.423826
25	worklog.view	Xem bảng chấm công	staff	2026-03-08 14:53:10.423826
26	worklog.update	Sửa dữ liệu chấm công	staff	2026-03-08 14:53:10.423826
27	report.revenue	Xem báo cáo doanh thu	report	2026-03-08 14:53:10.423826
28	report.staff	Xem báo cáo nhân sự	report	2026-03-08 14:53:10.423826
29	report.inventory	Xem báo cáo tồn kho	report	2026-03-08 14:53:10.423826
30	report.export	Xuất báo cáo ra file	report	2026-03-08 14:53:10.423826
31	account.view	Xem danh sách tài khoản	system	2026-03-08 14:53:10.423826
32	account.create	Tạo tài khoản mới	system	2026-03-08 14:53:10.423826
33	account.update	Sửa thông tin tài khoản	system	2026-03-08 14:53:10.423826
34	account.reset_pass	Reset mật khẩu tài khoản khác	system	2026-03-08 14:53:10.423826
35	system.audit_log	Xem lịch sử thao tác hệ thống	system	2026-03-08 14:53:10.423826
\.


--
-- TOC entry 5123 (class 0 OID 17096)
-- Dependencies: 220
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.products (id, category_id, name, description, price_small, price_medium, price_large, image, is_available, created_at) FROM stdin;
1	1	Espresso	Cà phê Espresso nguyên chất Ý	25000.00	35000.00	45000.00	/images/espresso.jpg	t	2026-03-07 01:47:31.196239
2	1	Americano	Espresso pha loãng	30000.00	40000.00	50000.00	/images/americano.jpg	t	2026-03-07 01:47:31.196239
3	1	Cappuccino	Espresso + sữa + bọt	35000.00	45000.00	55000.00	/images/cappuccino.jpg	t	2026-03-07 01:47:31.196239
4	1	Latte	Espresso + nhiều sữa	35000.00	45000.00	55000.00	/images/latte.jpg	t	2026-03-07 01:47:31.196239
5	1	Mocha	Latte + chocolate	40000.00	50000.00	60000.00	/images/mocha.jpg	t	2026-03-07 01:47:31.196239
6	1	Caramel Macchiato	Latte + caramel	45000.00	55000.00	65000.00	/images/caramel.jpg	t	2026-03-07 01:47:31.196239
7	1	Cà phê đen	Cà phê phin VN	25000.00	30000.00	35000.00	/images/black.jpg	t	2026-03-07 01:47:31.196239
8	1	Cà phê sữa	Phin + sữa đặc	30000.00	35000.00	40000.00	/images/milk.jpg	t	2026-03-07 01:47:31.196239
9	2	Trà xanh	Trà xanh Thái Nguyên	25000.00	30000.00	35000.00	/images/green-tea.jpg	t	2026-03-07 01:47:31.196239
10	2	Trà đào cam sả	Trà đen + đào + cam	35000.00	45000.00	55000.00	/images/peach.jpg	t	2026-03-07 01:47:31.196239
11	2	Trà sữa trân châu	Trà sữa + trân châu	40000.00	50000.00	60000.00	/images/bubble.jpg	t	2026-03-07 01:47:31.196239
12	2	Matcha latte	Matcha + sữa	45000.00	55000.00	65000.00	/images/matcha.jpg	t	2026-03-07 01:47:31.196239
13	2	Hồng trà sữa	Hồng trà + sữa	35000.00	45000.00	55000.00	/images/milk-tea.jpg	t	2026-03-07 01:47:31.196239
14	3	Sinh tố dâu	Dâu + sữa	35000.00	45000.00	55000.00	/images/strawberry.jpg	t	2026-03-07 01:47:31.196239
15	3	Sinh tố bơ	Bơ + sữa đặc	40000.00	50000.00	60000.00	/images/avocado.jpg	t	2026-03-07 01:47:31.196239
16	3	Sinh tố xoài	Xoài + sữa chua	35000.00	45000.00	55000.00	/images/mango.jpg	t	2026-03-07 01:47:31.196239
17	3	Nước ép cam	Cam tươi 100%	30000.00	40000.00	50000.00	/images/orange.jpg	t	2026-03-07 01:47:31.196239
18	4	Croissant	Bánh sừng bò Pháp	25000.00	\N	\N	/images/croissant.jpg	t	2026-03-07 01:47:31.196239
19	4	Tiramisu	Tiramisu Ý	45000.00	\N	\N	/images/tiramisu.jpg	t	2026-03-07 01:47:31.196239
20	4	Bánh mì que	Bánh mì giòn	15000.00	\N	\N	/images/bread.jpg	t	2026-03-07 01:47:31.196239
\.


--
-- TOC entry 5145 (class 0 OID 17460)
-- Dependencies: 242
-- Data for Name: recipes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.recipes (id, product_id, ingredient_id, quantity_small, quantity_medium, quantity_large, created_at) FROM stdin;
1	1	1	9.00	18.00	27.00	2026-03-07 02:01:14.190525
2	2	1	9.00	18.00	18.00	2026-03-07 02:01:14.190525
3	2	24	5.00	8.00	10.00	2026-03-07 02:01:14.190525
4	2	25	100.00	150.00	200.00	2026-03-07 02:01:14.190525
5	3	1	9.00	18.00	18.00	2026-03-07 02:01:14.190525
6	3	4	90.00	120.00	150.00	2026-03-07 02:01:14.190525
7	3	24	5.00	8.00	10.00	2026-03-07 02:01:14.190525
8	4	1	9.00	18.00	18.00	2026-03-07 02:01:14.190525
9	4	4	180.00	240.00	300.00	2026-03-07 02:01:14.190525
10	4	12	10.00	15.00	20.00	2026-03-07 02:01:14.190525
11	4	24	5.00	8.00	10.00	2026-03-07 02:01:14.190525
12	5	1	9.00	18.00	18.00	2026-03-07 02:01:14.190525
13	5	4	150.00	200.00	250.00	2026-03-07 02:01:14.190525
14	5	13	20.00	30.00	40.00	2026-03-07 02:01:14.190525
15	5	10	30.00	45.00	60.00	2026-03-07 02:01:14.190525
16	5	24	8.00	12.00	15.00	2026-03-07 02:01:14.190525
17	5	25	80.00	120.00	150.00	2026-03-07 02:01:14.190525
18	6	1	9.00	18.00	18.00	2026-03-07 02:01:14.190525
19	6	4	180.00	240.00	300.00	2026-03-07 02:01:14.190525
20	6	11	15.00	20.00	25.00	2026-03-07 02:01:14.190525
21	6	12	15.00	20.00	25.00	2026-03-07 02:01:14.190525
22	6	10	20.00	30.00	40.00	2026-03-07 02:01:14.190525
23	6	24	5.00	8.00	10.00	2026-03-07 02:01:14.190525
24	6	25	100.00	150.00	200.00	2026-03-07 02:01:14.190525
25	7	3	20.00	25.00	30.00	2026-03-07 02:01:14.190525
26	7	24	0.00	5.00	10.00	2026-03-07 02:01:14.190525
27	7	25	80.00	120.00	150.00	2026-03-07 02:01:14.190525
28	8	3	20.00	25.00	30.00	2026-03-07 02:01:14.190525
29	8	5	20.00	25.00	30.00	2026-03-07 02:01:14.190525
30	8	25	100.00	150.00	200.00	2026-03-07 02:01:14.190525
31	9	15	5.00	8.00	10.00	2026-03-07 02:01:14.190525
32	9	24	10.00	15.00	20.00	2026-03-07 02:01:14.190525
33	9	25	80.00	120.00	150.00	2026-03-07 02:01:14.190525
34	10	16	8.00	12.00	15.00	2026-03-07 02:01:14.190525
35	10	20	60.00	90.00	120.00	2026-03-07 02:01:14.190525
36	10	22	30.00	50.00	70.00	2026-03-07 02:01:14.190525
37	10	26	5.00	8.00	10.00	2026-03-07 02:01:14.190525
38	10	24	15.00	20.00	25.00	2026-03-07 02:01:14.190525
39	10	25	100.00	150.00	200.00	2026-03-07 02:01:14.190525
40	11	16	8.00	12.00	15.00	2026-03-07 02:01:14.190525
41	11	4	100.00	150.00	200.00	2026-03-07 02:01:14.190525
42	11	14	30.00	50.00	70.00	2026-03-07 02:01:14.190525
43	11	24	15.00	20.00	25.00	2026-03-07 02:01:14.190525
44	11	25	80.00	120.00	150.00	2026-03-07 02:01:14.190525
45	12	17	5.00	8.00	10.00	2026-03-07 02:01:14.190525
46	12	4	180.00	240.00	300.00	2026-03-07 02:01:14.190525
47	12	24	10.00	15.00	20.00	2026-03-07 02:01:14.190525
48	12	25	80.00	120.00	150.00	2026-03-07 02:01:14.190525
49	13	18	8.00	12.00	15.00	2026-03-07 02:01:14.190525
50	13	4	120.00	170.00	220.00	2026-03-07 02:01:14.190525
51	13	24	15.00	20.00	25.00	2026-03-07 02:01:14.190525
52	13	25	80.00	120.00	150.00	2026-03-07 02:01:14.190525
53	14	19	100.00	150.00	200.00	2026-03-07 02:01:14.190525
54	14	9	50.00	80.00	100.00	2026-03-07 02:01:14.190525
55	14	4	50.00	80.00	100.00	2026-03-07 02:01:14.190525
56	14	24	10.00	15.00	20.00	2026-03-07 02:01:14.190525
57	14	25	50.00	80.00	100.00	2026-03-07 02:01:14.190525
58	15	23	120.00	180.00	240.00	2026-03-07 02:01:14.190525
59	15	5	20.00	30.00	40.00	2026-03-07 02:01:14.190525
60	15	4	60.00	90.00	120.00	2026-03-07 02:01:14.190525
61	15	25	50.00	80.00	100.00	2026-03-07 02:01:14.190525
62	16	21	120.00	180.00	240.00	2026-03-07 02:01:14.190525
63	16	9	40.00	60.00	80.00	2026-03-07 02:01:14.190525
64	16	4	50.00	80.00	100.00	2026-03-07 02:01:14.190525
65	16	24	8.00	12.00	15.00	2026-03-07 02:01:14.190525
66	16	25	50.00	80.00	100.00	2026-03-07 02:01:14.190525
67	17	22	200.00	300.00	400.00	2026-03-07 02:01:14.190525
68	17	24	5.00	8.00	10.00	2026-03-07 02:01:14.190525
69	17	25	50.00	80.00	100.00	2026-03-07 02:01:14.190525
\.


--
-- TOC entry 5155 (class 0 OID 17547)
-- Dependencies: 252
-- Data for Name: refresh_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.refresh_tokens (id, account_id, token_hash, device_info, ip_address, expires_at, is_revoked, created_at) FROM stdin;
\.


--
-- TOC entry 5151 (class 0 OID 17502)
-- Dependencies: 248
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.role_permissions (id, role_id, permission_id) FROM stdin;
1	1	1
2	1	2
3	1	3
4	1	4
5	1	5
6	1	6
7	1	7
8	1	8
9	1	9
10	1	10
11	1	11
12	1	12
13	1	13
14	1	14
15	1	15
16	1	16
17	1	17
18	1	18
19	1	19
20	1	20
21	1	21
22	1	22
23	1	23
24	1	24
25	1	25
26	1	26
27	1	27
28	1	28
29	1	29
30	1	30
31	1	31
32	1	32
33	1	33
34	1	34
35	1	35
36	2	1
37	2	2
38	2	3
39	2	5
40	2	6
41	2	10
42	2	11
43	2	16
44	2	17
45	2	18
46	2	25
47	3	1
48	3	6
49	3	11
50	3	14
51	3	25
52	4	1
53	4	2
54	4	6
55	4	16
\.


--
-- TOC entry 5147 (class 0 OID 17480)
-- Dependencies: 244
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, name, display_name, description, created_at) FROM stdin;
1	quan_ly	Quản lý	Toàn quyền hệ thống, xem báo cáo, quản lý nhân sự	2026-03-08 14:53:10.423826
2	thu_ngan	Thu ngân	Tạo/sửa đơn hàng, thanh toán, tra cứu khách hàng	2026-03-08 14:53:10.423826
3	barista	Barista	Xem đơn hàng, xem công thức, kiểm tra nguyên liệu	2026-03-08 14:53:10.423826
4	part_time	Part-time	Quyền hạn chế: chỉ xem đơn và tạo đơn cơ bản	2026-03-08 14:53:10.423826
\.


--
-- TOC entry 5133 (class 0 OID 17181)
-- Dependencies: 230
-- Data for Name: staff; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.staff (id, name, phone, email, role, salary, hire_date, is_active, created_at) FROM stdin;
1	Nguyễn Văn Quản Lý	0971111111	manager@coffee.com	Quản lý	15000000.00	2023-06-01	t	2026-03-07 01:47:31.196239
2	Trần Thị Thu Ngân 1	0972222222	cashier1@coffee.com	Thu ngân	8000000.00	2023-08-15	t	2026-03-07 01:47:31.196239
3	Lê Thị Thu Ngân 2	0973333333	cashier2@coffee.com	Thu ngân	7500000.00	2024-01-10	t	2026-03-07 01:47:31.196239
4	Phạm Văn Barista 1	0974444444	barista1@coffee.com	Barista	9000000.00	2023-07-20	t	2026-03-07 01:47:31.196239
5	Hoàng Thị Barista 2	0975555555	barista2@coffee.com	Barista	8500000.00	2023-09-01	t	2026-03-07 01:47:31.196239
6	Võ Văn Barista 3	0976666666	barista3@coffee.com	Barista	8000000.00	2024-02-01	t	2026-03-07 01:47:31.196239
7	Đặng Thị Barista 4	0977777777	barista4@coffee.com	Barista	7800000.00	2024-11-15	t	2026-03-07 01:47:31.196239
8	Bùi Văn Part-time	0978888888	parttime@coffee.com	Part-time	50000.00	2024-12-01	t	2026-03-07 01:47:31.196239
\.


--
-- TOC entry 5135 (class 0 OID 17192)
-- Dependencies: 232
-- Data for Name: work_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.work_logs (id, staff_id, work_date, check_in, check_out, hours_worked, created_at) FROM stdin;
1	1	2024-12-01	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
2	2	2024-12-01	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
3	3	2024-12-01	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
4	4	2024-12-01	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
5	5	2024-12-01	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
6	6	2024-12-01	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
7	1	2024-12-02	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
8	2	2024-12-02	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
9	3	2024-12-02	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
10	4	2024-12-02	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
11	5	2024-12-02	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
12	6	2024-12-02	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
13	1	2024-12-03	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
14	2	2024-12-03	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
15	3	2024-12-03	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
16	4	2024-12-03	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
17	5	2024-12-03	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
18	6	2024-12-03	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
19	1	2024-12-04	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
20	2	2024-12-04	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
21	3	2024-12-04	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
22	4	2024-12-04	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
23	5	2024-12-04	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
24	6	2024-12-04	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
25	1	2024-12-05	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
26	2	2024-12-05	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
27	3	2024-12-05	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
28	4	2024-12-05	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
29	5	2024-12-05	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
30	6	2024-12-05	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
31	1	2024-12-06	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
32	2	2024-12-06	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
33	3	2024-12-06	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
34	4	2024-12-06	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
35	5	2024-12-06	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
36	6	2024-12-06	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
37	1	2024-12-07	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
38	2	2024-12-07	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
39	3	2024-12-07	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
40	4	2024-12-07	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
41	5	2024-12-07	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
42	6	2024-12-07	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
43	1	2024-12-08	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
44	2	2024-12-08	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
45	3	2024-12-08	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
46	4	2024-12-08	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
47	5	2024-12-08	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
48	6	2024-12-08	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
49	1	2024-12-09	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
50	2	2024-12-09	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
51	3	2024-12-09	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
52	4	2024-12-09	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
53	5	2024-12-09	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
54	6	2024-12-09	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
55	1	2024-12-10	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
56	2	2024-12-10	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
57	3	2024-12-10	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
58	4	2024-12-10	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
59	5	2024-12-10	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
60	6	2024-12-10	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
61	1	2024-12-11	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
62	2	2024-12-11	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
63	3	2024-12-11	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
64	4	2024-12-11	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
65	5	2024-12-11	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
66	6	2024-12-11	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
67	1	2024-12-12	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
68	2	2024-12-12	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
69	3	2024-12-12	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
70	4	2024-12-12	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
71	5	2024-12-12	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
72	6	2024-12-12	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
73	1	2024-12-13	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
74	2	2024-12-13	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
75	3	2024-12-13	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
76	4	2024-12-13	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
77	5	2024-12-13	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
78	6	2024-12-13	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
79	1	2024-12-14	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
80	2	2024-12-14	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
81	3	2024-12-14	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
82	4	2024-12-14	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
83	5	2024-12-14	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
84	6	2024-12-14	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
85	1	2024-12-15	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
86	2	2024-12-15	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
87	3	2024-12-15	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
88	4	2024-12-15	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
89	5	2024-12-15	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
90	6	2024-12-15	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
91	1	2024-12-16	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
92	2	2024-12-16	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
93	3	2024-12-16	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
94	4	2024-12-16	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
95	5	2024-12-16	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
96	6	2024-12-16	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
97	1	2024-12-17	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
98	2	2024-12-17	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
99	3	2024-12-17	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
100	4	2024-12-17	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
101	5	2024-12-17	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
102	6	2024-12-17	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
103	1	2024-12-18	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
104	2	2024-12-18	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
105	3	2024-12-18	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
106	4	2024-12-18	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
107	5	2024-12-18	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
108	6	2024-12-18	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
109	1	2024-12-19	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
110	2	2024-12-19	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
111	3	2024-12-19	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
112	4	2024-12-19	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
113	5	2024-12-19	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
114	6	2024-12-19	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
115	1	2024-12-20	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
116	2	2024-12-20	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
117	3	2024-12-20	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
118	4	2024-12-20	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
119	5	2024-12-20	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
120	6	2024-12-20	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
121	1	2024-12-21	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
122	2	2024-12-21	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
123	3	2024-12-21	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
124	4	2024-12-21	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
125	5	2024-12-21	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
126	6	2024-12-21	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
127	1	2024-12-22	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
128	2	2024-12-22	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
129	3	2024-12-22	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
130	4	2024-12-22	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
131	5	2024-12-22	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
132	6	2024-12-22	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
133	1	2024-12-23	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
134	2	2024-12-23	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
135	3	2024-12-23	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
136	4	2024-12-23	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
137	5	2024-12-23	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
138	6	2024-12-23	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
139	1	2024-12-24	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
140	2	2024-12-24	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
141	3	2024-12-24	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
142	4	2024-12-24	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
143	5	2024-12-24	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
144	6	2024-12-24	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
145	1	2024-12-25	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
146	2	2024-12-25	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
147	3	2024-12-25	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
148	4	2024-12-25	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
149	5	2024-12-25	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
150	6	2024-12-25	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
151	1	2024-12-26	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
152	2	2024-12-26	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
153	3	2024-12-26	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
154	4	2024-12-26	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
155	5	2024-12-26	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
156	6	2024-12-26	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
157	1	2024-12-27	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
158	2	2024-12-27	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
159	3	2024-12-27	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
160	4	2024-12-27	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
161	5	2024-12-27	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
162	6	2024-12-27	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
163	1	2024-12-28	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
164	2	2024-12-28	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
165	3	2024-12-28	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
166	4	2024-12-28	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
167	5	2024-12-28	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
168	6	2024-12-28	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
169	1	2024-12-29	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
170	2	2024-12-29	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
171	3	2024-12-29	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
172	4	2024-12-29	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
173	5	2024-12-29	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
174	6	2024-12-29	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
175	1	2024-12-30	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
176	2	2024-12-30	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
177	3	2024-12-30	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
178	4	2024-12-30	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
179	5	2024-12-30	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
180	6	2024-12-30	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
181	1	2024-12-31	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
182	2	2024-12-31	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
183	3	2024-12-31	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
184	4	2024-12-31	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
185	5	2024-12-31	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
186	6	2024-12-31	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
187	8	2024-12-01	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
188	8	2024-12-07	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
189	8	2024-12-08	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
190	8	2024-12-14	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
191	8	2024-12-15	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
192	8	2024-12-21	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
193	8	2024-12-22	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
194	8	2024-12-28	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
195	8	2024-12-29	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
196	1	2025-01-01	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
197	2	2025-01-01	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
198	3	2025-01-01	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
199	4	2025-01-01	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
200	5	2025-01-01	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
201	6	2025-01-01	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
202	1	2025-01-02	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
203	2	2025-01-02	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
204	3	2025-01-02	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
205	4	2025-01-02	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
206	5	2025-01-02	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
207	6	2025-01-02	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
208	1	2025-01-03	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
209	2	2025-01-03	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
210	3	2025-01-03	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
211	4	2025-01-03	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
212	5	2025-01-03	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
213	6	2025-01-03	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
214	1	2025-01-04	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
215	2	2025-01-04	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
216	3	2025-01-04	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
217	4	2025-01-04	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
218	5	2025-01-04	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
219	6	2025-01-04	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
220	1	2025-01-05	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
221	2	2025-01-05	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
222	3	2025-01-05	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
223	4	2025-01-05	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
224	5	2025-01-05	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
225	6	2025-01-05	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
226	1	2025-01-06	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
227	2	2025-01-06	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
228	3	2025-01-06	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
229	4	2025-01-06	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
230	5	2025-01-06	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
231	6	2025-01-06	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
232	1	2025-01-07	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
233	2	2025-01-07	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
234	3	2025-01-07	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
235	4	2025-01-07	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
236	5	2025-01-07	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
237	6	2025-01-07	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
238	1	2025-01-08	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
239	2	2025-01-08	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
240	3	2025-01-08	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
241	4	2025-01-08	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
242	5	2025-01-08	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
243	6	2025-01-08	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
244	1	2025-01-09	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
245	2	2025-01-09	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
246	3	2025-01-09	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
247	4	2025-01-09	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
248	5	2025-01-09	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
249	6	2025-01-09	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
250	1	2025-01-10	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
251	2	2025-01-10	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
252	3	2025-01-10	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
253	4	2025-01-10	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
254	5	2025-01-10	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
255	6	2025-01-10	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
256	1	2025-01-11	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
257	2	2025-01-11	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
258	3	2025-01-11	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
259	4	2025-01-11	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
260	5	2025-01-11	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
261	6	2025-01-11	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
262	1	2025-01-12	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
263	2	2025-01-12	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
264	3	2025-01-12	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
265	4	2025-01-12	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
266	5	2025-01-12	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
267	6	2025-01-12	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
268	1	2025-01-13	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
269	2	2025-01-13	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
270	3	2025-01-13	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
271	4	2025-01-13	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
272	5	2025-01-13	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
273	6	2025-01-13	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
274	1	2025-01-14	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
275	2	2025-01-14	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
276	3	2025-01-14	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
277	4	2025-01-14	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
278	5	2025-01-14	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
279	6	2025-01-14	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
280	1	2025-01-15	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
281	2	2025-01-15	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
282	3	2025-01-15	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
283	4	2025-01-15	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
284	5	2025-01-15	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
285	6	2025-01-15	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
286	1	2025-01-16	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
287	2	2025-01-16	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
288	3	2025-01-16	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
289	4	2025-01-16	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
290	5	2025-01-16	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
291	6	2025-01-16	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
292	1	2025-01-17	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
293	2	2025-01-17	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
294	3	2025-01-17	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
295	4	2025-01-17	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
296	5	2025-01-17	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
297	6	2025-01-17	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
298	1	2025-01-18	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
299	2	2025-01-18	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
300	3	2025-01-18	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
301	4	2025-01-18	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
302	5	2025-01-18	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
303	6	2025-01-18	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
304	1	2025-01-19	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
305	2	2025-01-19	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
306	3	2025-01-19	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
307	4	2025-01-19	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
308	5	2025-01-19	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
309	6	2025-01-19	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
310	1	2025-01-20	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
311	2	2025-01-20	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
312	3	2025-01-20	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
313	4	2025-01-20	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
314	5	2025-01-20	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
315	6	2025-01-20	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
316	1	2025-01-21	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
317	2	2025-01-21	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
318	3	2025-01-21	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
319	4	2025-01-21	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
320	5	2025-01-21	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
321	6	2025-01-21	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
322	1	2025-01-22	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
323	2	2025-01-22	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
324	3	2025-01-22	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
325	4	2025-01-22	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
326	5	2025-01-22	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
327	6	2025-01-22	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
328	1	2025-01-23	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
329	2	2025-01-23	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
330	3	2025-01-23	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
331	4	2025-01-23	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
332	5	2025-01-23	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
333	6	2025-01-23	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
334	1	2025-01-24	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
335	2	2025-01-24	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
336	3	2025-01-24	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
337	4	2025-01-24	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
338	5	2025-01-24	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
339	6	2025-01-24	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
340	1	2025-01-25	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
341	2	2025-01-25	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
342	3	2025-01-25	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
343	4	2025-01-25	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
344	5	2025-01-25	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
345	6	2025-01-25	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
346	1	2025-01-26	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
347	2	2025-01-26	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
348	3	2025-01-26	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
349	4	2025-01-26	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
350	5	2025-01-26	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
351	6	2025-01-26	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
352	1	2025-01-27	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
353	2	2025-01-27	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
354	3	2025-01-27	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
355	4	2025-01-27	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
356	5	2025-01-27	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
357	6	2025-01-27	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
358	1	2025-01-28	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
359	2	2025-01-28	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
360	3	2025-01-28	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
361	4	2025-01-28	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
362	5	2025-01-28	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
363	6	2025-01-28	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
364	1	2025-01-29	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
365	2	2025-01-29	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
366	3	2025-01-29	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
367	4	2025-01-29	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
368	5	2025-01-29	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
369	6	2025-01-29	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
370	1	2025-01-30	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
371	2	2025-01-30	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
372	3	2025-01-30	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
373	4	2025-01-30	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
374	5	2025-01-30	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
375	6	2025-01-30	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
376	1	2025-01-31	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
377	2	2025-01-31	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
378	3	2025-01-31	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
379	4	2025-01-31	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
380	5	2025-01-31	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
381	6	2025-01-31	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
382	8	2025-01-04	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
383	8	2025-01-05	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
384	8	2025-01-11	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
385	8	2025-01-12	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
386	8	2025-01-18	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
387	8	2025-01-19	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
388	8	2025-01-25	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
389	8	2025-01-26	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
390	1	2025-02-01	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
391	2	2025-02-01	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
392	3	2025-02-01	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
393	4	2025-02-01	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
394	5	2025-02-01	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
395	6	2025-02-01	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
396	1	2025-02-02	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
397	2	2025-02-02	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
398	3	2025-02-02	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
399	4	2025-02-02	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
400	5	2025-02-02	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
401	6	2025-02-02	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
402	1	2025-02-03	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
403	2	2025-02-03	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
404	3	2025-02-03	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
405	4	2025-02-03	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
406	5	2025-02-03	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
407	6	2025-02-03	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
408	1	2025-02-04	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
409	2	2025-02-04	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
410	3	2025-02-04	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
411	4	2025-02-04	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
412	5	2025-02-04	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
413	6	2025-02-04	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
414	1	2025-02-05	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
415	2	2025-02-05	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
416	3	2025-02-05	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
417	4	2025-02-05	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
418	5	2025-02-05	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
419	6	2025-02-05	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
420	1	2025-02-06	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
421	2	2025-02-06	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
422	3	2025-02-06	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
423	4	2025-02-06	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
424	5	2025-02-06	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
425	6	2025-02-06	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
426	1	2025-02-07	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
427	2	2025-02-07	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
428	3	2025-02-07	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
429	4	2025-02-07	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
430	5	2025-02-07	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
431	6	2025-02-07	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
432	1	2025-02-08	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
433	2	2025-02-08	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
434	3	2025-02-08	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
435	4	2025-02-08	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
436	5	2025-02-08	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
437	6	2025-02-08	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
438	1	2025-02-09	07:30:00	17:30:00	10.00	2026-03-07 01:47:31.196239
439	2	2025-02-09	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
440	3	2025-02-09	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
441	4	2025-02-09	07:00:00	15:00:00	8.00	2026-03-07 01:47:31.196239
442	5	2025-02-09	09:00:00	17:00:00	8.00	2026-03-07 01:47:31.196239
443	6	2025-02-09	15:00:00	23:00:00	8.00	2026-03-07 01:47:31.196239
444	8	2025-02-01	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
445	8	2025-02-02	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
446	8	2025-02-08	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
447	8	2025-02-09	10:00:00	18:00:00	8.00	2026-03-07 01:47:31.196239
\.


--
-- TOC entry 5183 (class 0 OID 0)
-- Dependencies: 249
-- Name: accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.accounts_id_seq', 8, true);


--
-- TOC entry 5184 (class 0 OID 0)
-- Dependencies: 253
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 1, false);


--
-- TOC entry 5185 (class 0 OID 0)
-- Dependencies: 217
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categories_id_seq', 4, true);


--
-- TOC entry 5186 (class 0 OID 0)
-- Dependencies: 225
-- Name: customers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.customers_id_seq', 50, true);


--
-- TOC entry 5187 (class 0 OID 0)
-- Dependencies: 223
-- Name: customizations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.customizations_id_seq', 15, true);


--
-- TOC entry 5188 (class 0 OID 0)
-- Dependencies: 239
-- Name: daily_stats_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.daily_stats_id_seq', 64, true);


--
-- TOC entry 5189 (class 0 OID 0)
-- Dependencies: 227
-- Name: favorite_drinks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.favorite_drinks_id_seq', 20, true);


--
-- TOC entry 5190 (class 0 OID 0)
-- Dependencies: 221
-- Name: ingredients_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ingredients_id_seq', 26, true);


--
-- TOC entry 5191 (class 0 OID 0)
-- Dependencies: 235
-- Name: order_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.order_items_id_seq', 290, true);


--
-- TOC entry 5192 (class 0 OID 0)
-- Dependencies: 233
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.orders_id_seq', 150, true);


--
-- TOC entry 5193 (class 0 OID 0)
-- Dependencies: 237
-- Name: payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payments_id_seq', 150, true);


--
-- TOC entry 5194 (class 0 OID 0)
-- Dependencies: 245
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.permissions_id_seq', 35, true);


--
-- TOC entry 5195 (class 0 OID 0)
-- Dependencies: 219
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.products_id_seq', 20, true);


--
-- TOC entry 5196 (class 0 OID 0)
-- Dependencies: 241
-- Name: recipes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.recipes_id_seq', 69, true);


--
-- TOC entry 5197 (class 0 OID 0)
-- Dependencies: 251
-- Name: refresh_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.refresh_tokens_id_seq', 1, false);


--
-- TOC entry 5198 (class 0 OID 0)
-- Dependencies: 247
-- Name: role_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.role_permissions_id_seq', 56, true);


--
-- TOC entry 5199 (class 0 OID 0)
-- Dependencies: 243
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 4, true);


--
-- TOC entry 5200 (class 0 OID 0)
-- Dependencies: 229
-- Name: staff_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.staff_id_seq', 8, true);


--
-- TOC entry 5201 (class 0 OID 0)
-- Dependencies: 231
-- Name: work_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.work_logs_id_seq', 447, true);


--
-- TOC entry 4943 (class 2606 OID 17531)
-- Name: accounts accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (id);


--
-- TOC entry 4945 (class 2606 OID 17533)
-- Name: accounts accounts_staff_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_staff_id_key UNIQUE (staff_id);


--
-- TOC entry 4947 (class 2606 OID 17535)
-- Name: accounts accounts_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_username_key UNIQUE (username);


--
-- TOC entry 4955 (class 2606 OID 17571)
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 4888 (class 2606 OID 17094)
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- TOC entry 4897 (class 2606 OID 17159)
-- Name: customers customers_phone_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_phone_key UNIQUE (phone);


--
-- TOC entry 4899 (class 2606 OID 17157)
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (id);


--
-- TOC entry 4895 (class 2606 OID 17147)
-- Name: customizations customizations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customizations
    ADD CONSTRAINT customizations_pkey PRIMARY KEY (id);


--
-- TOC entry 4922 (class 2606 OID 17269)
-- Name: daily_stats daily_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_stats
    ADD CONSTRAINT daily_stats_pkey PRIMARY KEY (id);


--
-- TOC entry 4924 (class 2606 OID 17271)
-- Name: daily_stats daily_stats_stat_date_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_stats
    ADD CONSTRAINT daily_stats_stat_date_key UNIQUE (stat_date);


--
-- TOC entry 4901 (class 2606 OID 17169)
-- Name: favorite_drinks favorite_drinks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorite_drinks
    ADD CONSTRAINT favorite_drinks_pkey PRIMARY KEY (id);


--
-- TOC entry 4893 (class 2606 OID 17120)
-- Name: ingredients ingredients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ingredients
    ADD CONSTRAINT ingredients_pkey PRIMARY KEY (id);


--
-- TOC entry 4918 (class 2606 OID 17235)
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (id);


--
-- TOC entry 4913 (class 2606 OID 17215)
-- Name: orders orders_order_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_order_number_key UNIQUE (order_number);


--
-- TOC entry 4915 (class 2606 OID 17213)
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- TOC entry 4920 (class 2606 OID 17253)
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- TOC entry 4935 (class 2606 OID 17500)
-- Name: permissions permissions_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_code_key UNIQUE (code);


--
-- TOC entry 4937 (class 2606 OID 17498)
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- TOC entry 4891 (class 2606 OID 17105)
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- TOC entry 4929 (class 2606 OID 17466)
-- Name: recipes recipes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipes
    ADD CONSTRAINT recipes_pkey PRIMARY KEY (id);


--
-- TOC entry 4953 (class 2606 OID 17556)
-- Name: refresh_tokens refresh_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id);


--
-- TOC entry 4939 (class 2606 OID 17507)
-- Name: role_permissions role_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_pkey PRIMARY KEY (id);


--
-- TOC entry 4941 (class 2606 OID 17509)
-- Name: role_permissions role_permissions_role_id_permission_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_role_id_permission_id_key UNIQUE (role_id, permission_id);


--
-- TOC entry 4931 (class 2606 OID 17490)
-- Name: roles roles_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);


--
-- TOC entry 4933 (class 2606 OID 17488)
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- TOC entry 4903 (class 2606 OID 17190)
-- Name: staff staff_phone_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.staff
    ADD CONSTRAINT staff_phone_key UNIQUE (phone);


--
-- TOC entry 4905 (class 2606 OID 17188)
-- Name: staff staff_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.staff
    ADD CONSTRAINT staff_pkey PRIMARY KEY (id);


--
-- TOC entry 4909 (class 2606 OID 17198)
-- Name: work_logs work_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_logs
    ADD CONSTRAINT work_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 4948 (class 1259 OID 17579)
-- Name: idx_accounts_role; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_accounts_role ON public.accounts USING btree (role_id);


--
-- TOC entry 4949 (class 1259 OID 17578)
-- Name: idx_accounts_staff; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_accounts_staff ON public.accounts USING btree (staff_id);


--
-- TOC entry 4950 (class 1259 OID 17577)
-- Name: idx_accounts_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_accounts_username ON public.accounts USING btree (username);


--
-- TOC entry 4956 (class 1259 OID 17581)
-- Name: idx_audit_logs_account; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_logs_account ON public.audit_logs USING btree (account_id);


--
-- TOC entry 4957 (class 1259 OID 17582)
-- Name: idx_audit_logs_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_logs_created ON public.audit_logs USING btree (created_at);


--
-- TOC entry 4925 (class 1259 OID 17278)
-- Name: idx_daily_stats_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_daily_stats_date ON public.daily_stats USING btree (stat_date);


--
-- TOC entry 4916 (class 1259 OID 17275)
-- Name: idx_order_items_order; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_order_items_order ON public.order_items USING btree (order_id);


--
-- TOC entry 4910 (class 1259 OID 17273)
-- Name: idx_orders_customer; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_orders_customer ON public.orders USING btree (customer_id);


--
-- TOC entry 4911 (class 1259 OID 17274)
-- Name: idx_orders_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_orders_date ON public.orders USING btree (order_date);


--
-- TOC entry 4889 (class 1259 OID 17272)
-- Name: idx_products_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_products_category ON public.products USING btree (category_id);


--
-- TOC entry 4926 (class 1259 OID 17478)
-- Name: idx_recipes_ingredient; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_recipes_ingredient ON public.recipes USING btree (ingredient_id);


--
-- TOC entry 4927 (class 1259 OID 17477)
-- Name: idx_recipes_product; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_recipes_product ON public.recipes USING btree (product_id);


--
-- TOC entry 4951 (class 1259 OID 17580)
-- Name: idx_refresh_tokens_acct; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_refresh_tokens_acct ON public.refresh_tokens USING btree (account_id);


--
-- TOC entry 4906 (class 1259 OID 17277)
-- Name: idx_work_logs_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_work_logs_date ON public.work_logs USING btree (work_date);


--
-- TOC entry 4907 (class 1259 OID 17276)
-- Name: idx_work_logs_staff; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_work_logs_staff ON public.work_logs USING btree (staff_id);


--
-- TOC entry 4971 (class 2606 OID 17541)
-- Name: accounts accounts_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE SET NULL;


--
-- TOC entry 4972 (class 2606 OID 17536)
-- Name: accounts accounts_staff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.staff(id) ON DELETE CASCADE;


--
-- TOC entry 4974 (class 2606 OID 17572)
-- Name: audit_logs audit_logs_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(id) ON DELETE SET NULL;


--
-- TOC entry 4959 (class 2606 OID 17170)
-- Name: favorite_drinks favorite_drinks_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorite_drinks
    ADD CONSTRAINT favorite_drinks_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id) ON DELETE CASCADE;


--
-- TOC entry 4960 (class 2606 OID 17175)
-- Name: favorite_drinks favorite_drinks_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorite_drinks
    ADD CONSTRAINT favorite_drinks_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE CASCADE;


--
-- TOC entry 4964 (class 2606 OID 17236)
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- TOC entry 4965 (class 2606 OID 17241)
-- Name: order_items order_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE SET NULL;


--
-- TOC entry 4962 (class 2606 OID 17216)
-- Name: orders orders_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id) ON DELETE SET NULL;


--
-- TOC entry 4963 (class 2606 OID 17221)
-- Name: orders orders_staff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.staff(id) ON DELETE SET NULL;


--
-- TOC entry 4966 (class 2606 OID 17254)
-- Name: payments payments_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- TOC entry 4958 (class 2606 OID 17106)
-- Name: products products_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE SET NULL;


--
-- TOC entry 4967 (class 2606 OID 17472)
-- Name: recipes recipes_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipes
    ADD CONSTRAINT recipes_ingredient_id_fkey FOREIGN KEY (ingredient_id) REFERENCES public.ingredients(id) ON DELETE CASCADE;


--
-- TOC entry 4968 (class 2606 OID 17467)
-- Name: recipes recipes_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipes
    ADD CONSTRAINT recipes_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE CASCADE;


--
-- TOC entry 4973 (class 2606 OID 17557)
-- Name: refresh_tokens refresh_tokens_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(id) ON DELETE CASCADE;


--
-- TOC entry 4969 (class 2606 OID 17515)
-- Name: role_permissions role_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE;


--
-- TOC entry 4970 (class 2606 OID 17510)
-- Name: role_permissions role_permissions_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- TOC entry 4961 (class 2606 OID 17199)
-- Name: work_logs work_logs_staff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_logs
    ADD CONSTRAINT work_logs_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.staff(id) ON DELETE CASCADE;


-- Completed on 2026-03-08 15:25:18

--
-- PostgreSQL database dump complete
--

\unrestrict QfPKcsc9ul4plcu6bprIaT4GCnvfQtirnOMQnhp7jVQpQMKTjrKQChMdHdgV63x

