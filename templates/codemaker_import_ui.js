(function () {
  var importInput = document.getElementById("codemaker-import-input");
  var importButton = document.getElementById("codemaker-import-button");
  var importStatus = document.getElementById("codemaker-import-status");
  if (!importInput || !importButton || !importStatus) {
    return;
  }

  var SERVER_IMPORT_PATH = "/internal/codemaker-resource-import";

  function setStatus(text) {
    importStatus.textContent = text;
  }

  async function importZipViaServer(file) {
    var payload = await file.arrayBuffer();
    var response = await fetch(SERVER_IMPORT_PATH, {
      method: "POST",
      headers: {
        "Content-Type": "application/zip",
        "X-Filename": file.name || "code-maker.zip"
      },
      body: payload
    });
    if (!response.ok) {
      throw new Error("server import failed");
    }
    try {
      return await response.json();
    } catch (error) {
      return {};
    }
  }

  setStatus("zip を えらんでください");

  importButton.addEventListener("click", async function () {
    if (!importInput.files || !importInput.files.length) {
      setStatus("zip を えらんでください");
      return;
    }
    var file = importInput.files[0];
    importButton.disabled = true;
    setStatus("とりこみ ちゅう...");
    try {
      await importZipViaServer(file);
      setStatus("server に とりこみました。みんなに ゆきわたります");
    } catch (error) {
      setStatus("server に とりこみできませんでした。しばらくたってから もういちど");
    } finally {
      importButton.disabled = false;
    }
  });
})();
