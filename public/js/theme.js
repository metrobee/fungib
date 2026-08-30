/**
 * FUNGIB DESIGN SYSTEM - UNIVERSAL THEME MANAGER
 * Automatically restores and toggles data-theme="dark" | "light"
 */
(function() {
  const savedTheme = localStorage.getItem('theme') || (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', savedTheme);

  window.toggleTheme = function() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeToggleButtons(newTheme);
  };

  function updateThemeToggleButtons(theme) {
    document.querySelectorAll('.btn-theme-toggle').forEach(btn => {
      btn.textContent = theme === 'dark' ? 'Valge teema' : 'Tume teema';
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    updateThemeToggleButtons(document.documentElement.getAttribute('data-theme') || 'light');
  });
})();
