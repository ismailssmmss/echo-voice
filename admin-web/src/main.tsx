import React from 'react'
import ReactDOM from 'react-dom/client'
import './styles.css'

function App() {
  return (
    <main className="admin-shell">
      <header>
        <h1>Echo Voice Admin</h1>
        <button>New report</button>
      </header>

      <section className="grid">
        <div className="card">
          <h2>Users</h2>
          <p>12,345</p>
        </div>
        <div className="card">
          <h2>Active Jobs</h2>
          <p>184</p>
        </div>
        <div className="card">
          <h2>Cost / GPU</h2>
          <p>$2,431</p>
        </div>
      </section>
    </main>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
