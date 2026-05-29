(function () {
  const sidebar = document.getElementById("sidebar");
  const mainWrapper = document.getElementById("mainWrapper");
  const toggleBtn = document.getElementById("sidebarToggle");
  const mobileToggle = document.getElementById("mobileSidebarToggle");
  const overlay = document.getElementById("sidebarOverlay");

  if (toggleBtn && sidebar && mainWrapper) {
    const collapsed = localStorage.getItem("sidebarCollapsed") === "true";
    if (collapsed && window.innerWidth > 768) {
      sidebar.classList.add("collapsed");
      mainWrapper.classList.add("sidebar-collapsed");
    }

    toggleBtn.addEventListener("click", function () {
      if (window.innerWidth <= 768) return;
      sidebar.classList.toggle("collapsed");
      mainWrapper.classList.toggle("sidebar-collapsed");
      localStorage.setItem(
        "sidebarCollapsed",
        sidebar.classList.contains("collapsed")
      );
    });
  }

  function closeMobileSidebar() {
    if (sidebar) sidebar.classList.remove("mobile-open");
    if (overlay) overlay.classList.remove("visible");
  }

  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener("click", function () {
      sidebar.classList.toggle("mobile-open");
      if (overlay) overlay.classList.toggle("visible");
    });
  }

  if (overlay) {
    overlay.addEventListener("click", closeMobileSidebar);
  }

  const profileToggle = document.getElementById("profileMenuToggle");
  const profileDropdown = document.getElementById("profileDropdown");
  const profileMenu = document.getElementById("profileMenu");

  if (profileToggle && profileDropdown) {
    profileToggle.addEventListener("click", function (e) {
      e.stopPropagation();
      const isOpen = profileDropdown.classList.toggle("open");
      profileToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    document.addEventListener("click", function (e) {
      if (profileMenu && !profileMenu.contains(e.target)) {
        profileDropdown.classList.remove("open");
        profileToggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  const eyeIcon =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">' +
    '<path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/>' +
    '<circle cx="12" cy="12" r="3"/></svg>';

  function initPasswordToggles(root) {
    const scope = root || document;
    scope.querySelectorAll('input[type="password"]').forEach(function (input) {
      if (input.closest(".password-field")) return;

      const wrap = document.createElement("div");
      wrap.className = "password-field";
      input.parentNode.insertBefore(wrap, input);
      wrap.appendChild(input);

      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "password-toggle";
      btn.setAttribute("aria-label", "Show password on hover");
      btn.innerHTML = eyeIcon;
      wrap.appendChild(btn);

      btn.addEventListener("mouseenter", function () {
        input.type = "text";
        btn.setAttribute("aria-label", "Hide password");
      });
      btn.addEventListener("mouseleave", function () {
        input.type = "password";
        btn.setAttribute("aria-label", "Show password on hover");
      });
    });
  }

  initPasswordToggles();

  const addUserModal = document.getElementById("addUserModalOverlay");
  if (addUserModal) {
    const observer = new MutationObserver(function () {
      if (addUserModal.classList.contains("visible")) {
        initPasswordToggles(addUserModal);
      }
    });
    observer.observe(addUserModal, { attributes: true, attributeFilter: ["class"] });
  }
})();
