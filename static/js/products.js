(function () {
  function openModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add("visible");
  }

  function closeModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove("visible");
  }

  document.querySelectorAll("[data-close-modal]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      closeModal(btn.getAttribute("data-close-modal"));
    });
  });

  document.querySelectorAll(".modal-overlay").forEach(function (overlay) {
    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) overlay.classList.remove("visible");
    });
  });

  const openMap = {
    openCategoryModal: "categoryModalOverlay",
    openProductModal: "productModalOverlay",
    openBulkModal: "bulkModalOverlay",
    openSummaryCount: "summaryCountModal",
    openSummaryAmount: "summaryAmountModal",
  };

  Object.keys(openMap).forEach(function (btnId) {
    const btn = document.getElementById(btnId);
    if (btn) {
      btn.addEventListener("click", function () {
        openModal(openMap[btnId]);
      });
    }
  });

  document.querySelectorAll(".modal-tab").forEach(function (tab) {
    tab.addEventListener("click", function () {
      const panelId = "tab-" + tab.getAttribute("data-tab");
      const container = tab.closest(".product-modal-lg") || tab.closest(".product-modal");
      if (!container) return;
      container.querySelectorAll(".modal-tab").forEach(function (t) {
        t.classList.remove("active");
      });
      container.querySelectorAll(".modal-tab-panel").forEach(function (p) {
        p.classList.remove("active");
      });
      tab.classList.add("active");
      const panel = document.getElementById(panelId);
      if (panel) panel.classList.add("active");
    });
  });
})();
