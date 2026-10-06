/**
 * Theme Switcher for AI Study Buddy
 * Manages dynamic theme state using CSS data attributes and localStorage.
 */
(function() {
    const THEMES = ['default', 'sunset', 'cyber', 'emerald'];
    const THEME_ICONS = {
        'default': '🌌',
        'sunset': '🌅',
        'cyber': '🔮',
        'emerald': '🌿'
    };

    function setTheme(themeName) {
        if (!THEMES.includes(themeName)) themeName = 'default';
        
        // Update document attribute
        document.documentElement.setAttribute('data-theme', themeName);
        
        // Save to localStorage
        localStorage.setItem('studybuddy-theme', themeName);
        
        // Update any UI elements that show the current theme
        const themeBtn = document.getElementById('theme-toggle-btn');
        if (themeBtn) {
            const icon = THEME_ICONS[themeName];
            themeBtn.innerHTML = `<span class="nl-icon">${icon}</span>Theme: ${themeName.charAt(0).toUpperCase() + themeName.slice(1)}`;
        }
    }

    function cycleTheme() {
        const currentTheme = localStorage.getItem('studybuddy-theme') || 'default';
        const currentIndex = THEMES.indexOf(currentTheme);
        const nextIndex = (currentIndex + 1) % THEMES.length;
        setTheme(THEMES[nextIndex]);
    }

    // Initialize theme on load
    document.addEventListener('DOMContentLoaded', () => {
        const savedTheme = localStorage.getItem('studybuddy-theme') || 'default';
        setTheme(savedTheme);
        
        // Add listener to existing button if present
        const themeBtn = document.getElementById('theme-toggle-btn');
        if (themeBtn) {
            themeBtn.onclick = (e) => { e.preventDefault(); cycleTheme(); };
        }

        // Find or create the theme toggle button if it doesn't exist yet but we are in a sidebar context
        const sidebar = document.querySelector('.sidebar-bottom');
        if (sidebar && !themeBtn) {
            const btn = document.createElement('a');
            btn.href = '#';
            btn.className = 'nav-link';
            btn.id = 'theme-toggle-btn';
            btn.style.marginTop = '8px';
            btn.onclick = (e) => { e.preventDefault(); cycleTheme(); };
            
            const icon = THEME_ICONS[savedTheme];
            btn.innerHTML = `<span class="nl-icon">${icon}</span>Theme: ${savedTheme.charAt(0).toUpperCase() + savedTheme.slice(1)}`;
            
            sidebar.insertBefore(btn, sidebar.querySelector('a[href="/logout"]'));
        }
    });

    // Also apply immediately to prevent FOIT (Flash of Incorrect Theme)
    const savedTheme = localStorage.getItem('studybuddy-theme') || 'default';
    document.documentElement.setAttribute('data-theme', savedTheme);
})();
