-- 1. Temperatura media por sala
CREATE OR REPLACE VIEW avg_temp_por_sala AS
SELECT
    room_id,
    ROUND(AVG(temp)::numeric, 2) AS avg_temp,
    COUNT(*) AS total_leituras
FROM temperature_readings
GROUP BY room_id;

-- 2. Quantidade de leituras por hora
CREATE OR REPLACE VIEW leituras_por_hora AS
SELECT
    EXTRACT(HOUR FROM noted_date)::integer AS hora,
    COUNT(*) AS contagem
FROM temperature_readings
GROUP BY EXTRACT(HOUR FROM noted_date);

-- 3. Temperaturas maxima, minima e media por dia
CREATE OR REPLACE VIEW temp_max_min_por_dia AS
SELECT
    CAST(noted_date AS date) AS data,
    MAX(temp) AS temp_max,
    MIN(temp) AS temp_min,
    ROUND(AVG(temp)::numeric, 2) AS temp_media
FROM temperature_readings
GROUP BY CAST(noted_date AS date);

-- 4. Comparacao de temperaturas por origem
CREATE OR REPLACE VIEW avg_temp_por_origem AS
SELECT
    out_in,
    ROUND(AVG(temp)::numeric, 2) AS avg_temp,
    COUNT(*) AS total_leituras
FROM temperature_readings
GROUP BY out_in;
