# 🧠 CyberLureAI Developed by Jennifer Lascarro Sosa

**CyberLureAI** es una plataforma inteligente de detección y análisis de ciberamenazas. Su objetivo es identificar múltiples tipos de ataques —como phishing, malware e intrusiones de red— mediante técnicas de *Machine Learning* e *Inteligencia Artificial*.

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
│ ├── phishing/
│ ├── intrusion/
│ ├── malware/
│ ├── email/
│ └── dns/
├── ingestion/ # Scripts para obtener datasets (Kaggle, URLs, APIs)
├── preprocessing/ # Scripts de limpieza y extracción de características
│ ├── phishing/
│ ├── intrusion/
│ └── malware/
├── models/ # Modelos de IA por tipo de amenaza
│ ├── phishing/
│ ├── intrusion/
│ └── malware/
├── backend/ # API (Flask o FastAPI)
│ └── api/
├── frontend/ # Interfaz visual (HTML, React o similar)
├── experiments/ # Notebooks, reportes y resultados
├── tests/ # Pruebas unitarias o de integración
├── .gitignore
└── README.md

---

## 🧩 Tecnologías Clave

- **Lenguaje principal:** Python 3.10+
- **Bibliotecas:**  
  `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `fastapi`, `joblib`, `requests`
- **Herramientas de IA:** PyTorch o TensorFlow (para etapas avanzadas)
- **Control de versiones:** Git + GitHub  
- **Versionado de datos:** DVC o Git LFS (opcional)
- **Frontend:** React o HTML/CSS/Bootstrap

---

## 📚 Datasets Iniciales

| Tipo de amenaza | Dataset | Fuente |
|-----------------|----------------------|--------|
| Phishing | [Phishing Websites Dataset](https://www.kaggle.com/datasets/saurabhshahane/classification-of-malwares) | Kaggle |
| Intrusión de red | [CIC-IDS 2018](https://www.unb.ca/cic/datasets/ids-2018.html) o [UNSW-NB15](https://research.unsw.edu.au/projects/unsw-nb15-dataset) | UNB / UNSW |
| Malware | [EMBER Dataset](https://www.kaggle.com/datasets/hollylee/malware-analysis-dataset) | Kaggle |
| DNS malicioso | [CTU-Malware DNS Dataset](https://www.stratosphereips.org/datasets-malware) | Stratosphere IPS |
| Emails / Spam | [Enron Email Dataset](https://www.cs.cmu.edu/~enron/) | CMU |

---

## 🧪 Ejecución básica

1. Clona el repositorio  
   ```bash
   git clone https://github.com/tuusuario/CyberLureAI.git
   cd CyberLureAI


## CyberLureAI es un proyecto educativo. No debe usarse con fines maliciosos.
Todos los datos utilizados provienen de fuentes públicas y autorizadas para investigación académica.