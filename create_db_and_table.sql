CREATE DATABASE tg_bot;

CREATE TABLE data_api (
    id CONSTRAINT firstkey PRIMARY KEY,
    timestamp_arrival INT,
    station TEXT,
    direction TEXT,
    stops TEXT,
    thread TEXT,
    type TEXT
);