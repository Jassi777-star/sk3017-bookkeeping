课程设计选题：题目三-个人记账本（收支管理 + 图表统计）

# 个人记账本 MVP

基于 Flask、SQLAlchemy 和 ECharts 的单用户收支管理 Web 应用。当前版本已包含交易管理、服务端聚合统计、图表、月度预算和提醒。

GitHub 仓库：`https://github.com/Jassi777-star/sk3017-bookkeeping`

## 当前功能

- 自定义收入、支出分类。
- 新增、编辑、删除交易。
- 按月份、类型、分类组合筛选，每页 20 条。
- 金额、日期和分类类型校验。
- 当月收入、支出、结余指标。
- 月度预算设置、使用进度和 80% 提醒。
- 支出分类饼图、近 6 个月收支柱状图、每日支出折线图。
- 自定义 404/500 错误页和响应式侧栏应用壳层。
- 60 条动态演示数据和默认分类。

## 界面预览

![财务概览](screenshots/dashboard-desktop.png)

![移动端财务概览](screenshots/dashboard-mobile.png)

## 技术栈

- Python 3.12
- Flask 3.1
- Flask-SQLAlchemy 3.1
- Flask-WTF 1.2
- MySQL 8 / SQLite（MVP 本地回退）
- ECharts 5.5

## 快速启动（零配置 SQLite）

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:FLASK_APP = "run.py"
.\.venv\Scripts\python.exe -m flask init-db
.\.venv\Scripts\python.exe -m flask seed-demo
.\.venv\Scripts\python.exe run.py
```

浏览器访问：`http://127.0.0.1:5000`

SQLite 数据文件位于 `instance/bookkeeping.sqlite`，仅用于本地 MVP 快速体验。

本项目为单用户本地应用，不设登录账号。进入系统后直接使用分类、交易、预算和图表功能。

## MySQL 配置

1. 创建数据库并建表：

```powershell
Get-Content database\schema.sql -Raw -Encoding UTF8 |
  mysql -u root -p --default-character-set=utf8mb4
```

2. 导入默认分类和 60 条演示交易：

```powershell
Get-Content database\seed.sql -Raw -Encoding UTF8 |
  mysql -u root -p --default-character-set=utf8mb4
```

3. 将 `.env.example` 复制为 `.env`，填写真实 MySQL 密码：

```text
SECRET_KEY=replace-with-a-random-local-secret
DATABASE_URL=mysql+pymysql://root:your_password@127.0.0.1:3306/sk3017_bookkeeping?charset=utf8mb4
```

4. 启动项目：

```powershell
.\.venv\Scripts\python.exe run.py
```

## 测试

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

测试使用内存 SQLite，以保证快速反馈；项目已在临时 MySQL 8.0.46 实例中实际执行 `schema.sql` 和 `seed.sql`，页面及三类统计接口均返回 200。

当前测试结果：`25 passed`。桌面端与 390px 移动端已通过 Playwright 验证，三张 ECharts 图表均实际绘制。

## 目录

```text
app/
  routes/           页面和统计接口
  services/         月份边界与聚合查询
  static/           CSS、JavaScript、ECharts
  templates/        Jinja 页面
database/
  schema.sql        MySQL 建表脚本
docs/               开发、Debug 与 AI 协作记录
tests/              pytest 自动化测试
```

## MVP 边界

当前不包含注册登录、多用户、账单导入、Excel 导出和移动 App。

UI 设计参考与取舍见 `docs/UI_REFERENCES.md`。

系统架构、ER 图、表结构和聚合 SQL 见 `docs/DESIGN.md`。

课程设计报告：

- Word 可编辑版：`docs/SK3017课程设计报告（个人记账本）.docx`
- PDF 提交版：`docs/课程设计报告.pdf`

报告正文已完成，封面中的姓名、学号、教学班、递交日期和签名需本人填写。
