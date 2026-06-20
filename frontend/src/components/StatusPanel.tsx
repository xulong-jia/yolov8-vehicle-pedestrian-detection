export default function StatusPanel() {
  return (
    <section className="panel">
      <p className="eyebrow">Docs / Status</p>
      <h2>Minimal React Frontend</h2>
      <p>
        This frontend is an optional Vite + React + TypeScript client for the existing FastAPI
        service. Streamlit remains available as the local demo path.
      </p>
      <ul className="status-list">
        <li>Depends on FastAPI running separately.</li>
        <li>Supports optional X-API-Key when API key auth is enabled.</li>
        <li>Shows X-Request-ID response correlation.</li>
        <li>Does not include a video player.</li>
        <li>Does not include multi-user permissions or production auth.</li>
        <li>Does not include DeepSORT or a production dashboard.</li>
      </ul>
    </section>
  );
}
