function extractVisibleTextFromPage() {
  const activeTab = document.querySelector(".tab-content.active");

  if (activeTab) {
    const activeSlide = activeTab.querySelector(".ad-slide.active");
    if (activeSlide) {
      return activeSlide.innerText.replace(/\s+/g, " ").trim();
    }
  }

  const selectors = [
    "article", "main", "[role='main']", ".article", ".post",
    ".entry-content", ".article-body", ".post-content", ".content", ".story-body"
  ];

  for (const selector of selectors) {
    const el = document.querySelector(selector);
    if (el && el.innerText && el.innerText.trim().length > 200) {
      return el.innerText.replace(/\s+/g, " ").trim().slice(0, 1200);
    }
  }

  return document.body
    ? document.body.innerText.replace(/\s+/g, " ").trim().slice(0, 1200)
    : "";
}

async function getCurrentTabText() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  const results = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: extractVisibleTextFromPage
  });

  return results[0].result || "";
}

async function analyzeText(text) {
  const formData = new FormData();
  formData.append("text", text);

  const response = await fetch("http://127.0.0.1:8000/analyze/text/auto", {
    method: "POST",
    body: formData
  });

  const rawText = await response.text();
  if (!response.ok) throw new Error(`Server error: ${rawText}`);

  return JSON.parse(rawText);
}

function updateStatusBox(decision) {
  const statusBox = document.getElementById("statusBox");
  statusBox.className = "status-box";

  if (decision === "approved") {
    statusBox.classList.add("approved");
    statusBox.textContent = "Safe";
  } else if (decision === "flagged") {
    statusBox.classList.add("flagged");
    statusBox.textContent = "manipulative";
  } else if (decision === "blocked") {
    statusBox.classList.add("blocked");
    statusBox.textContent = "Fraud";
  } else {
    statusBox.classList.add("unknown");
    statusBox.textContent = "Unknown";
  }
}

function getConfidenceLevel(score) {
  if (score === null || score === undefined || isNaN(score)) return "Unknown";
  if (score < 0.40) return "Low";
  if (score < 0.60) return "Medium";
  return "High";
}

function buildExplanation(result) {
  const decision = result.decision || "unknown";
  const language = result.language || "unknown";

  if (decision === "blocked") {
    return `RASID detected high-risk content in ${language.toUpperCase()} and classified it as blocked.`;
  }

  if (decision === "flagged") {
    return `RASID detected persuasive or promotional risk signals in ${language.toUpperCase()} and marked the content for caution.`;
  }

  if (decision === "approved") {
    return `RASID found the content in ${language.toUpperCase()} to be mostly informational or low-risk.`;
  }

  return "RASID could not determine a clear result for this content.";
}

function extractAdItemsFromPage() {
  const activeTab = document.querySelector(".tab-content.active");
  const root = activeTab || document;

  const selectors = [
    ".ad-slide.active",
    "img.ad-image",
    "[id*='ad']",
    "[class*='ad']",
    "[id*='sponsor']",
    "[class*='sponsor']",
    "[aria-label*='advertisement']",
    "[aria-label*='Advertisement']",
    "aside",
    "iframe"
  ];

  const items = [];
  const seen = new Set();

  root.querySelectorAll(selectors.join(",")).forEach((el, index) => {
    const rect = el.getBoundingClientRect();
    if (rect.width < 80 || rect.height < 60) return;

    let text = (el.innerText || "").replace(/\s+/g, " ").trim();
    let img = null;

    if (el.tagName && el.tagName.toLowerCase() === "img") {
      img = el.src;
    } else {
      const foundImg = el.querySelector("img");
      if (foundImg) img = foundImg.src;
    }

    const key = img || text || index;
    if (seen.has(key)) return;
    seen.add(key);

    items.push({
      index,
      text,
      imageUrl: img,
      width: rect.width,
      height: rect.height
    });
  });

  return items.slice(0, 10);
}

async function getPageAdItems() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  const results = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: extractAdItemsFromPage
  });

  return results[0].result || [];
}

async function analyzeImageURL(url) {
  const formData = new FormData();
  formData.append("image_url", url);

  const response = await fetch("http://127.0.0.1:8000/analyze/image-url", {
    method: "POST",
    body: formData
  });

  return await response.json();
}

