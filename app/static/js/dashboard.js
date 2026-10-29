const monthInput = document.querySelector("#month-filter");
const categoryInput = document.querySelector("#category-filter");
const filterForm = document.querySelector("#dashboard-filter");
const statusText = document.querySelector("#chart-status");
let latestCategoryData = null;

const charts = {
  category: echarts.init(document.querySelector("#category-chart")),
  months: echarts.init(document.querySelector("#months-chart")),
  daily: echarts.init(document.querySelector("#daily-chart")),
};

const colors = {
  green: "#11986a",
  red: "#ed654f",
  gold: "#d89422",
  blue: "#2457e6",
  grid: "#e4e7ec",
  ink: "#131722",
  muted: "#737c8c",
};

function formatMoney(value) {
  const amount = Number(value || 0);
  return `¥${amount.toLocaleString("zh-CN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function queryUrl(base, month, categoryId, monthParameter = "month") {
  const params = new URLSearchParams({ [monthParameter]: month });
  if (categoryId) params.set("category_id", categoryId);
  return `${base}?${params.toString()}`;
}

async function getJson(url) {
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "统计数据加载失败");
  return data;
}

function emptyOption(message) {
  return {
    graphic: {
      type: "text",
      left: "center",
      top: "middle",
      style: { text: message, fill: colors.muted, fontSize: 14 },
    },
  };
}

function renderCategory(data) {
  latestCategoryData = data;
  if (!data.labels.length) {
    charts.category.setOption(emptyOption("本月暂无支出"), true);
    return;
  }
  const compact = window.innerWidth < 600;
  charts.category.setOption({
    color: [colors.green, colors.red, colors.gold, colors.blue, "#7b8c67", "#8a6d83"],
    tooltip: { trigger: "item", valueFormatter: (value) => `¥${Number(value).toFixed(2)}` },
    legend: { bottom: 0, textStyle: { color: colors.ink } },
    series: [{
      type: "pie",
      radius: ["42%", "70%"],
      center: ["50%", "45%"],
      data: data.labels.map((name, index) => ({ name, value: data.values[index] })),
      label: { show: !compact, formatter: "{b}\n{d}%" },
      labelLine: { show: !compact },
      emphasis: { label: { show: true } },
    }],
  }, true);
}

function renderMonths(data) {
  charts.months.setOption({
    color: [colors.green, colors.red],
    tooltip: { trigger: "axis", valueFormatter: (value) => `¥${Number(value).toFixed(2)}` },
    legend: { top: 0, data: ["收入", "支出"], textStyle: { color: colors.ink } },
    grid: { left: 18, right: 18, bottom: 18, top: 48, containLabel: true },
    xAxis: {
      type: "category",
      data: data.months,
      axisLine: { lineStyle: { color: colors.grid } },
      axisLabel: { color: colors.muted },
    },
    yAxis: {
      type: "value",
      splitLine: { lineStyle: { color: colors.grid } },
      axisLabel: { color: colors.muted },
    },
    series: [
      { name: "收入", type: "bar", data: data.income, barMaxWidth: 28 },
      { name: "支出", type: "bar", data: data.expense, barMaxWidth: 28 },
    ],
  }, true);
}

function renderDaily(data) {
  charts.daily.setOption({
    color: [colors.red],
    tooltip: { trigger: "axis", valueFormatter: (value) => `¥${Number(value).toFixed(2)}` },
    grid: { left: 18, right: 18, bottom: 18, top: 24, containLabel: true },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: data.days.map((day) => day.slice(5)),
      axisLine: { lineStyle: { color: colors.grid } },
      axisLabel: { color: colors.muted },
    },
    yAxis: {
      type: "value",
      splitLine: { lineStyle: { color: colors.grid } },
      axisLabel: { color: colors.muted },
    },
    series: [{
      name: "每日支出",
      type: "line",
      smooth: true,
      symbolSize: 6,
      data: data.expenses,
      areaStyle: { opacity: 0.12 },
    }],
  }, true);
}

function renderSummary(data) {
  const income = data.income.at(-1) || 0;
  const expense = data.expense.at(-1) || 0;
  document.querySelector("#metric-income").textContent = formatMoney(income);
  document.querySelector("#metric-expense").textContent = formatMoney(expense);
  document.querySelector("#metric-balance").textContent = formatMoney(income - expense);
}

function renderBudget(data) {
  const budgetValue = document.querySelector("#metric-budget");
  const budgetFill = document.querySelector("#budget-fill");
  const budgetMeta = document.querySelector("#budget-meta");
  const alert = document.querySelector("#budget-alert");
  const alertCopy = document.querySelector("#budget-alert-copy");
  const budgetLink = document.querySelector("#budget-link");

  budgetValue.textContent = data.has_budget ? formatMoney(data.total_amount) : "未设置";
  budgetFill.style.width = `${Math.min(data.usage_ratio * 100, 100)}%`;
  budgetFill.classList.toggle("warning", data.alert);
  budgetMeta.textContent = data.has_budget
    ? `已用 ${formatMoney(data.expense)}，剩余 ${formatMoney(data.remaining)}`
    : "设置预算后显示使用进度";
  alert.hidden = !data.alert;
  if (data.alert) {
    alertCopy.textContent = `本月已使用预算的 ${Math.round(data.usage_ratio * 100)}%，请留意后续支出。`;
  }

  const url = new URL(budgetLink.href, window.location.origin);
  url.searchParams.set("month", data.month);
  budgetLink.href = url.toString();
}

async function refreshDashboard() {
  statusText.textContent = "加载中…";
  const month = monthInput.value;
  const categoryId = categoryInput.value;
  try {
    const [categoryData, monthsData, dailyData, budgetData] = await Promise.all([
      getJson(queryUrl(window.dashboardConfig.categoryUrl, month, categoryId)),
      getJson(queryUrl(window.dashboardConfig.monthsUrl, month, categoryId, "end")),
      getJson(queryUrl(window.dashboardConfig.dailyUrl, month, categoryId)),
      getJson(queryUrl(window.dashboardConfig.budgetUrl, month, null)),
    ]);
    renderCategory(categoryData);
    renderMonths(monthsData);
    renderDaily(dailyData);
    renderSummary(monthsData);
    renderBudget(budgetData);
    statusText.textContent = "";
    const url = new URL(window.location.href);
    url.searchParams.set("month", month);
    categoryId ? url.searchParams.set("category_id", categoryId) : url.searchParams.delete("category_id");
    window.history.replaceState({}, "", url);
  } catch (error) {
    statusText.textContent = error.message;
  }
}

filterForm.addEventListener("submit", (event) => {
  event.preventDefault();
  refreshDashboard();
});

window.addEventListener("resize", () => {
  Object.values(charts).forEach((chart) => chart.resize());
  if (latestCategoryData) renderCategory(latestCategoryData);
});

refreshDashboard();
