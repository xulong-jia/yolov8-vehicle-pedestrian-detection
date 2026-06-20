export default function StatusPanel() {
  return (
    <section className="panel">
      <p className="eyebrow">说明</p>
      <h2>最小 React 前端</h2>
      <p>
        这是一个面向本地演示的最小 React 前端。它依赖 FastAPI 后端已经运行，
        Streamlit 仍然保留为本地演示入口。
      </p>
      <ul className="status-list">
        <li>依赖 FastAPI 后端运行。</li>
        <li>支持视频任务提交、状态查询、结果下载、问题样例记录。</li>
        <li>支持可选访问密钥 X-API-Key。</li>
        <li>显示请求编号 X-Request-ID，方便排查问题。</li>
        <li>不包含视频播放器。</li>
        <li>不包含多用户权限或生产级登录系统。</li>
        <li>不包含 DeepSORT 或生产级 dashboard。</li>
      </ul>
    </section>
  );
}
