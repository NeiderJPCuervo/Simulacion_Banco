# 🏦 Simulación de Colas y Atención Bancaria

Este proyecto implementa un modelo de simulación matemática basado en **teoría de colas** y **métodos de Monte Carlo** para analizar y optimizar la eficiencia en la atención al cliente de una entidad bancaria. 

El script evalúa dinámicamente diferentes configuraciones de cajeros (uso mixto vs. atención exclusiva por tipo de transacción) con el objetivo de minimizar los tiempos de espera y mantener una correcta utilización del sistema.

## 🚀 Características Principales

- **Modelado Estocástico de Llegadas y Servicios:** Utiliza distribuciones exponenciales para simular el comportamiento y flujo real de los clientes.
- **Clasificación Detallada de Usuarios:** Segmenta las transacciones en `Retiros` y `Pagos`, asignando subtipos de velocidad (Rápido, Normal, Lento, Muy Lento) con sus respectivas probabilidades.
- **Evaluación Comparativa de Escenarios:** - Simulación de una línea base con 3 cajeros mixtos.
  - Evaluación de configuraciones dedicadas (ej. asignación de cajeros exclusivos para retiros y otros para pagos).
- **Generación de Métricas Clave:** Calcula métricas operativas fundamentales como el tiempo de servicio, el tiempo de espera en cola ($W_q$) y el factor de utilización ($\\rho$).
- **Sistema de Diagnóstico Automatizado:** Genera recomendaciones directas sobre la necesidad de incorporar nuevos cajeros si se superan los umbrales críticos (espera mayor a 5 minutos o utilización > 85%).

## 🛠️ Requisitos del Sistema

Para ejecutar esta simulación, el entorno debe contar con **Python 3.x** y las siguientes librerías de manipulación y análisis de datos:

```bash
pip install numpy pandas
