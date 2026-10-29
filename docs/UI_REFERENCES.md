# UI 与交互参考

调研日期：2026-10-29

## 参考项目

| 项目 | Stars | 许可证 | 主要借鉴内容 |
| --- | ---: | --- | --- |
| [maybe-finance/maybe](https://github.com/maybe-finance/maybe) | 54.2k | AGPL-3.0 | 个人财务信息的层级、预算进度和指标组织 |
| [tabler/tabler](https://github.com/tabler/tabler) | 42.0k | MIT | 紧凑后台应用壳层、侧栏导航、卡片和表格密度 |
| [actualbudget/actual](https://github.com/actualbudget/actual) | 29.8k | MIT | 本地优先产品感、交易列表和清晰的财务状态 |
| [ColorlibHQ/gentelella](https://github.com/ColorlibHQ/gentelella) | 21.5k | MIT | 后台导航、内容区宽度和表格可读性 |

## 本项目采用的设计原则

- 使用固定侧栏和轻量顶部操作区，桌面端形成稳定应用壳层。
- 移动端把侧栏收束为横向导航，不引入抽屉脚本。
- 指标卡分别使用蓝、红、绿、金色区分收入、支出、结余和预算。
- 图表上保留简短说明，图表数据仍由服务端接口提供。
- 交易列表使用柔和表头、类型标签和更高行距，便于快速扫描。
- 预算达到 80% 时显示带文字的警示条，不只依赖颜色。
- 使用本地 CSS 和 ECharts，不增加前端框架或 CDN 运行依赖。

## 使用边界

上述项目只用于信息架构与视觉原则参考。没有复制其源码、模板或素材。`maybe-finance/maybe` 使用 AGPL-3.0，后续也不应直接复制其代码。
