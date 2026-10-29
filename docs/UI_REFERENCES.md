# UI 与交互参考

调研日期：2026-10-29

## 参考项目

| 项目 | Stars | 许可证 | 主要借鉴内容 |
| --- | ---: | --- | --- |
| [shadcn-ui/ui](https://github.com/shadcn-ui/ui) | 126.8k | MIT | 克制的边框、紧凑控件、明确状态和可组合组件层级 |
| [saadeghi/daisyui](https://github.com/saadeghi/daisyui) | 42.7k | MIT | 现代卡片、表单和响应式布局模式 |
| [tabler/tabler](https://github.com/tabler/tabler) | 42.0k | MIT | 紧凑后台信息密度与表格可读性 |
| [actualbudget/actual](https://github.com/actualbudget/actual) | 29.8k | MIT | 本地优先产品感和交易管理体验 |
| [lucide-icons/lucide](https://github.com/lucide-icons/lucide) | 25.4k | ISC | 统一线性图标系统 |
| [midday-ai/midday](https://github.com/midday-ai/midday) | 15.1k | AGPL-3.0 | 现代财务产品中的指标、预算和内容组织 |
| [maybe-finance/maybe](https://github.com/maybe-finance/maybe) | 54.2k | AGPL-3.0 | 个人财务信息的层级、预算进度和指标组织 |

## 本项目采用的设计原则

- 使用窄图标侧栏和浮动顶部操作区，减少传统后台模板的厚重感。
- 移动端把侧栏收束为单行图标导航，不引入抽屉脚本。
- 使用 Lucide 线性图标保证导航、按钮和状态图标一致。
- 深色结余卡作为视觉重点，收入、支出和预算使用绿、珊瑚和琥珀语义色。
- 移动端表格改为字段信息行，避免横向滚动截断内容。
- 图表上保留简短说明，图表数据仍由服务端接口提供。
- 交易列表使用柔和表头、类型标签和更高行距，便于快速扫描。
- 预算达到 80% 时显示带文字的警示条，不只依赖颜色。
- 使用本地 CSS 和 ECharts，不增加前端框架或 CDN 运行依赖。

## 使用边界

上述项目只用于信息架构与视觉原则参考。没有复制其页面源码或模板。`maybe-finance/maybe` 和 `midday-ai/midday` 使用 AGPL-3.0，后续也不应直接复制其代码。Lucide 图标库按 ISC 许可证作为本地静态依赖使用。
