(function () {
  var importInput = document.getElementById("codemaker-import-input");
  var importButton = document.getElementById("codemaker-import-button");
  var importStatus = document.getElementById("codemaker-import-status");
  if (!importInput || !importButton || !importStatus || !window.localStorage) {
    return;
  }

  var ZIP_STORAGE_KEY = "{{BROWSER_IMPORT_ZIP_KEY}}";
  var META_STORAGE_KEY = "{{BROWSER_IMPORT_META_KEY}}";
  var SERVER_IMPORT_PATH = "/internal/codemaker-resource-import";

  function setStatus(text) {
    importStatus.textContent = text;
  }

  function loadStoredMeta() {
    var rawMeta = window.localStorage.getItem(META_STORAGE_KEY);
    if (!rawMeta) {
      return null;
    }
    try {
      return JSON.parse(rawMeta);
    } catch (error) {
      return null;
    }
  }

  function renderStoredStatus() {
    var storedMeta = loadStoredMeta();
    if (storedMeta && storedMeta.source_name) {
      setStatus("さいごに このブラウザへ ほぞんした zip: " + storedMeta.source_name);
      return;
    }
    setStatus("zip を えらんでください");
  }

  function bytesToBase64(bytes) {
    var chunkSize = 0x8000;
    var parts = [];
    for (var index = 0; index < bytes.length; index += chunkSize) {
      var chunk = bytes.subarray(index, index + chunkSize);
      var binary = "";
      for (var chunkIndex = 0; chunkIndex < chunk.length; chunkIndex += 1) {
        binary += String.fromCharCode(chunk[chunkIndex]);
      }
      parts.push(binary);
    }
    return window.btoa(parts.join(""));
  }

  function clearBrowserImport() {
    if (typeof window.localStorage.removeItem === "function") {
      window.localStorage.removeItem(ZIP_STORAGE_KEY);
      window.localStorage.removeItem(META_STORAGE_KEY);
      return;
    }
    if (typeof window.localStorage.setItem === "function") {
      window.localStorage.setItem(ZIP_STORAGE_KEY, "");
      window.localStorage.setItem(META_STORAGE_KEY, "");
    }
  }

  async function storeBrowserImport(file) {
    var bytes = new Uint8Array(await file.arrayBuffer());
    window.localStorage.setItem(ZIP_STORAGE_KEY, bytesToBase64(bytes));
    window.localStorage.setItem(
      META_STORAGE_KEY,
      JSON.stringify({
        source_name: file.name || "code-maker.zip",
        stored_at: new Date().toISOString()
      })
    );
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

  renderStoredStatus();

  importButton.addEventListener("click", async function () {
    if (!importInput.files || !importInput.files.length) {
      renderStoredStatus();
      return;
    }
    var file = importInput.files[0];
    importButton.disabled = true;
    setStatus("とりこみ ちゅう...");
    try {
      await importZipViaServer(file);
      clearBrowserImport();
      setStatus("server に とりこみました。ほかの ききでも development で つかえます");
    } catch (error) {
      try {
        await storeBrowserImport(file);
        setStatus("server が つかえないので このブラウザに ほぞんしました");
      } catch (storageError) {
        setStatus("server にも このブラウザにも ほぞんできませんでした");
      }
    } finally {
      importButton.disabled = false;
    }
  });
})();
