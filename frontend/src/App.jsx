import { useState, useEffect } from 'react'
import { Line } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'
import { Activity, Play, Server, Wifi, CheckCircle, AlertTriangle } from 'lucide-react'
import './App.css'

// Register ChartJS components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

// Chart Options for Dark Theme
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: { color: '#94a3b8' }
    },
    tooltip: {
      backgroundColor: '#1e293b',
      titleColor: '#f8fafc',
      bodyColor: '#cbd5e1',
      borderColor: '#334155',
      borderWidth: 1
    }
  },
  scales: {
    x: {
      grid: { color: '#334155' },
      ticks: { color: '#94a3b8' }
    },
    y: {
      grid: { color: '#334155' },
      ticks: { color: '#94a3b8' }
    }
  }
}

function App() {
  const [status, setStatus] = useState('Checking...')
  const [isOnline, setIsOnline] = useState(false)
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [chartData, setChartData] = useState(null)

  // Check status on mount
  useEffect(() => {
    checkBackendStatus()
  }, [])

  const checkBackendStatus = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/')
      const data = await response.json()
      setStatus(data.message)
      setIsOnline(true)
    } catch (error) {
      setStatus('Backend Offline')
      setIsOnline(false)
      console.error(error)
    }
  }

  const runAnalysis = async () => {
    setLoading(true)
    setPrediction(null)
    // Keep previous chart data if you want, or clear it: setChartData(null)
    
    try {
      const response = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
      const data = await response.json()
      setPrediction(data)

      if (data.signal && data.time) {
        setChartData({
          labels: data.time.map(t => t.toFixed(2)),
          datasets: [
            {
              label: 'Vibration Signal (g)',
              data: data.signal,
              borderColor: '#38bdf8',
              backgroundColor: 'rgba(56, 189, 248, 0.1)',
              borderWidth: 2,
              pointRadius: 0,
              tension: 0.4,
              fill: true
            }
          ]
        })
      }
    } catch (error) {
      console.error('Error fetching prediction:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="brand">
          <Activity size={28} />
          <span>VibroGuard AI</span>
        </div>
        <div className="status-indicator">
          <div className={`status-dot ${isOnline ? 'online' : 'offline'}`} />
          <span>{status}</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        
        {/* Left Column: Controls & Results */}
        <div className="control-panel">
          
          {/* System Control Card */}
          <div className="card">
            <div className="card-header">
              <Server size={20} className="text-secondary" />
              <span className="card-title">System Controls</span>
            </div>
            <button 
              className="action-btn" 
              onClick={runAnalysis} 
              disabled={loading || !isOnline}
            >
              {loading ? <Activity className="animate-spin" /> : <Play size={20} />}
              {loading ? 'Analyzing Signal...' : 'Run Diagnostics'}
            </button>
            
            <button className="action-btn secondary" onClick={checkBackendStatus}>
              <Wifi size={20} />
              Reconnect Backend
            </button>
          </div>

          {/* Results Card */}
          {prediction && (
            <div className="card">
              <div className="card-header">
                <CheckCircle size={20} className="text-secondary" />
                <span className="card-title">Analysis Result</span>
              </div>
              
              <div className="result-display">
                <div className="prediction-label">Condition</div>
                <div className={`prediction-value ${prediction.prediction === 'Normal' ? 'normal' : 'fault'}`}>
                  {prediction.prediction}
                </div>
                
                <div className="confidence-bar">
                  <div 
                    className="confidence-fill" 
                    style={{ width: `${prediction.confidence * 100}%` }} 
                  />
                </div>
                <div style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#94a3b8' }}>
                  Confidence: {(prediction.confidence * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Visualization */}
        <div className="card chart-card">
          <div className="card-header">
            <Activity size={20} className="text-secondary" />
            <span className="card-title">Real-time Signal Visualization</span>
          </div>
          <div className="chart-wrapper">
            {chartData ? (
              <Line data={chartData} options={chartOptions} />
            ) : (
              <div style={{ 
                height: '100%', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                color: '#475569' 
              }}>
                No signal data available. Run diagnostics to view.
              </div>
            )}
          </div>
        </div>

      </main>
    </div>
  )
}

export default App
