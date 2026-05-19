# 🛡️ CyberLureAI — Análisis de Estado y Hoja de Ruta

> Análisis realizado el 17 de mayo de 2026 sobre el código fuente real del proyecto.
> Stack: **Python 3.10+ · FastAPI · scikit-learn · React + Vite · joblib**

---

## 1. Diagnóstico Rápido

### ✅ Lo que está bien construido

| Área | Estado |
|------|--------|
| Arquitectura backend | Limpia. FastAPI con routers separados, `core/settings.py` con `lru_cache`, manejo de errores centralizado |
| Feature extraction | Modular y desacoplado en `services/features/` (url_features, message_features, common) |
| Pipeline ML | Sólido: `LogisticRegression + StandardScaler` vía pipeline, `StratifiedKFold`, métricas F1/precision/recall |
| Calibración | Sistema completo: CSV de ejemplos etiquetados → evaluación → reporte de FP/FN |
| Tests | 5 archivos de test cubren API, servicios de análisis, calibración y ejemplos etiquetados |
| Contrato API | Schemas Pydantic bien definidos, `experimental_model` como campo opcional sin romper el contrato principal |
| Frontend | React+Vite funcional con historial local (`localStorage`), 3 flujos de análisis, componentes separados |
| CORS | Bien configurado: `allow_origins=["*"]` solo en debug, `frontend_url` en producción |

### 🔴 Focos Rojos / Advertencias Arquitectónicas

#### CRÍTICO: Overfitting en el dataset de calibración
```
Heuristic accuracy: 100.0%
Baseline CV accuracy: 100.0%
```
**Un 100% exacto en CV no es señal de fortaleza — es señal de que el dataset está "curado" alrededor de las propias reglas del heurístico.** Las 246 muestras están diseñadas para pasar el heurístico, por lo que el modelo aprende las mismas reglas. Esto no generalizará a ejemplos del mundo real.

#### CRÍTICO: Carga lazy del modelo en la primera solicitud HTTP
```python
# experimental_baseline.py L59-61
@lru_cache(maxsize=1)
def _load_separate_baseline_bundle() -> dict[str, object]:
    return fit_separate_baseline_classifiers()
```
El primer request al endpoint `/analyze/url` o `/analyze/message` **entrena el modelo en tiempo de request**. Esto puede causar un timeout o una respuesta de 5-10 segundos para el primer usuario. En producción esto es inaceptable.

#### ADVERTENCIA: Dataset pequeño para el alcance del objetivo
- 246 muestras para un clasificador de 3 clases (likely_safe / review / suspicious) es muy limitado
- No hay datos reales de phishing URLs (PhishTank, OpenPhish, etc.) integrados todavía
- Los datos de malware (`malware_classifier.joblib`, 3.5 MB) parecen estar entrenados fuera del pipeline de calibración, sin trazabilidad clara

#### ADVERTENCIA: `openai_api_key` definida pero sin uso
```python
# settings.py L58
openai_api_key=getenv("OPENAI_API_KEY", ""),
```
Hay un campo `openai_api_key` en Settings que no se usa en ningún servicio activo. Esto sugiere una funcionalidad planeada pero sin implementar, lo que puede generar confusión o configuraciones incorrectas.

#### ADVERTENCIA: El router de malware tiene lógica de negocio interna
```python
# analysis.py L56-101
risk_score = int(verdict.confidence * 100) if verdict.is_malware else ...
```
La conversión de confianza → risk_score, la generación de signals y la lógica de verdicts para malware está **embebida directamente en el router**, a diferencia de URL y mensajes que tienen su propio `_analyzer.py`. Esto rompe la separación de responsabilidades y dificulta testearlo en aislamiento.

#### INFO: `useHistoryEntry` no maneja Malware
```javascript
// App.jsx L76-83
function useHistoryEntry(item) {
    if (item.kind === "URL") { setUrlInput(item.input); return; }
    setMessageInput(item.input);  // Mensaje o Malware → siempre message input
}
```
El historial de análisis de Malware se guarda pero el botón "usar entrada" rellena el campo de mensaje en lugar del de malware.

---

## 2. Plan de Acción por Prioridades

---

### 🔴 FASE 1 — Crítico/Bloqueante (antes de cualquier demo o MVP público)

#### 1.1 — Mover la lógica de malware del router a un servicio propio
**Archivo objetivo:** `backend/app/services/malware_response_builder.py` (nuevo)
- Extraer la conversión `verdict → risk_score / risk_level / signals` del router `analysis.py`
- El router solo debe llamar al servicio y devolver el resultado
- Esto permite escribir tests unitarios del análisis sin levantar la API

**Estimado:** 1-2h · Riesgo bajo

