PRAGMA foreign_keys = ON;

-- =========================
-- account_master
-- =========================
DROP TABLE IF EXISTS account_master;
CREATE TABLE account_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    party_name TEXT,
    provider_names TEXT,
    contact TEXT,
    address TEXT,
    pdf_path TEXT,
    login_id INTEGER
);

-- =========================
-- delivery_manage_master
-- =========================
DROP TABLE IF EXISTS delivery_manage_master;
CREATE TABLE delivery_manage_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quot_no TEXT,
    part_no TEXT,
    delivery_qty INTEGER,
    delivery_dt TEXT,
    login_id INTEGER
);

-- =========================
-- firm_master
-- =========================
DROP TABLE IF EXISTS firm_master;
CREATE TABLE firm_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_name TEXT,
    firm_address TEXT,
    firm_contact TEXT,
    login_id INTEGER
);

-- =========================
-- login_master
-- =========================
DROP TABLE IF EXISTS login_master;
CREATE TABLE login_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firm_id INTEGER,
    user_name TEXT,
    user_pass TEXT
);

INSERT INTO login_master (id, firm_id, user_name, user_pass)
VALUES (1, 1, 'admin', 'admin');

-- =========================
-- machining_master
-- =========================
DROP TABLE IF EXISTS machining_master;
CREATE TABLE machining_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL
);

-- =========================
-- master_table
-- =========================
DROP TABLE IF EXISTS master_table;
CREATE TABLE master_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    customer_contact TEXT,
    date_of_activation TEXT,
    client_hard_key TEXT,
    client_secret_key TEXT,
    valid_till TEXT,
    active INTEGER
);

-- =========================
-- material_master
-- =========================
DROP TABLE IF EXISTS material_master;
CREATE TABLE material_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    density REAL,
    rate REAL,
    login_id INTEGER
);

INSERT INTO material_master VALUES
(1,'M.S',7860,130,1),
(2,'S.S',8000,400,1),
(3,'Al',2700,650,1),
(4,'20MnCr5',8000,140,1),
(5,'EN8',8000,85,1),
(6,'8620',8000,100,1),
(7,'Copper',8960,853,1),
(8,'Gun metal',8719,875,1),
(9,'Nylon',1160,1000,1),
(10,'UHMW',970,950,1),
(11,'PU',961,1250,1),
(12,'Delrin',1420,500,1),
(13,'Kelvler',1440,1800,1);

-- =========================
-- quotation_master
-- =========================
DROP TABLE IF EXISTS quotation_master;
CREATE TABLE quotation_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quotation_id TEXT,
    invoice_id TEXT,
    cust_id INTEGER,
    cust_name TEXT,
    provider_name TEXT,
    date_tr_quot TEXT,
    invoice_generated TEXT,
    invoice_tr_date TEXT,
    login_id INTEGER
);

-- =========================
-- quotation_master_details
-- =========================
DROP TABLE IF EXISTS quotation_master_details;
CREATE TABLE quotation_master_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Quotation_Id TEXT,
    part_no TEXT,
    part_desc TEXT,
    part_qty INTEGER,
    material TEXT,
    unit_measurement TEXT,
    shape TEXT,
    width REAL,
    length_part REAL,
    thickness REAL,
    unit_weight REAL,
    rmc REAL,
    profit_per REAL,
    unit_price TEXT,
    total_price REAL,
    date_tr TEXT,
    delivery_flag TEXT,
    login_id INTEGER
);

-- =========================
-- quotation_master_details_machining_details
-- =========================
DROP TABLE IF EXISTS quotation_master_details_machining_details;
CREATE TABLE quotation_master_details_machining_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Quotation_Id TEXT,
    part_no_id TEXT,
    machining_name TEXT,
    lbl_rate REAL,
    cust_rate REAL,
    total_hr REAL,
    date_tr TEXT,
    login_id INTEGER
);

-- =========================
-- raw_cost
-- =========================
DROP TABLE IF EXISTS raw_cost;
CREATE TABLE raw_cost (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL
);

-- =========================
-- secret_key
-- =========================
DROP TABLE IF EXISTS secret_key;
CREATE TABLE secret_key (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    secret_key_hard TEXT,
    secret_key_1 TEXT,
    secret_keycol TEXT,
    valid_from TEXT,
    valid_till TEXT,
    active_ TEXT
);
