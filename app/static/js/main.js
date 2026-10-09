// StudentHub Main JavaScript

document.addEventListener('DOMContentLoaded', function () {
  // 1. Theme Management (Light / Dark)
  const themeToggleBtn = document.getElementById('theme-toggle');
  const themeIcon = document.getElementById('theme-icon');
  
  function getPreferredTheme() {
    const storedTheme = localStorage.getItem('studenthub_theme');
    if (storedTheme) return storedTheme;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('studenthub_theme', theme);
    if (themeIcon) {
      if (theme === 'dark') {
        themeIcon.className = 'bi bi-sun-fill text-warning';
      } else {
        themeIcon.className = 'bi bi-moon-stars-fill text-secondary';
      }
    }
  }

  // Initialize theme
  applyTheme(getPreferredTheme());

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', function () {
      const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'light';
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      applyTheme(newTheme);
    });
  }

  // 2. Sidebar Toggle (Desktop collapse & Mobile drawer)
  const sidebarToggleBtn = document.getElementById('sidebar-toggle');
  const sidebarBackdrop = document.getElementById('sidebar-backdrop');
  const appContainer = document.querySelector('.app-container');

  if (sidebarToggleBtn) {
    sidebarToggleBtn.addEventListener('click', function () {
      if (window.innerWidth < 992) {
        document.body.classList.toggle('sidebar-mobile-open');
      } else {
        document.body.classList.toggle('sidebar-collapsed');
        const isCollapsed = document.body.classList.contains('sidebar-collapsed');
        localStorage.setItem('studenthub_sidebar_collapsed', isCollapsed ? '1' : '0');
      }
    });
  }

  if (sidebarBackdrop) {
    sidebarBackdrop.addEventListener('click', function () {
      document.body.classList.remove('sidebar-mobile-open');
    });
  }

  // Restore desktop sidebar state
  if (window.innerWidth >= 992) {
    if (localStorage.getItem('studenthub_sidebar_collapsed') === '1') {
      document.body.classList.add('sidebar-collapsed');
    }
  }

  // 3. Auto-dismiss alerts after 5 seconds
  const autoAlerts = document.querySelectorAll('.alert-dismissible');
  autoAlerts.forEach(alert => {
    setTimeout(() => {
      try {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        bsAlert.close();
      } catch (e) {
        // ignore if already closed
      }
    }, 5000);
  });

  // 4. Client-side Search Filter for Tables
  const clientSearchInputs = document.querySelectorAll('[data-table-search]');
  clientSearchInputs.forEach(input => {
    const tableId = input.getAttribute('data-table-search');
    const table = document.getElementById(tableId);
    if (!table) return;

    input.addEventListener('keyup', function () {
      const filter = input.value.toLowerCase();
      const rows = table.querySelectorAll('tbody tr');
      rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(filter) ? '' : 'none';
      });
    });
  });
});
