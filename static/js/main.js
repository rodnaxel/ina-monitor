const ctxMain = document.getElementById("mainChart").getContext("2d");
const ctxPower = document.getElementById("powerChart").getContext("2d");

let windowSize = 30; // seconds of data to show
let allData = [];

const mainChart = new Chart(ctxMain, {
  type: "line",
  data: {
    labels: [],
    datasets: [
      {
        label: "Напряжение (V)",
        data: [],
        borderColor: "#38bdf8",
        backgroundColor: "rgba(56, 189, 248, 0.1)",
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.3,
        yAxisID: "y",
      },
      {
        label: "Ток (A)",
        data: [],
        borderColor: "#fbbf24",
        backgroundColor: "rgba(251, 191, 36, 0.1)",
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.3,
        yAxisID: "y1",
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    interaction: { mode: "index", intersect: false },
    plugins: {
      legend: { labels: { color: "#94a3b8" } },
    },
    scales: {
      x: {
        ticks: { color: "#64748b", maxTicksLimit: 8 },
        grid: { color: "#334155" },
      },
      y: {
        type: "linear",
        display: true,
        position: "left",
        ticks: { color: "#38bdf8" },
        grid: { color: "#334155" },
        title: { display: true, text: "V", color: "#38bdf8" },
      },
      y1: {
        type: "linear",
        display: true,
        position: "right",
        ticks: { color: "#fbbf24" },
        grid: { drawOnChartArea: false },
        title: { display: true, text: "A", color: "#fbbf24" },
      },
    },
  },
});

const powerChart = new Chart(ctxPower, {
  type: "line",
  data: {
    labels: [],
    datasets: [
      {
        label: "Мощность (W)",
        data: [],
        borderColor: "#f87171",
        backgroundColor: "rgba(248, 113, 113, 0.15)",
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.3,
        fill: true,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    plugins: {
      legend: { labels: { color: "#94a3b8" } },
    },
    scales: {
      x: {
        ticks: { color: "#64748b", maxTicksLimit: 8 },
        grid: { color: "#334155" },
      },
      y: {
        ticks: { color: "#f87171" },
        grid: { color: "#334155" },
        title: { display: true, text: "W", color: "#f87171" },
      },
    },
  },
});

function setWindow(seconds) {
  windowSize = seconds;
  document
    .querySelectorAll(".controls .btn")
    .forEach((b) => b.classList.remove("active"));
  event.target.classList.add("active");
  updateCharts();
}

function updateCharts() {
  let data = allData;
  if (windowSize > 0) {
    const cutoff = Date.now() / 1000 - windowSize;
    data = allData.filter((d) => d.timestamp > cutoff);
  }

  const labels = data.map((d) => {
    const dt = new Date(d.timestamp * 1000);
    return dt.toLocaleTimeString("ru-RU", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  });

  mainChart.data.labels = labels;
  mainChart.data.datasets[0].data = data.map((d) => d.supply_voltage);
  mainChart.data.datasets[1].data = data.map((d) => d.current);
  mainChart.update("none");

  powerChart.data.labels = labels;
  powerChart.data.datasets[0].data = data.map((d) => d.power);
  powerChart.update("none");
}

async function fetchData() {
  try {
    const res = await fetch("/api/data");
    const json = await res.json();

    if (json.latest) {
      document.getElementById("supplyV").textContent =
        json.latest.supply_voltage.toFixed(3);
      document.getElementById("busV").textContent =
        json.latest.bus_voltage.toFixed(3);
      document.getElementById("currentA").textContent =
        json.latest.current.toFixed(4);
      document.getElementById("powerW").textContent =
        json.latest.power.toFixed(4);
      document.getElementById("shuntV").textContent = (
        json.latest.shunt_voltage * 1000
      ).toFixed(3);
    }

    allData = json.data;
    updateCharts();

    // Check for overflow (bus voltage near max or current near max)
    if (
      json.latest &&
      (json.latest.bus_voltage > 31.5 || Math.abs(json.latest.current) > 3.1)
    ) {
      document.getElementById("overflowWarn").classList.add("show");
    } else {
      document.getElementById("overflowWarn").classList.remove("show");
    }
  } catch (e) {
    document.getElementById("statusText").textContent =
      "Ошибка подключения: " + e.message;
  }
}

// Update at 5 Hz (UI refresh), data collected at 10 Hz
setInterval(fetchData, 200);
