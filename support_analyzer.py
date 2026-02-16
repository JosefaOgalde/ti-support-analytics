"""
Analizador de tickets de soporte TI
Análisis de métricas de servicio y automatización de procesos
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SupportAnalyzer:
    """Analizador de tickets de soporte y métricas de servicio"""
    
    def __init__(self, db_path='support_tickets.db'):
        """
        Inicializa el analizador de soporte.
        
        Args:
            db_path: Ruta a la base de datos SQLite
        """
        self.db_path = db_path
        self.conn = None
        self.metrics = {}
    
    def connect_db(self):
        """Conecta a la base de datos SQLite"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            logger.info(f"Conectado a base de datos: {self.db_path}")
            return self.conn
        except Exception as e:
            logger.error(f"Error al conectar a BD: {str(e)}")
            raise
    
    def create_tables(self):
        """Crea las tablas necesarias en la base de datos"""
        cursor = self.conn.cursor()
        
        # Tabla de tickets
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT UNIQUE,
                fecha_creacion DATE,
                fecha_resolucion DATE,
                categoria TEXT,
                prioridad TEXT,
                estado TEXT,
                agente_asignado TEXT,
                tiempo_resolucion_horas REAL,
                canal TEXT,
                satisfaccion_cliente INTEGER,
                descripcion TEXT
            )
        ''')
        
        # Tabla de métricas diarias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metricas_diarias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE,
                tickets_abiertos INTEGER,
                tickets_resueltos INTEGER,
                tiempo_promedio_resolucion REAL,
                satisfaccion_promedio REAL,
                tickets_por_categoria TEXT
            )
        ''')
        
        self.conn.commit()
        logger.info("Tablas creadas exitosamente")
    
    def insert_sample_tickets(self, n_tickets=200):
        """Inserta tickets de ejemplo para análisis"""
        logger.info(f"Generando {n_tickets} tickets de ejemplo...")
        
        np.random.seed(42)
        cursor = self.conn.cursor()
        
        categorias = ['Hardware', 'Software', 'Red', 'Acceso', 'Email', 'Impresora']
        prioridades = ['Baja', 'Media', 'Alta', 'Crítica']
        estados = ['Abierto', 'En Progreso', 'Resuelto', 'Cerrado']
        canales = ['Email', 'Teléfono', 'Chat', 'Portal', 'Slack']
        agentes = ['Agente1', 'Agente2', 'Agente3', 'Agente4']
        
        base_date = datetime.now() - timedelta(days=60)
        
        for i in range(n_tickets):
            fecha_creacion = base_date + timedelta(days=np.random.randint(0, 60))
            tiempo_resolucion = np.random.exponential(24)  # Horas
            
            # Tickets resueltos tienen fecha de resolución
            if np.random.random() > 0.2:  # 80% resueltos
                fecha_resolucion = fecha_creacion + timedelta(hours=tiempo_resolucion)
                estado = np.random.choice(['Resuelto', 'Cerrado'], p=[0.7, 0.3])
            else:
                fecha_resolucion = None
                estado = np.random.choice(['Abierto', 'En Progreso'], p=[0.3, 0.7])
            
            satisfaccion = np.random.randint(1, 6) if fecha_resolucion else None
            
            cursor.execute('''
                INSERT OR IGNORE INTO tickets 
                (ticket_id, fecha_creacion, fecha_resolucion, categoria, prioridad, 
                 estado, agente_asignado, tiempo_resolucion_horas, canal, 
                 satisfaccion_cliente, descripcion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                f'TICK-{i+1:04d}',
                fecha_creacion.strftime('%Y-%m-%d'),
                fecha_resolucion.strftime('%Y-%m-%d') if fecha_resolucion else None,
                np.random.choice(categorias),
                np.random.choice(prioridades, p=[0.3, 0.4, 0.2, 0.1]),
                estado,
                np.random.choice(agentes),
                tiempo_resolucion if fecha_resolucion else None,
                np.random.choice(canales),
                satisfaccion,
                f"Ticket de ejemplo {i+1}"
            ))
        
        self.conn.commit()
        logger.info(f"{n_tickets} tickets insertados")
    
    def calculate_metrics(self):
        """Calcula métricas de soporte"""
        logger.info("Calculando métricas de soporte...")
        
        # Leer datos desde SQL
        df = pd.read_sql_query('''
            SELECT 
                fecha_creacion,
                fecha_resolucion,
                categoria,
                prioridad,
                estado,
                tiempo_resolucion_horas,
                satisfaccion_cliente,
                canal
            FROM tickets
        ''', self.conn)
        
        df['fecha_creacion'] = pd.to_datetime(df['fecha_creacion'])
        if 'fecha_resolucion' in df.columns:
            df['fecha_resolucion'] = pd.to_datetime(df['fecha_resolucion'])
        
        # Métricas generales
        total_tickets = len(df)
        tickets_resueltos = len(df[df['estado'].isin(['Resuelto', 'Cerrado'])])
        tickets_abiertos = total_tickets - tickets_resueltos
        tasa_resolucion = (tickets_resueltos / total_tickets * 100) if total_tickets > 0 else 0
        
        # Tiempo promedio de resolución
        tiempos_resueltos = df[df['tiempo_resolucion_horas'].notna()]['tiempo_resolucion_horas']
        tiempo_promedio = tiempos_resueltos.mean() if len(tiempos_resueltos) > 0 else 0
        
        # Satisfacción promedio
        satisfacciones = df[df['satisfaccion_cliente'].notna()]['satisfaccion_cliente']
        satisfaccion_promedio = satisfacciones.mean() if len(satisfacciones) > 0 else 0
        
        # Tickets por categoría
        tickets_por_categoria = df['categoria'].value_counts().to_dict()
        
        # Tickets por prioridad
        tickets_por_prioridad = df['prioridad'].value_counts().to_dict()
        
        # Tickets por canal
        tickets_por_canal = df['canal'].value_counts().to_dict()
        
        # SLA (tickets resueltos en menos de 24 horas)
        sla_24h = len(tiempos_resueltos[tiempos_resueltos <= 24]) / len(tiempos_resueltos) * 100 if len(tiempos_resueltos) > 0 else 0
        
        self.metrics = {
            'total_tickets': total_tickets,
            'tickets_resueltos': tickets_resueltos,
            'tickets_abiertos': tickets_abiertos,
            'tasa_resolucion': round(tasa_resolucion, 2),
            'tiempo_promedio_resolucion_horas': round(tiempo_promedio, 2),
            'satisfaccion_promedio': round(satisfaccion_promedio, 2),
            'sla_24h': round(sla_24h, 2),
            'tickets_por_categoria': tickets_por_categoria,
            'tickets_por_prioridad': tickets_por_prioridad,
            'tickets_por_canal': tickets_por_canal
        }
        
        logger.info("Métricas calculadas exitosamente")
        return self.metrics
    
    def generate_sql_report(self):
        """Genera reporte usando consultas SQL"""
        logger.info("Generando reporte SQL...")
        
        cursor = self.conn.cursor()
        
        # Consulta 1: Tickets por categoría y estado
        cursor.execute('''
            SELECT 
                categoria,
                estado,
                COUNT(*) as cantidad,
                AVG(tiempo_resolucion_horas) as tiempo_promedio
            FROM tickets
            GROUP BY categoria, estado
            ORDER BY categoria, cantidad DESC
        ''')
        
        reporte_categoria = cursor.fetchall()
        
        # Consulta 2: Performance por agente
        cursor.execute('''
            SELECT 
                agente_asignado,
                COUNT(*) as total_tickets,
                AVG(tiempo_resolucion_horas) as tiempo_promedio,
                AVG(satisfaccion_cliente) as satisfaccion_promedio
            FROM tickets
            WHERE estado IN ('Resuelto', 'Cerrado')
            GROUP BY agente_asignado
            ORDER BY total_tickets DESC
        ''')
        
        reporte_agentes = cursor.fetchall()
        
        # Consulta 3: Tendencia semanal
        cursor.execute('''
            SELECT 
                strftime('%Y-%W', fecha_creacion) as semana,
                COUNT(*) as tickets_creados,
                COUNT(CASE WHEN estado IN ('Resuelto', 'Cerrado') THEN 1 END) as tickets_resueltos
            FROM tickets
            GROUP BY semana
            ORDER BY semana DESC
            LIMIT 8
        ''')
        
        reporte_semanal = cursor.fetchall()
        
        return {
            'por_categoria': reporte_categoria,
            'por_agente': reporte_agentes,
            'tendencia_semanal': reporte_semanal
        }
    
    def export_for_powerbi(self, output_path='powerbi_support_data.json'):
        """Exporta datos formateados para Power BI"""
        logger.info("Exportando datos para Power BI...")
        
        # Leer datos completos
        df = pd.read_sql_query('SELECT * FROM tickets', self.conn)
        
        # Preparar datos para Power BI
        powerbi_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics,
            'tickets': df.to_dict('records'),
            'summary': {
                'total_tickets': len(df),
                'date_range': {
                    'start': df['fecha_creacion'].min() if 'fecha_creacion' in df.columns else None,
                    'end': df['fecha_creacion'].max() if 'fecha_creacion' in df.columns else None
                }
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(powerbi_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Datos exportados a: {output_path}")
        return output_path
    
    def get_summary_report(self):
        """Genera reporte resumen"""
        report = "\n" + "=" * 60
        report += "\nREPORTE DE MÉTRICAS DE SOPORTE TI"
        report += "\n" + "=" * 60
        
        if not self.metrics:
            return report + "\nNo hay métricas calculadas. Ejecuta calculate_metrics() primero."
        
        report += f"\n\n📊 MÉTRICAS GENERALES"
        report += f"\n  Total de tickets: {self.metrics['total_tickets']}"
        report += f"\n  Tickets resueltos: {self.metrics['tickets_resueltos']}"
        report += f"\n  Tickets abiertos: {self.metrics['tickets_abiertos']}"
        report += f"\n  Tasa de resolución: {self.metrics['tasa_resolucion']}%"
        
        report += f"\n\n⏱️ TIEMPOS DE RESOLUCIÓN"
        report += f"\n  Tiempo promedio: {self.metrics['tiempo_promedio_resolucion_horas']:.2f} horas"
        report += f"\n  SLA 24h: {self.metrics['sla_24h']:.2f}%"
        
        report += f"\n\n😊 SATISFACCIÓN"
        report += f"\n  Satisfacción promedio: {self.metrics['satisfaccion_promedio']:.2f}/5"
        
        report += f"\n\n📁 TICKETS POR CATEGORÍA"
        for categoria, cantidad in self.metrics['tickets_por_categoria'].items():
            report += f"\n  {categoria}: {cantidad}"
        
        report += f"\n\n📞 TICKETS POR CANAL"
        for canal, cantidad in self.metrics['tickets_por_canal'].items():
            report += f"\n  {canal}: {cantidad}"
        
        report += "\n" + "=" * 60
        
        return report
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()
            logger.info("Conexión cerrada")


def main():
    """Función principal"""
    analyzer = SupportAnalyzer()
    
    try:
        # Conectar y crear tablas
        analyzer.connect_db()
        analyzer.create_tables()
        
        # Insertar datos de ejemplo
        analyzer.insert_sample_tickets(n_tickets=200)
        
        # Calcular métricas
        analyzer.calculate_metrics()
        
        # Generar reportes SQL
        sql_reports = analyzer.generate_sql_report()
        
        # Mostrar reporte resumen
        print(analyzer.get_summary_report())
        
        # Exportar para Power BI
        analyzer.export_for_powerbi()
        
        # Mostrar algunos reportes SQL
        print("\n" + "=" * 60)
        print("REPORTE SQL - PERFORMANCE POR AGENTE")
        print("=" * 60)
        for agente, total, tiempo, satisfaccion in sql_reports['por_agente']:
            print(f"  {agente}: {total} tickets, {tiempo:.2f}h promedio, {satisfaccion:.2f} satisfacción")
        
    finally:
        analyzer.close()


if __name__ == "__main__":
    main()