#### 1.2 — Pre-cargar el modelo experimental al arrancar el servidor (startup event)
```python
# main.py — agregar:
from contextlib import asynccontextmanager
from backend.app.services.experimental_baseline import _load_separate_baseline_bundle

@asynccontextmanager
async def lifespan(app: FastAPI):
    _load_separate_baseline_bundle()  # warm-up en startup
    yield

app = FastAPI(..., lifespan=lifespan)
```
**Sin este fix, el primer request tardará varios segundos entrenando el modelo.**

**Estimado:** 30min · Riesgo muy bajo

#### 1.3 — Corregir `useHistoryEntry` en el frontend para Malware
```javascript
function useHistoryEntry(item) {
    if (item.kind === "URL") { setUrlInput(item.input); return; }
    if (item.kind === "Malware") { setMalwareInput(item.input); return; }
    setMessageInput(item.input);
}
```
**Estimado:** 15min · Riesgo ninguno

#### 1.4 — Agregar un test de integración para el endpoint `/analyze/malware`
El archivo `test_api.py` probablemente no cubre el endpoint de malware o lo hace de forma incompleta. Verificar y ampliar.

---

### 🟡 FASE 2 — Importante (necesario para un MVP robusto)

#### 2.1 — Expandir el dataset de calibración con ejemplos adversariales reales
**El problema:** 100% de accuracy en CV significa que el modelo no tiene capacidad de generalización real.
**Acción:**
- Integrar al menos 50-100 URLs de PhishTank (público y gratuito) como ejemplos `suspicious`
- Agregar URLs de dominios legítimos conocidos como ejemplos `likely_safe`
- Incluir casos borde: URLs con HTTPS pero dominio sospechoso, acortadores de URL, etc.
- Agregar mensajes SMS spam del dataset "UCI SMS Spam Collection" (público)

**Objetivo:** Bajar el accuracy de calibración a 85-95% con datos reales → eso sí significa que el modelo generaliza.

**=== COMPLETADO May 18, 2026 ===**
- Integrados 1,950 ejemplos reales: 950 URLs (Kaggle taruntiwarihp + OpenPhish), 1,000 SMS (UCI)
- Heurístico real-world accuracy: 51% URLs, 52% mensajes
- Baseline ML (LogisticRegression CV) accuracy: 73% (+22pp sobre heurístico)
- Añadidos 14 nuevos keywords de phishing, 12 TLDs sospechosos, 8 acortadores nuevos
- Nueva señal `suspicious_script_file` (+15 puntos para .php/.asp con keywords)
- Whitelist de TLDs confiables (.edu, .gov, .ac.uk) para subdominios
- `insecure_http` score subido de 10→15
- Corregidos falsos positivos en mensajes: removidos "free", "now", "today", "selected" de términos demasiado amplios
- 283 tests pasan (hand-crafted + baseline)
- Script `scripts/convert_external_data.py` creado para ingesta de datasets futuros
- Datasets en `data/external/` y `data/phishing_urls/`, `data/sms_spam/`
- Modelo baseline re-entrenado guardado en `models/baseline_model_external.joblib`

**Limitaciones documentadas:**
- URLs phishing sin keywords visibles en la URL → indetectables sin content analysis o reputación de dominio
- Spam conversacional sin frases scam obvias → requiere NLP/ML
- Phishing en plataformas legítimas (Vercel, GitHub Pages, Google Forms) → heurístico ciego
- Solo 2 clases en datos reales (likely_safe/suspicious), clase "review" vacía → necesita más datos borderline

#### 2.2 — Separar `malware_classifier.joblib` con documentación de trazabilidad
El modelo `.joblib` de 3.5 MB en `/models` fue generado fuera del pipeline visible. Necesitas:
- Un notebook o script que documente cómo fue entrenado, con qué dataset y qué métricas
- Un archivo `models/malware_features.json` (ya existe) ligado explícitamente al entrenamiento
- Versionar el modelo con un nombre que incluya fecha o hash del dataset

#### 2.3 — Añadir rate limiting al backend
Para un MVP público, los endpoints de análisis son abusables. FastAPI con `slowapi` (integración con `limits`) permite agregar rate limiting por IP en ~30 minutos.
```python
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)
# @limiter.limit("10/minute") en cada endpoint
```

#### 2.4 — Variables de entorno para producción bien documentadas
El `.env.example` existe pero el `DEBUG=True` por defecto en `settings.py` es un riesgo. Necesitas:
- Un `.env.production.example` con valores seguros
- Documentar claramente que `DEBUG=False` desactiva el CORS abierto
- Asegurarte de que `FRONTEND_URL` esté configurado antes de cualquier deploy

#### 2.5 — Pipeline de build del frontend para producción
```bash
# Verificar que el dist de Vite sirve correctamente desde el backend o un CDN
cd frontend && npm run build
```
Actualmente `frontend/dist/` existe pero no hay evidencia de que FastAPI lo sirva como static files. Necesitas decidir: ¿servidor separado (Nginx/Vercel) o monolito (FastAPI sirve el `dist/`)?

