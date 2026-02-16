# Analizador de Soporte TI - Métricas y Automatización

Sistema de análisis de tickets de soporte TI con integración de métricas, consultas SQL y automatización de procesos. Incluye análisis de performance, dashboards para Power BI y scripts de automatización.

## Descripción

Este proyecto implementa un sistema completo de análisis de soporte TI que:
- Analiza tickets de soporte y calcula métricas clave
- Utiliza SQL para consultas y reportes
- Genera datos para dashboards en Power BI
- Simula automatizaciones (Zendesk, Slack, Power Automate)
- Documenta procesos y flujos de trabajo

Desarrollado para demostrar competencias en análisis de soporte TI, SQL, Power BI y automatización de procesos.

## Tecnologías

- Python 3.8+
- SQL (SQLite, compatible con SQL ANSI)
- Pandas - análisis de datos
- Power BI - visualización (datos exportados)

## Estructura del Proyecto

```
ti-support-analytics/
│
├── support_analyzer.py      # Analizador principal de tickets
├── automation_scripts.py    # Scripts de automatización
├── sql_queries.sql          # Consultas SQL para análisis
├── requirements.txt         # Dependencias
└── README.md               # Documentación
```

## Instalación

```bash
# Clonar repositorio
git clone https://github.com/JosefaOgalde/ti-support-analytics.git
cd ti-support-analytics

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

### Análisis de Tickets

```bash
python support_analyzer.py
```

Esto generará:
- Base de datos SQLite con tickets de ejemplo
- Cálculo de métricas de soporte
- Reportes SQL
- Exportación para Power BI

### Automatizaciones

```bash
python automation_scripts.py
```

Simula:
- Integración con Zendesk API
- Notificaciones a Slack
- Auto-asignación de tickets
- Reportes automatizados

### Consultas SQL

Ejecuta las consultas en `sql_queries.sql` usando cualquier cliente SQL:
- SQLite (incluido)
- PostgreSQL
- Oracle
- SQL Server

## Métricas Calculadas

- **Tickets totales, resueltos y abiertos**
- **Tiempo promedio de resolución**
- **Tasa de resolución**
- **SLA 24 horas**
- **Satisfacción promedio**
- **Distribución por categoría, prioridad y canal**
- **Performance por agente**

## Integración con Herramientas

### Power BI
Los datos se exportan en formato JSON listo para importar en Power BI y crear dashboards interactivos.

### Zendesk / Slack
El código incluye simulaciones de integración con APIs de Zendesk y Slack, demostrando conocimiento de integraciones.

### Power Automate
Los scripts de automatización simulan procesos que pueden implementarse en Power Automate.

## Consultas SQL Incluidas

- Tickets abiertos por categoría
- Performance de agentes
- Tickets por prioridad y estado
- Tendencia semanal
- Tickets que exceden SLA
- Satisfacción por categoría
- Distribución por canal
- Tickets pendientes
- Resumen diario
- Top categorías

## Experiencia Relevante

Este proyecto demuestra competencias adquiridas trabajando con:
- **Zendesk** - Gestión de tickets y atención al cliente
- **Slack** - Comunicación y notificaciones
- **Análisis de datos** - Métricas de servicio y performance
- **Automatización** - Procesos de soporte automatizados

## Autor

Josefa Ogalde - Ingeniera en Informática

---

*Proyecto desarrollado para demostrar competencias en análisis de soporte TI, SQL, Power BI y automatización.*