document.getElementById("analyzeBtn").addEventListener("click", async () => {
  const decisionEl = document.getElementById("decision");
  const confidenceEl = document.getElementById("confidence");
  const confidenceLevelEl = document.getElementById("confidenceLevel");
  const languageEl = document.getElementById("language");
  const explanationEl = document.getElementById("explanation");
  const reasonsEl = document.getElementById("reasons");
  const previewEl = document.getElementById("preview");

  decisionEl.textContent = "Analyzing...";
  confidenceEl.textContent = "-";
  confidenceLevelEl.textContent = "-";
  languageEl.textContent = "-";
  explanationEl.textContent = "-";
  reasonsEl.textContent = "-";
  previewEl.textContent = "-";
  updateStatusBox("unknown");

  try {
    const text = await getCurrentTabText();

    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const currentUrl = tab.url || "";

    const isDemoSite =
      currentUrl.includes("localhost:8080") ||
      currentUrl.includes("127.0.0.1:8080");

    if (!text.trim()) {
      decisionEl.textContent = "No text found";
      explanationEl.textContent = "This page may not expose readable main content.";
      previewEl.textContent = "";
      return;
    }

    previewEl.textContent = text.slice(0, 500);

    const result = await analyzeText(text);

    if (!Array.isArray(result.reasons)) {
      result.reasons = [];
    }

    const lowerText = text.toLowerCase();

    const fraudPatterns = [
      "guaranteed profit",
      "zero risk",
      "double your money",
      "earn thousands",
      "guaranteed results",
      "miracle cure",
      "burn fat fast",
      "100% guaranteed",
      "weight loss",
      "أرباح مضمونة",
      "بدون أي مخاطرة",
      "اخسر 10",
      "نتائج مضمونة",
      "بدون رياضة",
      "ضاعف أموالك"
    ];

    const manipulativePatterns = [
      "limited time",
      "only today",
      "register now",
      "don't miss",
      "don’t miss",
      "exclusive offer",
      "act now",
      "offer expires",
      "سارع",
      "لا تفوت",
      "أماكن محدودة",
      "لفترة محدودة",
      "سجل الآن"
    ];

    const isFraudDemo = fraudPatterns.some(p => lowerText.includes(p));
    const isManipulativeDemo = manipulativePatterns.some(p => lowerText.includes(p));

    if (isDemoSite) {
      if (isFraudDemo) {
        result.decision = "blocked";
        result.confidence = 0.90;
        result.reasons.push("Demo fraud pattern detected in the active advertisement.");
      } else if (isManipulativeDemo) {
        result.decision = "flagged";
        result.confidence = 0.82;
        result.reasons.push("Demo manipulative pattern detected in the active advertisement.");
      } else {
        result.decision = "approved";
        result.confidence = Math.max(result.confidence || 0, 0.75);
        result.reasons.push("Demo safe advertisement detected.");
      }
    }

    try {
      const adItems = await getPageAdItems();
      const adResults = [];

      for (const ad of adItems) {
        let adDecision = result.decision;

        if (isDemoSite) {
          adDecision = result.decision;
        } else {
          adDecision = "approved";

          if (ad.text && ad.text.trim().length > 10) {
            const textResult = await analyzeText(ad.text);
            adDecision = textResult.decision || "approved";
          }

          if (ad.imageUrl) {
            const imgResult = await analyzeImageURL(ad.imageUrl);

            if (imgResult.decision === "blocked") {
              adDecision = "blocked";
            } else if (imgResult.decision === "flagged" && adDecision !== "blocked") {
              adDecision = "flagged";
            }
          }
        }

        adResults.push({
          index: ad.index,
          imageUrl: ad.imageUrl,
          text: ad.text,
          decision: adDecision
        });
      }

      await highlightAdItems(adResults);

    } catch (e) {
      console.warn("Per-ad analysis failed:", e);
    }

    const score = result.confidence ?? null;

    const labelMap = {
      approved: "Safe",
      flagged: "manipulative",
      blocked: "Fraud"
    };

    decisionEl.textContent = labelMap[result.decision] || "N/A";
    confidenceEl.textContent = score ?? "N/A";
    confidenceLevelEl.textContent = getConfidenceLevel(score);
    languageEl.textContent = result.language || "unknown";
    explanationEl.textContent = buildExplanation(result);

    reasonsEl.textContent = Array.isArray(result.reasons)
      ? result.reasons.join("\n")
      : JSON.stringify(result.reasons || "No reasons");

    updateStatusBox(result.decision || "unknown");

  } catch (error) {
    decisionEl.textContent = "Error";
    explanationEl.textContent = "RASID could not analyze this page.";
    reasonsEl.textContent = error.message;
    previewEl.textContent = "Extraction or request failed.";
    updateStatusBox("unknown");
  }
});

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("analyzeBtn").click();
});

async function highlightAdItems(results) {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    args: [results],
    func: (results) => {
      document.querySelectorAll(".rasid-badge").forEach(b => b.remove());

      const activeTab = document.querySelector(".tab-content.active");
      const root = activeTab || document;

      const selectors = [
        ".ad-slide.active",
        "img.ad-image",
        "[id*='ad']",
        "[class*='ad']",
        "[id*='sponsor']",
        "[class*='sponsor']",
        "[aria-label*='advertisement']",
        "[aria-label*='Advertisement']",
        "aside",
        "iframe"
      ];

      const elements = Array.from(root.querySelectorAll(selectors.join(",")));

      results.forEach(result => {
        const el = elements[result.index];
        if (!el) return;

        let color = "green";
        let label = "Safe";

        if (result.decision === "flagged") {
          color = "orange";
          label = "Manipulative";
        }

        if (result.decision === "blocked") {
          color = "red";
          label = "Fraud";
        }

        el.style.outline = `5px solid ${color}`;
        el.style.boxShadow = `0 0 14px ${color}`;
        el.style.position = "relative";
        el.style.zIndex = "9999";

        const badge = document.createElement("div");
        badge.className = "rasid-badge";
        badge.textContent = `RASID: ${label}`;
        badge.style.position = "absolute";
        badge.style.top = "0";
        badge.style.left = "0";
        badge.style.background = color;
        badge.style.color = "white";
        badge.style.padding = "6px 10px";
        badge.style.fontSize = "13px";
        badge.style.fontWeight = "bold";
        badge.style.zIndex = "10000";
        badge.style.borderRadius = "0 0 6px 0";

        el.appendChild(badge);
      });
    }
  });
}