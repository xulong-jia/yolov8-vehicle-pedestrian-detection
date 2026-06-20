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
      setError(err instanceof Error ? err.message : "无法记录问题样例");
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
      setError(err instanceof Error ? err.message : "无法加载问题样例列表");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel panel-wide">
      <div className="panel-header">
        <div>
          <p className="eyebrow">复核</p>
          <h2>问题样例记录（高级/复核用）</h2>
        </div>
        <button type="button" onClick={loadBadCases} disabled={loading}>
          加载列表
        </button>
      </div>
      <form className="form-grid" onSubmit={submitBadCase}>
        {Object.entries(form).map(([field, value]) => (
          <label key={field}>
            {badCaseFieldLabels[field] || field} <span className="field-key">{field}</span>
            <input
              value={value}
              onChange={(event) => setForm({ ...form, [field]: event.target.value })}
            />
          </label>
        ))}
        <div className="form-actions">
          <button type="submit" disabled={loading}>
            {loading ? "保存中" : "记录问题样例"}
          </button>
        </div>
      </form>
      {error ? <p className="error-text">{error}</p> : null}
      {records.length ? (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>样例编号 case_id</th>
                <th>模块 module</th>
                <th>问题类型 case_type</th>
                <th>视频ID video_id</th>
                <th>期望 expected</th>
                <th>实际 actual</th>
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
        <p className="muted">暂无问题样例</p>
      )}
    </section>
  );
}

const badCaseFieldLabels: Record<string, string> = {
  module: "所属模块",
  case_type: "问题类型",
  video_id: "视频ID",
  image_name: "图片名称",
  frame_index: "帧编号",
  expected_result: "期望结果",
  actual_result: "实际结果",
  root_cause: "原因分析",
  tags: "标签",
  reviewer_note: "复核备注"
};