---

### 🟢 FASE 3 — Deseable / Optimizaciones (post-MVP)

#### 3.1 — Reemplazar LogisticRegression por un modelo más expresivo
Una vez que tengas un dataset real de >500 ejemplos balanceados, considera:
- `RandomForestClassifier` o `GradientBoostingClassifier` para capturar interacciones no lineales entre señales
- Calibración de probabilidades con `CalibratedClassifierCV` si la confianza del modelo se muestra al usuario

#### 3.2 — Sistema de feedback del usuario ("¿Este análisis fue útil?")
Para mejorar el modelo de forma continua:
- Botones de feedback en `ResultPanel.jsx` ("Este resultado fue correcto / incorrecto")
- Endpoint `POST /feedback` que guarda el ejemplo etiquetado por el usuario
- Estos se acumulan para re-entrenar con `python -m backend.app.services.baseline_classifier`

#### 3.3 — Integración con APIs de reputación externas
- **VirusTotal API** (gratuito con límites): enriquecer el análisis de URLs
- **Google Safe Browsing API** (gratuito): verificar URLs contra lista de phishing conocido
- Integrar como señales adicionales sin reemplazar el análisis heurístico local

#### 3.4 — Dashboard de métricas de calibración en el frontend
Un panel de "Salud del modelo" que muestre:
- Accuracy actual, F1 por clase
- Número de ejemplos en el dataset
- Fecha del último entrenamiento

#### 3.5 — Análisis de archivos reales (upload)
Actualmente el análisis de malware requiere pegar JSON con features PE. El siguiente paso natural es aceptar un archivo `.exe` y extraer las features automáticamente con `pefile` (biblioteca Python).

---

## 3. Cuellos de Botella Técnicos a Prever

### ⚡ Rendimiento

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Primera carga del modelo experimental (~3-8s) | Alto | **Implementar startup warm-up (Fase 1.2)** |
| `cross_val_predict` con datasets grandes (>10K ejemplos) | Medio | Cachear el modelo entrenado; solo re-entrenar al actualizar el dataset |
| `malware_classifier.joblib` (3.5 MB) cargado en cada proceso worker | Medio | Usar `gunicorn` con workers compartidos o un cache de modelos |
| `localStorage` history sin límite real en el cliente | Bajo | `HISTORY_LIMIT` ya existe, verificar que se aplica correctamente |

### 🏗️ Arquitectura

| Riesgo | Descripción |
|--------|-------------|
| **Dataset-model coupling** | El modelo experimental se re-entrena desde los CSVs en cada startup. Si el CSV cambia sin control de versiones, el comportamiento del API cambia silenciosamente |
| **Feature drift** | Si agregas nuevas señales al heurístico (url_features.py), el modelo re-entrenado tendrá más features. Los modelos `.joblib` guardados en `/models` quedarán incompatibles si intentas cargarlos |
| **Single responsibility en router** | La lógica de negocio en `analysis.py` para malware hace difícil agregar tests unitarios sin levantar el servidor completo |
| **Sin autenticación** | Para un MVP público, cualquier persona puede hacer llamadas ilimitadas. Considerar al menos una API key simple |

### 🤖 ML / Datos

| Riesgo | Descripción |
|--------|-------------|
| **Clase "review" subrepresentada** | En datos reales, los casos borderline son los más difíciles. Si el dataset de calibración tiene pocos ejemplos de `review`, el modelo los clasificará como `suspicious` o `likely_safe` |
| **Sesgo por diseño** | Las 246 muestras actuales fueron diseñadas para validar el heurístico, no para entrenar un modelo generalizable. El 100% de accuracy lo confirma |
| **Explicabilidad vs. precisión** | LogisticRegression es interpretable pero menos preciso. RandomForest es más preciso pero los usuarios no pueden saber "por qué" fue clasificado así. Mantener el heurístico explainable como capa primaria es una buena decisión |

---

## Resumen Ejecutivo

```
ESTADO ACTUAL: Sprint 2 completado, Fase 2.1 (datos reales) COMPLETADA May 18 2026
BLOQUEANTES:   3 resueltos (model warm-up, lógica malware en router, history bug)
SIGUIENTE MVP: Fase 2.3-2.5: rate limiting (ya hecho), build producción, API key
CALIBRACIÓN:   Hand-crafted: 100% → Real-world: 51% heurístico / 73% baseline ML
TIMELINE:      ~1 semana para MVP demo-able con modelo re-entrenado
```

El proyecto tiene una arquitectura bien pensada y código limpio. Los riesgos principales no son técnicos sino de **calidad del dato** y **preparación para producción**. La prioridad inmediata es la Fase 1 (3-4h de trabajo) y luego expandir el dataset antes de invertir más en el modelo.
