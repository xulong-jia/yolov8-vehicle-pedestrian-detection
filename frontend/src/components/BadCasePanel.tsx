import { FormEvent, useState } from "react";
import { apiRequest } from "../api";
import type { ApiClientConfig, BadCasePayload, BadCaseRecord } from "../types";

interface BadCasePanelProps {
  config: ApiClientConfig;
  onRequestId: (requestId: string) => void;
}

const initialBadCase: BadCasePayload = {
  module: "detector",
  case_type: "false_positive",
  video_id: "",
  image_name: "",
  frame_index: "",
  expected_result: "",
  actual_result: "",
  root_cause: "",
  tags: "",
  reviewer_note: ""
};

export default function BadCasePanel({ config, onRequestId }: BadCasePanelProps) {
  const [form, setForm] = useState<BadCasePayload>(initialBadCase);
  const [records, setRecords] = useState<BadCaseRecord[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submitBadCase(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const result = await apiRequest<BadCaseRecord>(config, "/api/bad-cases", {
        method: "POST",
        body: JSON.stringify(form)
      });
      setRecords((current) => [result.data, ...current]);
      onRequestId(result.requestId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create Bad Case");
    } finally {
      setLoading(false);
    }
  }

  async function loadBadCases() {
    setLoading(true);
    setError("");
    try {
      const result = await apiRequest<BadCaseRecord[]>(config, "/api/bad-cases");
      setRecords(result.data);
      onRequestId(result.requestId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load Bad Cases");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel panel-wide">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Review</p>
          <h2>Bad Cases</h2>
        </div>
        <button type="button" onClick={loadBadCases} disabled={loading}>
          Load list
        </button>
      </div>
      <form className="form-grid" onSubmit={submitBadCase}>
        {Object.entries(form).map(([field, value]) => (
          <label key={field}>
            {field}
            <input
              value={value}
              onChange={(event) => setForm({ ...form, [field]: event.target.value })}
            />
          </label>
        ))}
        <div className="form-actions">
          <button type="submit" disabled={loading}>
            {loading ? "Saving" : "Create Bad Case"}
          </button>
        </div>
      </form>
      {error ? <p className="error-text">{error}</p> : null}
      {records.length ? (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>case_id</th>
                <th>module</th>
                <th>case_type</th>
                <th>video_id</th>
                <th>expected</th>
                <th>actual</th>
              </tr>
            </thead>
            <tbody>
              {records.map((record) => (
                <tr key={record.case_id}>
                  <td>{record.case_id}</td>
                  <td>{record.module}</td>
                  <td>{record.case_type}</td>
                  <td>{record.video_id}</td>
                  <td>{record.expected_result}</td>
                  <td>{record.actual_result}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="muted">No Bad Cases loaded.</p>
      )}
    </section>
  );
}
