import React, { useState, useMemo } from 'react';
import './App.css'; 

// Import Chart.js components
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

// Base URL for our backend
const API_URL = 'http://127.0.0.1:8000';

function App() {
  // State for the form controls
  const [reportType, setReportType] = useState('activity');
  const [format, setFormat] = useState('json');

  // State for the report data
  const [data, setData] = useState(null); 
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const handleReportTypeChange = (newType) => {
    setReportType(newType);
    setData(null); // <-- This is the fix
    setError(null); // Also clear any old errors
  };
  // --- Function to Fetch Report Data ---
  const fetchReport = async () => {
    setIsLoading(true);
    setError(null);
    setData(null);

    try {
      const response = await fetch(
        `${API_URL}/api/export?type=${reportType}&format=json`
      );
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const jsonData = await response.json();
      setData(jsonData);
    } catch (e) {
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Add this new handler function inside the App component

  // --- Function to Handle the Final Download ---
  const downloadReport = async () => {
    // If user wants JSON, use the data we already have
    if (format === 'json') {
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json',
      });
      triggerDownload(blob, `${reportType}.json`);
    } 
    // If user wants CSV, fetch it from the backend
    else if (format === 'csv') {
      try {
        const response = await fetch(
          `${API_URL}/api/export?type=${reportType}&format=csv`
        );
        const blob = await response.blob();
        triggerDownload(blob, `${reportType}.csv`);
      } catch (e) {
        setError(e.message);
      }
    }
  };

  // Helper function to trigger a file download
  const triggerDownload = (blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="App">
      <header>
        <h1>Gym Report Exporter</h1>
      </header>
      
{/* --- Controls --- */}
<div className="controls">
  {/* Update this onChange handler */}
  <select value={reportType} onChange={(e) => handleReportTypeChange(e.target.value)}>
    <option value="activity">Member Activity Report</option>
    <option value="popular-exercises">Popular Exercises Report</option>
  </select>

  <button onClick={fetchReport} disabled={isLoading}>
    {isLoading ? 'Loading...' : 'Visualize Report'}
  </button>
</div>

      
      {/* --- Visuals Container --- */}
      {data && (
        <div className="visuals-container">
          <ReportChart data={data} reportType={reportType} />
          <ReportTable data={data} />
        </div>
      )}

      {/* --- Download Area --- */}
      {data && (
        <div className="download-area">
          <h3>Download Visualized Report</h3>
          <select value={format} onChange={(e) => setFormat(e.target.value)}>
            <option value="json">as JSON</option>
            <option value="csv">as CSV</option>
          </select>
          <button onClick={downloadReport}>Download</button>
        </div>
      )}

      {error && <div className="error">Error: {error}</div>}
    </div>
  );
}

// --- Helper function to generate random colors for the chart ---
const getRandomColor = () => {
  const h = Math.floor(Math.random() * 360);
  return `hsla(${h}, 70%, 60%, 0.8)`;
};

// --- Updated Chart Component ---
const ReportChart = ({ data, reportType }) => {

  const { chartData, chartOptions } = useMemo(() => {
    if (!data || data.length === 0) {
      return { chartData: null, chartOptions: {} };
    }

    let chartData = null; // Default to null
    let chartOptions = {};

    // --- LOGIC FOR STACKED BAR CHART (Member Activity) ---
    if (reportType === 'activity') {
      // 1. Get unique X-axis labels (Club Names)
      const labels = [...new Set(data.map(item => item.club_name))];
      
      // 2. Get unique stack segments (Months)
      const months = [...new Set(data.map(item => item.month_year))].sort();

      // 3. Generate a color for each month
      const monthColors = months.reduce((acc, month) => {
        acc[month] = getRandomColor();
        return acc;
      }, {});
      
      // 4. Build the datasets (one dataset per month)
      const datasets = months.map(month => {
        // For each month, create an array of check-in data for each club
        const monthData = labels.map(clubName => {
          const entry = data.find(
            item => item.club_name === clubName && item.month_year === month
          );
          return entry ? entry.total_checkins : 0; // Return 0 if club had no checkins that month
        });
        
        return {
          label: month,
          data: monthData,
          backgroundColor: monthColors[month],
        };
      });

      chartData = { labels, datasets };
      chartOptions = {
        plugins: {
          title: { display: true, text: 'Total Member Check-ins by Club and Month' },
        },
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { stacked: true }, 
          y: { stacked: true },
        },
      };

    // --- POPULAR EXERCISES LOGIC HAS BEEN REMOVED ---
    
    } 

    return { chartData, chartOptions };

  }, [data, reportType]); 

  if (!chartData) {
    return null; // Don't render a chart if chartData is null
  }

  return (
    <div className="chart-container">
      <Bar options={chartOptions} data={chartData} />
    </div>
  );
};


// --- Dynamic Table Component ---
const ReportTable = ({ data }) => {
  if (!data || data.length === 0) {
    return <p>No data to display.</p>;
  }
  const headers = Object.keys(data[0]);

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            {headers.map((header) => (
              <th key={header}>{header.replace(/_/g, ' ')}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index}>
              {headers.map((header) => (
                <td key={header}>{String(row[header])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default App;