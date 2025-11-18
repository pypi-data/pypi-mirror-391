# Detector de Anomalías de Rendimiento

[![CI](https://img.shields.io/github/actions/workflow/status/ezequielranieridev/anomaly-detector-seo/ci.yml?branch=main&label=CI)](https://github.com/ezequielranieridev/anomaly-detector-seo/actions)
[![Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen.svg)](https://github.com/ezequielranieridev/anomaly-detector-seo/actions)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

## Acerca de

Microservicio responsable de centralizar logs del ecosistema SEO, detectar anomalías de rendimiento y disparar alertas operativas. Conecta con Loki y Prometheus para observabilidad de punta a punta y expone una API FastAPI preparada para escenarios multi-tenant.

- Sitio/landing: [https://anomaly-detector.ranieri.dev](https://anomaly-detector.ranieri.dev) *(placeholder, actualizar con enlace oficial si aplica)*
- Demo rápida: `docker compose up` + `uvicorn src.api.main:app`
- Documentación de la API: consultar `/docs` una vez desplegado el servicio.

### Estado del proyecto

- Versión estable recomendada: `v1.0.0` (ver [CHANGELOG](CHANGELOG.md)).
- Pipelines de CI y cobertura ejecutan en GitHub Actions (`ci.yml`).
- Compatibilidad verificada en Python 3.10 y 3.12.

## Características principales

- **Ingesta** de logs estructurados y envío a Loki.
- **Detección** de anomalías basada en modelos de machine learning.
- **Alertas** automáticas hacia canales críticos (Slack u otros).
- **Infraestructura observability-ready** vía `docker-compose` (Loki, Promtail, Grafana).

### Arquitectura

```
                   ┌──────────────────────┐
                   │   Clientes / Grafana │
                   │ Dashboards & Alertas │
                   └───────┬──────────────┘
                           │  Prometheus scrape / dashboards
            ┌──────────────▼───────────────┐
            │       FastAPI Service        │
            │  (/healthz, /metrics, /prom) │
            └───────┬─────────┬────────────┘
                    │         │
       API ingest    │         │ expose metrics
 ┌──────────────────▼─┐     ┌─▼─────────────────────────┐
 │  Anomaly Store     │     │ Prometheus Instrumentator │
 │ (Memory / SQLite)  │     └────────────────────────────┘
 └────────┬───────────┘
          │ read/write detecciones & drift
 ┌────────▼─────────┐
 │ Detection        │  emite alertas Slack / RCA
 │ Orchestrator     │────────────► Slack Webhook
 │ (IsolationForest)│
 └────────┬─────────┘
          │ fetch logs & training data
 ┌────────▼─────────┐
 │   Loki Ingestion  │◄──────────────┐
 │ (HTTP API)        │               │
 └────────┬─────────┘               │
          │ push                     │
 ┌────────▼─────────┐                │
 │ Scheduled Jobs   │  retraining    │
 │ (main_scheduler) │──────────────► Retrain Manager
 └──────────────────┘                │
                                     │ persiste modelo & estado
                                     ▼
                               Model Artifacts / Retrain State
```

## Casos de uso típicos

- **Monitoreo de servicios SEO**: detectar latencias anómalas en rastreadores, indexadores o APIs internas.
- **Alertas tempranas de degradación**: notificar al equipo cuando un endpoint aumenta la latencia o comienza a fallar.
- **Auditoría continua**: registrar score, predicción y métricas para análisis forense.
- **Entornos multi-cliente**: operar varios sitios o servicios en paralelo con modelos aislados.

## Ejemplo de salida de detección

```json
{
  "timestamp": "2025-11-14T00:00:00Z",
  "service": "seo-optimizer",
  "score": -0.82,
  "prediction": -1,
  "tenant": "marketing",
  "drift_alert": false,
  "metadata": {
    "http": {"response": {"status_code": 200}},
    "performance": {"duration_ms": 1680},
    "seo_context": {"generation_strategy": "LLM_RAG_v2"}
  }
}
```

## Demo mínima (`/latest-anomalies`)

```json
[
  {
    "timestamp": "2025-11-14T00:00:00Z",
    "service": "seo-optimizer",
    "score": -0.82,
    "prediction": -1,
    "tenant": "marketing",
    "duration_ms": 1680,
    "status_code": 200
  }
]
```

## Requisitos

- Python 3.11+
- Docker y Docker Compose
- Make

## Comandos clave

| Comando             | Descripción                                         |
|---------------------|-----------------------------------------------------|
| `make install`      | Crea/actualiza el entorno local e instala dependencias. |
| `make lint`         | Ejecuta validaciones estáticas con Ruff.             |
| `make test`         | Corre la suite de Pytest (ver carpeta `tests/`).     |
| `make build`        | Empaqueta el proyecto (requiere `pyproject.toml`).   |
| `make train`        | Entrena y persiste `models/model.joblib`.           |
| `make run-infra`    | Levanta Loki/Promtail/Grafana vía Docker Compose.    |
| `make stop-infra`   | Detiene y limpia los contenedores de monitoreo.      |

## Configuración

Las variables se gestionan vía `.env` o variables de entorno. Consulta `src/config.py` para los valores soportados.

| Variable                         | Descripción                                                                 | Ejemplo                               |
|----------------------------------|-----------------------------------------------------------------------------|---------------------------------------|
| `ENVIRONMENT`                    | Ambiente actual (`development`, `staging`, `production`).                   | `production`                          |
| `SECRETS_FILE`                   | Ruta a un JSON con secretos (sobrescribe valores del `.env`).              | `/run/secrets/detector.json`          |
| `LOKI_PUSH_URL`                  | Endpoint de Loki para ingestión.                                           | `https://loki.mydomain.com/loki/api/v1/push` |
| `LOKI_TRAINING_QUERY`            | Consulta LogQL usada para reentrenamiento.                                 | `{service="seo-optimizer"}`          |
| `RETRAIN_INTERVAL_HOURS`         | Horas entre reentrenamientos automáticos.                                  | `6`                                   |
| `RETRAIN_ANOMALY_THRESHOLD`      | Número de anomalías detectadas antes de forzar reentrenamiento.            | `3`                                   |
| `RETRAIN_LOOKBACK_MINUTES`       | Ventana (min) de logs históricos para entrenamiento.                       | `180`                                 |
| `TRAINING_DATASET_PATH`          | Dataset local en formato JSON usado como fallback.                         | `data/training_logs.json`             |
| `METRICS_STREAM`                 | Etiqueta del stream emitido a logs para métricas de detección.             | `anomaly_detector_metrics`            |
| `SLACK_WEBHOOK_URL`              | Webhook de Slack para alertas.                                             | `https://hooks.slack.com/...`         |
| `ANOMALY_STORE_BACKEND`          | Backend de persistencia (`memory` para DEV, `sqlite` para persistencia).   | `sqlite`                              |
| `ANOMALY_STORE_SQLITE_PATH`      | Ruta del archivo SQLite cuando el backend es `sqlite`.                     | `data/anomaly_history.db`             |
| `ANOMALY_STORE_HISTORY_LIMIT`    | Máximo de detecciones retenidas por tenant en el store.                    | `500`                                 |
| `MULTI_TENANT_ENABLED`           | Activa el modo multi-tenant.                                               | `true`                                |
| `TENANTS`                        | Lista coma-separada de tenants soportados.                                 | `default,marketing,seo`               |
| `DEFAULT_TENANT`                 | Tenant usado por defecto si no se especifica otro.                         | `default`                             |
| `TENANT_API_KEYS`                | Mapa JSON `tenant:apikey` para proteger la API (`X-API-Key`).              | `{"default":"..."}`                |

> **Tip**: crea archivos `.env.<ambiente>` (ej. `.env.production`) para sobreescribir valores específicos. Si despliegas en contenedores, apunta `SECRETS_FILE` a un volumen seguro para credenciales sensibles.

## Puesta en marcha local

1. Crear el entorno virtual (solo una vez):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Instalar dependencias: `make install`
3. Generar datos sintéticos si no existen:
   ```bash
   python scripts/generate_training_logs.py  # si se externaliza
   # o usar el snippet provisto en la documentación
   ```
4. Entrenar el modelo: `make train`
5. Ejecutar pruebas: `make test`

## Reentrenamiento automático

- El `RetrainManager` monitorea las ejecuciones desde `src/main_scheduler.py`. Si supera `RETRAIN_INTERVAL_HOURS` desde el último ajuste, o la cuenta de anomalías llega a `RETRAIN_ANOMALY_THRESHOLD`, se descargan muestras de Loki (`LOKI_TRAINING_QUERY`) y se reentrena el modelo.
- En ausencia de datos en Loki se utiliza el dataset definido en `TRAINING_DATASET_PATH`. El modelo se persiste de forma atómica en `models/model.joblib` y el estado en `models/retrain_state.json` (ignóralo en git).

### Persistencia del historial (`anomaly_store`)

- Usa `memory` por defecto (ideal para desarrollo y pruebas rápidas).
- Para ambientes productivos, fija `ANOMALY_STORE_BACKEND=sqlite` y monta un volumen para `ANOMALY_STORE_SQLITE_PATH` (tiene WAL activado para lecturas concurrentes).
- El historial mantiene como máximo `ANOMALY_STORE_HISTORY_LIMIT` detecciones por tenant. Los endpoints `/latest-anomalies` y `/metrics` consumen esta información.

### Multi-tenant

- Activa `MULTI_TENANT_ENABLED=true` y declara la lista de tenants (`TENANTS`) junto a un `DEFAULT_TENANT`.
- Opcionalmente define `TENANT_API_KEYS` para proteger la API: cada petición puede enviar `X-API-Key` y `tenant` en el query string.
- El scheduler (`src/main_scheduler.py`) recorre todos los tenants si no se especifica `--tenant`. Los artefactos (modelos, estado, datasets) se guardan por tenant utilizando los directorios configurados (`tenant_model_directory`, etc.).
- Ejemplo rápido:
  ```bash
  MULTI_TENANT_ENABLED=true \
  TENANTS="default,marketing" \
  TENANT_API_KEYS='{"marketing":"secret-token"}' \
  python -m src.main_scheduler
  ```
  Luego, para consultar las anomalías del tenant `marketing`:
  ```bash
  curl "http://localhost:8000/latest-anomalies?tenant=marketing" \
       -H "X-API-Key: secret-token"
  ```

### Métricas y visualización

- Cada detección emite un registro JSON estructurado con el stream definido en `METRICS_STREAM`. Configura Grafana para leer esa etiqueta desde Loki y visualizar scores, predicciones y duración.
- Ejemplo de panel: gráfico de líneas con `score` vs. tiempo, usando `json` → `score` como campo numérico, y panel de tabla con `prediction`, `service` y `duration_ms` para auditoría.
- Capturas sugeridas: coloca imágenes en `docs/assets/` (ej. `grafana-overview.png`, `drift-breakdown.png`) y enlázalas en este README cuando estén disponibles.
- Plantilla para assets disponible en `docs/assets/README.md`.

## Docker

El Dockerfile es multietapa y entrena el modelo durante el build.

```bash
docker build -t anomaly-detector .
docker-compose up
```

El contenedor ejecuta el scheduler principal (`src/main_scheduler.py`), que lanza detecciones cada `DETECTION_INTERVAL_SECONDS` (valor por defecto: 60).

Para habilitar reentrenamiento programado dentro del contenedor, asegúrate de montar volúmenes persistentes para `models/` y `data/` y de proveer las variables `LOKI_*` con permisos de lectura.

## Infraestructura como código (IaC)

- **Terraform**: carpeta `infra/terraform/` con módulo básico que interactúa con Kubernetes y Helm, configurando backend remoto (ajusta bucket/credenciales antes de usar).
- **Helm chart**: carpeta `infra/helm/` contiene chart minimal que despliega el servicio con probes, recursos y variables de entorno configurables.
- **Uso sugerido**:
  ```bash
  cd infra/terraform
  terraform init
  terraform apply \
    -var="kube_host=..." \
    -var="kube_ca=..." \
    -var="kube_token=..." \
    -var="env={ENVIRONMENT=\"production\",ANOMALY_STORE_BACKEND=\"postgres\"}"
  ```
  Personaliza `values.yaml`/`variables.tf` para escalar réplicas, cambiar repositorio de imagen o apuntar a backends distribuidos.

## Estructura del proyecto

```
.
├── .github/workflows/ci.yml
├── Makefile
├── README.md
├── config/
│   └── promtail-config.yml
├── data/
├── docs/
│   ├── datasets.md
│   ├── executive_summary.md
│   └── release_instructions.md
├── infra/
│   ├── helm/
│   │   ├── Chart.yaml
│   │   ├── templates/
│   │   │   ├── _helpers.tpl
│   │   │   └── deployment.yaml
│   │   └── values.yaml
│   └── terraform/
│       ├── main.tf
│       └── variables.tf
├── docker-compose.yml
├── requirements.txt
└── src/
    ├── __init__.py
    ├── alerts/
    │   ├── __init__.py
    │   └── slack_notifier.py
    ├── anomaly_detector/
    │   ├── __init__.py
    │   └── detector_core.py
    ├── config.py
    ├── ingestion/
    │   ├── __init__.py
    │   └── loki_client.py
    └── models/
        └── log_schema.py
```

## Valor entregado

- **Reducción del tiempo de reacción**: detección y notificación de anomalías SEO en minutos gracias a pipelines automatizados.
- **Observabilidad unificada**: correlación Loki + Prometheus lista para grafos, alertas y autoescalado en Kubernetes.
- **Operación resiliente**: historial persistido (SQLite WAL) con opción de extender a backends externos, más joblib atómico para modelos.
- **Preparado para SaaS**: multi-tenant con API keys por cliente, endpoints aislados y documentación operativa.
- **Mantenibilidad acelerada**: código modular, suite de pruebas completa y flujos de reentrenamiento automatizados.
- **Dashboards plug-and-play**: paneles de Grafana listos (ver carpeta `observability/grafana-dashboards/`) para monitorear métricas de detección, drift y rendimiento.
- **Infraestructura escalable** *(roadmap)*: planeado soporte IaC (Terraform + Helm) y despliegues multi-región con backends Postgres/Timescale.
- **Modelos avanzados** *(roadmap)*: integración futura de autoencoders, Prophet, LSTM y blending por tenant para escenarios especializados.

## Roadmap

- Integrar data sources adicionales (Search Console, GA4) para ampliar señales.
- Añadir selección dinámica de modelos (Isolation Forest, Prophet, LSTM) por tenant.
- Publicar charts y dashboards preconfigurados para Grafana/Looker.
- Automatizar despliegues IaC con Terraform + Helm.
- Exponer API batch para reprocesamiento histórico a demanda.

## Limitaciones actuales

- No incluye integraciones nativas con Search Console ni GA4.
- No se proveen plantillas Terraform/Kubernetes, aunque el servicio es contenedorizable.
- El retraining utiliza Isolation Forest; otros algoritmos no están integrados aún.
- El store SQLite no soporta sharding: para cargas muy altas se recomienda migrar a Postgres u otro backend durable.

## Checklist antes de publicar

- Verifica que `.env`, `.env.*` y `TENANT_API_KEYS` contengan solo valores de ejemplo antes de versionar.
- Agrega/actualiza secretos reales mediante variables de entorno o stores seguros en despliegue.
- Confirma que el archivo `LICENSE` (MIT en este repo) esté presente y referenciado.
- Valida que los badges de CI/Coverage apunten al repositorio real.
- Incluye o actualiza capturas (Grafana, dashboards) y ejemplos recientes de la API para mantener el README actual.
- Documenta datasets de entrenamiento y ejemplos de eventos en `docs/datasets.md` (placeholder incluido) y añade capturas en `docs/assets/` para mantener evidencia visual.

## Publicación y distribución

1. **Crear release GitHub**
   - Ejecuta `make build` en un entorno limpio y adjunta los artefactos `dist/anomaly_detector-1.0.0.tar.gz` y `.whl` al release.
   - Etiqueta con `v1.0.0` y referencia las entradas del [CHANGELOG](CHANGELOG.md).
2. **Publicar en GitHub Packages**
   - Crea un token personal con permisos `write:packages` y `read:packages`.
   - Configura `~/.pypirc` con un índice llamado `github` que apunte a `https://upload.github.com/OWNER` (reemplaza `OWNER` por tu usuario u organización).
   - Ejecuta `python -m twine upload --repository github dist/*`.
3. **Registrar en PyPI (opcional)**
   - Asegúrate de tener `name` único en `pyproject.toml`.
   - Usa `python -m twine upload dist/*` apuntando a PyPI o TestPyPI según sea el caso.
4. **Metadata del repositorio**
   - Añade topics sugeridos: `fastapi`, `machine-learning`, `observability`, `seo`, `anomaly-detection`, `mlops`, `python`.
   - Completa la descripción corta y website en la configuración del repositorio.
