import { Panel, StatusBadge } from "./DashboardUi";

export default function StatusPanel() {
  return (
      <Panel title="项目边界" eyebrow="说明">
      <p>
        本系统用于课程演示与本机功能验证。React 负责提交任务、查看状态和整理结果，
        Streamlit 仍然保留为本地演示入口。
      </p>
      <div className="status-row">
        <StatusBadge status="说明" />
        <span>非生产级系统</span>
        <span>不作为公共安全决策依据</span>
      </div>
      <ul className="status-list">
        <li>依赖 FastAPI 后端运行。</li>
        <li>支持图片检测、视频任务提交、状态查询、结果下载、问题样例记录。</li>
        <li>支持可选访问密钥。</li>
        <li>显示请求编号，方便排查问题。</li>
        <li>不声明官方评测指标或生产级跟踪评测结果。</li>
        <li>不包含多用户权限或生产级登录系统。</li>
      </ul>
    </Panel>
  );
}
