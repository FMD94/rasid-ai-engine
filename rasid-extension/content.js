function getVisibleText() {
  if (!document.body) return "";

  return document.body.innerText
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 1000);
}

let rasidHasRun = false;

async function runRasidAnalysis() {
  if (rasidHasRun) return;
  rasidHasRun = true;

  const text = getVisibleText();

  if (!text || text.length < 50) {
    console.log("RASID: not enough content yet");
    return;
  }

  try {
    const formData = new FormData();
    formData.append("text", text);

    const response = await fetch("http://127.0.0.1:8000/analyze/text/auto", {
      method: "POST",
      body: formData
    });

    const result = await response.json();
    console.log("RASID RESULT:", result);

  } catch (e) {
    console.error("RASID ERROR:", e);
  }
}

window.addEventListener("load", () => {
  setTimeout(runRasidAnalysis, 2000);
});