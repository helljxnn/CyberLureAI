# 🧠 CyberLureAI  
**Developed by Jennifer Lascarro Sosa**

**CyberLureAI** es una plataforma inteligente de detección y análisis de ciberamenazas.  
Su objetivo es identificar múltiples tipos de ataques —como *phishing*, *malware* e *intrusiones de red*— mediante técnicas de *Machine Learning* e *Inteligencia Artificial*.

Este proyecto está diseñado para ser modular, escalable y educativo, permitiendo integrar diferentes modelos de detección en un solo ecosistema.

---

## 🚀 Objetivos Generales

1. **Detectar y clasificar** diferentes tipos de ciberamenazas (phishing, malware, intrusiones, DNS malicioso, etc.).
2. **Desarrollar modelos de IA y ML** capaces de analizar diversos tipos de datos (URLs, tráfico de red, binarios, correos, etc.).
3. **Construir una API y una interfaz web** que centralicen la predicción y visualización de resultados.
4. **Escalar el proyecto** hacia un sistema integral de detección y respuesta ante amenazas (SOC simulado).
5. **Fomentar la investigación** y el aprendizaje en ciberseguridad aplicada a la inteligencia artificial.

---

## 🏗️ Estructura del Proyecto

CyberLureAI/
├── docs/ # Documentación, diagramas, manuales y notas
├── data/ # Archivos de datos (datasets públicos)
│ ├── malware_classification/
│ ├── malware_behavior/
│ ├── phishing_urls/
│ ├── email_spam/
│ └── readme_datasets.txt
├── ingestion/ # Scripts para obtener datasets (Kaggle, URLs, APIs)
├── preprocessing/ # Limpieza, normalización y extracción de características
│ ├── phishing/
│ ├── intrusion/
│ └── malware/
├── models/ # Modelos de IA por tipo de amenaza
│ ├── phishing/
│ ├── intrusion/
│ └── malware/
├── backend/ # API (Flask o FastAPI)
│ └── api/
├── frontend/ # Interfaz visual (React o Bootstrap)
├── experiments/ # Notebooks, pruebas y reportes
├── tests/ # Pruebas unitarias o de integración
├── .gitignore
└── README.md

---

## 🧩 Tecnologías Clave

- **Lenguaje principal:** Python 3.10+
- **Bibliotecas:**  
  `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `fastapi`, `joblib`, `requests`
- **Herramientas de IA:** PyTorch o TensorFlow (en etapas avanzadas)
- **Control de versiones:** Git + GitHub  
- **Versionado de datos:** DVC o Git LFS (opcional)
- **Frontend:** React o HTML/CSS/Bootstrap

---

## 📚 Datasets Oficiales de CyberLureAI

| Tipo de amenaza | Dataset | Fuente | Sprint |
|-----------------|----------|--------|--------|
| **Malware (Principal)** | [Classification of Malwares](https://www.kaggle.com/datasets/saurabhshahane/classification-of-malwares) | Kaggle | 1 y 2 |
| **Malware (Comportamiento)** | [Malware Behavior Analysis](https://www.kaggle.com/datasets/saurabhshahane/malware-behavior-analysis) | Kaggle | 2 y 3 |
| **Phishing (URLs maliciosas)** | [Phishing URLs Dataset](https://www.kaggle.com/datasets/shashwatwork/phishing-dataset-for-machine-learning) | Kaggle | 3 y 4 |
| **Spam / Correos maliciosos** | [SMS Spam Collection Dataset](https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset) | Kaggle | 4 |
| **Intrusión de red (futuro)** | [UNSW-NB15](https://research.unsw.edu.au/projects/unsw-nb15-dataset) | UNSW | Fase avanzada |
| **DNS malicioso (futuro)** | [CTU-Malware DNS Dataset](https://www.stratosphereips.org/datasets-malware) | Stratosphere IPS | Fase avanzada |

---
⚠️ Nota Legal y Ética

CyberLureAI es un proyecto educativo. No debe usarse con fines maliciosos.
Todos los datos provienen de fuentes públicas y autorizadas para investigación académica.
El propósito del proyecto es fomentar el aprendizaje y la investigación ética en ciberseguridad.