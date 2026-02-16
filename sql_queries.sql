-- Consultas SQL para análisis de soporte TI
-- Compatible con SQL ANSI y PL/SQL básico

-- 1. Tickets abiertos por categoría
SELECT 
    categoria,
    COUNT(*) as tickets_abiertos,
    AVG(tiempo_resolucion_horas) as tiempo_promedio_horas
FROM tickets
WHERE estado IN ('Abierto', 'En Progreso')
GROUP BY categoria
ORDER BY tickets_abiertos DESC;

-- 2. Performance de agentes
SELECT 
    agente_asignado,
    COUNT(*) as total_tickets,
    COUNT(CASE WHEN estado IN ('Resuelto', 'Cerrado') THEN 1 END) as tickets_resueltos,
    ROUND(AVG(tiempo_resolucion_horas), 2) as tiempo_promedio_horas,
    ROUND(AVG(satisfaccion_cliente), 2) as satisfaccion_promedio
FROM tickets
WHERE fecha_creacion >= DATE('now', '-30 days')
GROUP BY agente_asignado
ORDER BY tickets_resueltos DESC;

-- 3. Tickets por prioridad y estado
SELECT 
    prioridad,
    estado,
    COUNT(*) as cantidad,
    ROUND(AVG(tiempo_resolucion_horas), 2) as tiempo_promedio
FROM tickets
GROUP BY prioridad, estado
ORDER BY 
    CASE prioridad
        WHEN 'Crítica' THEN 1
        WHEN 'Alta' THEN 2
        WHEN 'Media' THEN 3
        WHEN 'Baja' THEN 4
    END,
    cantidad DESC;

-- 4. Tendencia de tickets por semana
SELECT 
    strftime('%Y-%W', fecha_creacion) as semana,
    COUNT(*) as tickets_creados,
    COUNT(CASE WHEN estado IN ('Resuelto', 'Cerrado') THEN 1 END) as tickets_resueltos,
    ROUND(COUNT(CASE WHEN estado IN ('Resuelto', 'Cerrado') THEN 1 END) * 100.0 / COUNT(*), 2) as tasa_resolucion
FROM tickets
GROUP BY semana
ORDER BY semana DESC
LIMIT 8;

-- 5. Tickets que exceden SLA (más de 24 horas)
SELECT 
    ticket_id,
    categoria,
    prioridad,
    tiempo_resolucion_horas,
    agente_asignado,
    fecha_creacion
FROM tickets
WHERE tiempo_resolucion_horas > 24
    AND estado IN ('Resuelto', 'Cerrado')
ORDER BY tiempo_resolucion_horas DESC;

-- 6. Satisfacción por categoría
SELECT 
    categoria,
    COUNT(*) as total_tickets,
    ROUND(AVG(satisfaccion_cliente), 2) as satisfaccion_promedio,
    COUNT(CASE WHEN satisfaccion_cliente >= 4 THEN 1 END) as satisfechos,
    ROUND(COUNT(CASE WHEN satisfaccion_cliente >= 4 THEN 1 END) * 100.0 / COUNT(*), 2) as pct_satisfechos
FROM tickets
WHERE satisfaccion_cliente IS NOT NULL
GROUP BY categoria
ORDER BY satisfaccion_promedio DESC;

-- 7. Distribución de tickets por canal
SELECT 
    canal,
    COUNT(*) as total_tickets,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM tickets), 2) as porcentaje
FROM tickets
GROUP BY canal
ORDER BY total_tickets DESC;

-- 8. Tickets pendientes de resolución (más de 3 días)
SELECT 
    ticket_id,
    categoria,
    prioridad,
    fecha_creacion,
    agente_asignado,
    ROUND(julianday('now') - julianday(fecha_creacion), 2) as dias_pendiente
FROM tickets
WHERE estado IN ('Abierto', 'En Progreso')
    AND julianday('now') - julianday(fecha_creacion) > 3
ORDER BY dias_pendiente DESC;

-- 9. Resumen diario de actividad
SELECT 
    DATE(fecha_creacion) as fecha,
    COUNT(*) as tickets_creados,
    COUNT(CASE WHEN estado IN ('Resuelto', 'Cerrado') THEN 1 END) as tickets_resueltos,
    ROUND(AVG(tiempo_resolucion_horas), 2) as tiempo_promedio_horas
FROM tickets
WHERE fecha_creacion >= DATE('now', '-7 days')
GROUP BY DATE(fecha_creacion)
ORDER BY fecha DESC;

-- 10. Top 5 categorías con más tickets
SELECT 
    categoria,
    COUNT(*) as total_tickets,
    ROUND(AVG(tiempo_resolucion_horas), 2) as tiempo_promedio,
    ROUND(AVG(satisfaccion_cliente), 2) as satisfaccion_promedio
FROM tickets
GROUP BY categoria
ORDER BY total_tickets DESC
LIMIT 5;
