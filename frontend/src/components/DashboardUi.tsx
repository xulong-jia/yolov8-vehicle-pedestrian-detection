import type { ReactNode } from "react";

export interface NavItem {
  id: string;
  label: string;
  description: string;
}

interface SidebarProps {
  items: NavItem[];
  activeId: string;
  onSelect: (id: string) => void;
}

export function Sidebar({ items, activeId, onSelect }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="brand-block">
        <span className="brand-mark">YO</span>
        <div>
          <strong>YOLOV8</strong>
          <p>车辆与行人检测系统</p>
        </div>
      </div>
      <nav className="nav-list" aria-label="页面导航">
        {items.map((item) => (
          <button
            key={item.id}
            type="button"
            className={item.id === activeId ? "nav-item nav-item-active" : "nav-item"}
            aria-current={item.id === activeId ? "page" : undefined}
            aria-label={`${item.label}：${item.description}`}
            onClick={() => onSelect(item.id)}
          >
            <span>{item.label}</span>
            <small>{item.description}</small>
          </button>
        ))}
      </nav>
    </aside>
  );
}

interface TextFieldProps {
  label: string;
  fieldKey?: string;
  showFieldKey?: boolean;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: string;
  step?: string;
}

export function TextField({
  label,
  fieldKey,
  showFieldKey = false,
  value,
  onChange,
  placeholder,
  type = "text",
  step
}: TextFieldProps) {
  return (
    <label>
      {label} {showFieldKey && fieldKey ? <span className="field-key">{fieldKey}</span> : null}
      <input
        type={type}
        step={step}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        title={fieldKey}
      />
    </label>
  );
}

interface PageHeaderProps {
  title: string;
  description: string;
}

export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <header className="page-header">
      <div>
        <p className="eyebrow">YOLOv8 本地演示</p>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
    </header>
  );
}

interface PanelProps {
  title?: string;
  eyebrow?: string;
  actions?: ReactNode;
  children: ReactNode;
  wide?: boolean;
  className?: string;
}

export function Panel({ title, eyebrow, actions, children, wide = false, className = "" }: PanelProps) {
  return (
    <section className={`panel${wide ? " panel-wide" : ""}${className ? ` ${className}` : ""}`}>
      {(title || eyebrow || actions) ? (
        <div className="panel-header">
          <div>
            {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
            {title ? <h2>{title}</h2> : null}
          </div>
          {actions}
        </div>
      ) : null}
      {children}
    </section>
  );
}

interface StatCardProps {
  label: string;
  value: string | number;
  hint: string;
  tone?: "blue" | "cyan" | "green" | "orange";
}

export function StatCard({ label, value, hint, tone = "blue" }: StatCardProps) {
  return (
    <article className={`stat-card stat-${tone}`}>
      <span className="stat-accent" />
      <p>{label}</p>
      <strong>{value}</strong>
      <small>{hint}</small>
    </article>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const normalized = status.toLowerCase();
  const tone =
    normalized.includes("fail") || normalized.includes("error") || normalized.includes("失败") || normalized.includes("错误")
      ? "failed"
      : normalized.includes("running") || normalized.includes("processing") || normalized.includes("info") || normalized.includes("运行中") || normalized.includes("处理中") || normalized.includes("说明")
        ? "running"
        : normalized.includes("complete") || normalized.includes("ok") || normalized.includes("success") || normalized.includes("已完成") || normalized.includes("正常")
          ? "completed"
          : normalized.includes("upload") || normalized.includes("已上传")
            ? "uploaded"
            : "neutral";
  const labels: Record<string, string> = {
    waiting: "等待中",
    ok: "正常",
    completed: "已完成",
    complete: "已完成",
    success: "成功",
    uploaded: "已上传",
    running: "运行中",
    processing: "处理中",
    failed: "失败",
    error: "错误",
    false_positive: "误检",
    detector: "检测模块"
  };

  return <span className={`status-badge badge-${tone}`}>{labels[normalized] || status}</span>;
}
