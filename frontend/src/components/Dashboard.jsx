import React, { useEffect, useState } from 'react';
import { fetchSystemMetrics } from '../services/apiClient';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const COLORS = ['#14b8a6', '#f59e0b', '#ec4899'];

export default function Dashboard({ apiBaseUrl }) {
  const [metrics, setMetrics] = useState({ sample_type: [], class_metrics: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadMetrics() {
      try {
        setLoading(true);
        const data = await fetchSystemMetrics(apiBaseUrl);
        setMetrics(data);
        setError(null);
      } catch (err) {
        setError('No se pudieron cargar las métricas del modelo.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadMetrics();
  }, [apiBaseUrl]);

  if (loading) {
    return <div className="card loading-state">Cargando métricas del modelo...</div>;
  }

  if (error) {
    return <div className="card result-error">{error}</div>;
  }

  // Preparar datos para los gráficos
  const separateTypeMetrics = metrics.sample_type.filter(m => m.strategy === 'separate_by_type');
  
  const accuracyData = separateTypeMetrics.map(m => ({
    name: m.sample_type.charAt(0).toUpperCase() + m.sample_type.slice(1),
    Heurístico: parseFloat(m.heuristic_accuracy) * 100,
    ModeloML: parseFloat(m.baseline_accuracy) * 100
  }));

  const classDataRaw = metrics.class_metrics.filter(m => m.strategy === 'separate_by_type' && parseFloat(m.support) > 0);
  const supportData = classDataRaw.map(m => ({
    name: m.label,
    value: parseInt(m.support, 10)
  }));

  const f1Data = classDataRaw.map(m => ({
    name: m.label,
    F1_Score: parseFloat(m.f1_score) * 100,
    Precisión: parseFloat(m.precision) * 100,
    Recall: parseFloat(m.recall) * 100
  }));

  return (
    <div className="dashboard-container" style={{ display: 'grid', gap: '24px' }}>
      <div className="card">
        <div className="card-header">
          <p className="section-kicker">Rendimiento</p>
          <h2>Heurístico vs Modelo ML (Accuracy %)</h2>
        </div>
        <div style={{ width: '100%', height: 300 }}>
          <ResponsiveContainer>
            <BarChart data={accuracyData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="name" stroke="#a1a1aa" />
              <YAxis stroke="#a1a1aa" domain={[0, 100]} />
              <Tooltip 
                contentStyle={{ backgroundColor: 'rgba(24, 24, 27, 0.9)', borderColor: 'rgba(255,255,255,0.1)' }} 
                itemStyle={{ color: '#fff' }} 
              />
              <Legend />
              <Bar dataKey="Heurístico" fill="#a1a1aa" radius={[4, 4, 0, 0]} />
              <Bar dataKey="ModeloML" fill="#14b8a6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
        <div className="card">
          <div className="card-header">
            <p className="section-kicker">Distribución</p>
            <h2>Muestras de Entrenamiento</h2>
          </div>
          <div style={{ width: '100%', height: 250 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={supportData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {supportData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(24, 24, 27, 0.9)', borderColor: 'rgba(255,255,255,0.1)' }} 
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <p className="section-kicker">Métricas Detalladas</p>
            <h2>F1 Score, Precisión y Recall (%)</h2>
          </div>
          <div style={{ width: '100%', height: 250 }}>
            <ResponsiveContainer>
              <BarChart data={f1Data} margin={{ top: 20, right: 10, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="name" stroke="#a1a1aa" />
                <YAxis stroke="#a1a1aa" domain={[0, 100]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(24, 24, 27, 0.9)', borderColor: 'rgba(255,255,255,0.1)' }} 
                />
                <Legend />
                <Bar dataKey="F1_Score" fill="#ec4899" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Precisión" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Recall" fill="#14b8a6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
