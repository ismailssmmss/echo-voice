import React from 'react'
import ReactDOM from 'react-dom/client'
import './styles.css'

const checks = [
  ['API authentication', 'Bearer-token authentication is implemented; production secret management still required.'],
  ['Voice inference', 'Not connected. Generation requests are rejected instead of reporting false success.'],
  ['Persistent jobs', 'Not connected. Job queue, persistence, and status tracking remain unimplemented.'],
  ['Billing and moderation', 'Not connected. Do not accept payments or public user audio yet.'],
]

function App() {
  return (
    <main className="admin-shell">
      <header>
        <div>
          <h1>Echo Voice Admin</h1>
          <p>Deployment readiness · Preview environment</p>
        </div>
      </header>

      <section className="grid" aria-label="Readiness summary">
        {checks.map(([title, detail]) => (
          <article className="card" key={title}>
            <h2>{title}</h2>
            <p>{detail}</p>
          </article>
        ))}
      </section>

      <section className="card">
        <h2>Release gate</h2>
        <p>
          This dashboard does not yet query live operational metrics. User counts, job counts, GPU spend,
          and billing figures are intentionally not displayed until a verified metrics API is connected.
        </p>
        <p>
          Before public release, complete model licensing and quality evaluation, protected audio storage,
          persistent job processing, abuse reporting, rate limits, billing verification, and device/security testing.
        </p>
      </section>
    </main>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
