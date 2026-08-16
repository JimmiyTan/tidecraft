const demoForm = document.querySelector("#demoForm");
const topicInput = document.querySelector("#topicInput");
const operatorInput = document.querySelector("#operatorInput");
const runButton = document.querySelector("#runButton");
const buttonText = document.querySelector("#buttonText");
const serviceStatus = document.querySelector("#serviceStatus");
const errorBanner = document.querySelector("#errorBanner");
const resultEmpty = document.querySelector("#resultEmpty");
const resultPanel = document.querySelector("#resultPanel");
const liveRegion = document.querySelector("#liveRegion");
const flowSteps = [...document.querySelectorAll(".flow-step")];

const statusLabels = {
  completed: "内容已完成",
  approved: "审核已通过",
  archived: "回执已归档",
};

function wait(milliseconds) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

function setServiceStatus(online) {
  serviceStatus.classList.toggle("online", online);
  serviceStatus.querySelector("span:last-child").textContent = online
    ? "本地安全服务已就绪"
    : "本地演示服务未连接";
}

function resetFlow() {
  flowSteps.forEach((step) => {
    step.classList.remove("active", "completed");
    step.querySelector(".step-state").textContent = "等待";
  });
}

function markStage(index, state) {
  const step = flowSteps[index];
  if (!step) return;
  step.classList.remove("active", "completed");
  step.classList.add(state);
  step.querySelector(".step-state").textContent = state === "completed" ? "完成" : "执行中";
}

async function animateCompletedFlow() {
  for (let index = 0; index < flowSteps.length; index += 1) {
    if (index > 0) {
      markStage(index - 1, "completed");
    }
    markStage(index, "active");
    await wait(240);
  }
  markStage(flowSteps.length - 1, "completed");
}

function createCandidateItem(title) {
  const item = document.createElement("li");
  item.textContent = title;
  return item;
}

function createPlatformCard(platform) {
  const card = document.createElement("div");
  card.className = "platform-card";

  const label = document.createElement("span");
  label.textContent = "PLATFORM PACKAGE";
  const name = document.createElement("strong");
  name.textContent = platform.name;
  const status = document.createElement("small");
  status.textContent = platform.receipt;

  card.append(label, name, status);
  return card;
}

function renderDemoResult(demo) {
  document.querySelector("#resultTopic").textContent = demo.topic;
  document.querySelector("#taskId").textContent = demo.task_id;
  document.querySelector("#workflowStatus").textContent =
    statusLabels[demo.workflow_status] || demo.workflow_status;
  document.querySelector("#reviewStatus").textContent =
    statusLabels[demo.review_status] || demo.review_status;
  document.querySelector("#publishStatus").textContent =
    statusLabels[demo.publish_status] || demo.publish_status;
  document.querySelector("#completedAt").textContent = new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date(demo.completed_at));

  const candidateList = document.querySelector("#candidateList");
  candidateList.replaceChildren(...demo.candidate_titles.map(createCandidateItem));

  const platformGrid = document.querySelector("#platformGrid");
  platformGrid.replaceChildren(...demo.platforms.map(createPlatformCard));

  resultEmpty.hidden = true;
  resultPanel.hidden = false;
  liveRegion.textContent = `客户演示已完成，任务 ${demo.task_id} 已归档。`;
}

async function checkHealth() {
  try {
    const response = await fetch("/api/health", { cache: "no-store" });
    setServiceStatus(response.ok);
  } catch {
    setServiceStatus(false);
  }
}

async function runCustomerDemo(event) {
  event.preventDefault();
  errorBanner.hidden = true;
  resetFlow();
  markStage(0, "active");
  runButton.disabled = true;
  buttonText.textContent = "正在生成完整闭环…";
  liveRegion.textContent = "客户演示正在运行。";

  try {
    const response = await fetch("/api/demo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        topic: topicInput.value,
        operator: operatorInput.value,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "演示执行失败，请稍后重试。");
    }

    await animateCompletedFlow();
    renderDemoResult(payload.demo);
    resultPanel.scrollIntoView({ behavior: "smooth", block: "center" });
  } catch (error) {
    resetFlow();
    errorBanner.textContent = error.message;
    errorBanner.hidden = false;
    liveRegion.textContent = `客户演示失败：${error.message}`;
  } finally {
    runButton.disabled = false;
    buttonText.textContent = "再次运行客户演示";
  }
}

demoForm.addEventListener("submit", runCustomerDemo);
checkHealth();
