document.addEventListener('DOMContentLoaded', function() {
  // Default themes
  const themes = {
    default: {
      primaryColor: '#1a1a1a',
      secondaryColor: '#f7f7f7',
      accentColor: '#d32f2f',
      textColor: '#2c2c2c',
      linkColor: '#0066cc'
    },
    dark: {
      primaryColor: '#121212',
      secondaryColor: '#1e1e1e',
      accentColor: '#bb86fc',
      textColor: '#e0e0e0',
      linkColor: '#03dac6'
    },
    light: {
      primaryColor: '#ffffff',
      secondaryColor: '#f5f5f5',
      accentColor: '#0066cc',
      textColor: '#333333',
      linkColor: '#d32f2f'
    },
    nature: {
      primaryColor: '#2e7d32',
      secondaryColor: '#f1f8e9',
      accentColor: '#ff6d00',
      textColor: '#333333',
      linkColor: '#1b5e20'
    },
    ocean: {
      primaryColor: '#01579b',
      secondaryColor: '#e1f5fe',
      accentColor: '#ff6f00',
      textColor: '#263238',
      linkColor: '#0277bd'
    }
  };
  
  // Create theme switcher HTML
  function createThemeSwitcher() {
    const themeSwitcher = document.createElement('div');
    themeSwitcher.className = 'theme-switcher';
    
    // Create theme switcher toggle button
    const toggleButton = document.createElement('button');
    toggleButton.className = 'theme-toggle-btn';
    toggleButton.innerHTML = '<i class="fas fa-palette"></i>';
    
    // Create theme options container
    const themeOptions = document.createElement('div');
    themeOptions.className = 'theme-options';
    
    // Add title for the theme switcher
    const title = document.createElement('h4');
    title.textContent = 'Choose a theme';
    themeOptions.appendChild(title);
    
    // Create theme options
    for (const [themeName, themeColors] of Object.entries(themes)) {
      const themeOption = document.createElement('div');
      themeOption.className = 'theme-option';
      themeOption.dataset.theme = themeName;
      
      // Create color preview
      const colorPreview = document.createElement('div');
      colorPreview.className = 'color-preview';
      colorPreview.style.backgroundColor = themeColors.primaryColor;
      colorPreview.style.border = `2px solid ${themeColors.accentColor}`;
      
      // Create theme name
      const themeNameEl = document.createElement('span');
      themeNameEl.textContent = themeName.charAt(0).toUpperCase() + themeName.slice(1);
      
      themeOption.appendChild(colorPreview);
      themeOption.appendChild(themeNameEl);
      themeOptions.appendChild(themeOption);
      
      // Add event listener to apply theme on click
      themeOption.addEventListener('click', function() {
        applyTheme(themeName, themeColors);
        saveThemePreference(themeName);
        
        // Add selected class to the clicked theme and remove from others
        document.querySelectorAll('.theme-option').forEach(option => {
          option.classList.remove('selected');
        });
        themeOption.classList.add('selected');
        
        // Create ripple effect
        const ripple = document.createElement('span');
        ripple.className = 'theme-ripple';
        themeOption.appendChild(ripple);
        
        // Remove ripple after animation completes
        setTimeout(() => ripple.remove(), 600);
      });
    }
    
    // Add custom theme option with color pickers
    const customThemeOption = document.createElement('div');
    customThemeOption.className = 'custom-theme-option';
    
    const customTitle = document.createElement('h5');
    customTitle.textContent = 'Custom Theme';
    customThemeOption.appendChild(customTitle);
    
    // Create color pickers
    const colorLabels = {
      primaryColor: 'Primary',
      secondaryColor: 'Secondary',
      accentColor: 'Accent',
      textColor: 'Text',
      linkColor: 'Link'
    };
    
    const customColors = {};
    
    for (const [colorKey, colorLabel] of Object.entries(colorLabels)) {
      const colorPickerContainer = document.createElement('div');
      colorPickerContainer.className = 'color-picker-container';
      
      const label = document.createElement('label');
      label.textContent = colorLabel;
      
      const colorPicker = document.createElement('input');
      colorPicker.type = 'color';
      colorPicker.value = themes.default[colorKey];
      colorPicker.dataset.colorKey = colorKey;
      customColors[colorKey] = colorPicker.value;
      
      colorPicker.addEventListener('input', function() {
        customColors[colorKey] = this.value;
        applyTheme('custom', customColors);
        saveThemePreference('custom', customColors);
      });
      
      colorPickerContainer.appendChild(label);
      colorPickerContainer.appendChild(colorPicker);
      customThemeOption.appendChild(colorPickerContainer);
    }
    
    themeOptions.appendChild(customThemeOption);
    
    // Toggle theme switcher visibility
    toggleButton.addEventListener('click', function() {
      themeOptions.classList.toggle('show');
      toggleButton.classList.toggle('active');
      
      // Animation for the toggle button
      if (toggleButton.classList.contains('active')) {
        toggleButton.innerHTML = '<i class="fas fa-times"></i>';
      } else {
        toggleButton.innerHTML = '<i class="fas fa-palette"></i>';
      }
    });
    
    // Close theme switcher when clicking outside
    document.addEventListener('click', function(e) {
      if (!themeSwitcher.contains(e.target)) {
        themeOptions.classList.remove('show');
        toggleButton.classList.remove('active');
        toggleButton.innerHTML = '<i class="fas fa-palette"></i>';
      }
    });
    
    themeSwitcher.appendChild(toggleButton);
    themeSwitcher.appendChild(themeOptions);
    
    return themeSwitcher;
  }
  
  // Apply theme by updating CSS variables
  function applyTheme(themeName, colors) {
    const root = document.documentElement;
    
    for (const [key, value] of Object.entries(colors)) {
      root.style.setProperty(`--${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`, value);
      
      // If the key is accentColor, also set the RGB version
      if (key === 'accentColor') {
        // Convert hex to RGB
        const hexToRgb = (hex) => {
          const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
          const fullHex = hex.replace(shorthandRegex, (m, r, g, b) => r + r + g + g + b + b);
          const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(fullHex);
          return result ? 
            `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}` : 
            '211, 47, 47'; // Default to default accent color RGB
        };
        
        root.style.setProperty('--accent-color-rgb', hexToRgb(value));
      }
    }
    
    // Add theme name as class to body for additional styling
    document.body.className = '';
    document.body.classList.add(`theme-${themeName}`);
    
    // Apply color to meta theme-color for mobile browsers
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', colors.primaryColor);
    } else {
      const newMetaThemeColor = document.createElement('meta');
      newMetaThemeColor.name = 'theme-color';
      newMetaThemeColor.content = colors.primaryColor;
      document.head.appendChild(newMetaThemeColor);
    }
    
    // Trigger a custom event for other scripts that might need to react to theme changes
    document.dispatchEvent(new CustomEvent('themechange', { 
      detail: { 
        theme: themeName,
        colors: colors 
      } 
    }));
  }
  
  // Save theme preference to localStorage
  function saveThemePreference(themeName, customColors = null) {
    localStorage.setItem('theme', themeName);
    if (themeName === 'custom' && customColors) {
      localStorage.setItem('customTheme', JSON.stringify(customColors));
    }
  }
  
  // Load saved theme preference
  function loadThemePreference() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      if (savedTheme === 'custom') {
        const savedCustomTheme = localStorage.getItem('customTheme');
        if (savedCustomTheme) {
          const customColors = JSON.parse(savedCustomTheme);
          applyTheme('custom', customColors);
          
          // Update color picker values if the custom theme panel exists
          document.querySelectorAll('.color-picker-container input[type="color"]').forEach(picker => {
            const colorKey = picker.dataset.colorKey;
            if (customColors[colorKey]) {
              picker.value = customColors[colorKey];
            }
          });
        }
      } else if (themes[savedTheme]) {
        applyTheme(savedTheme, themes[savedTheme]);
      }
      
      // Mark the selected theme option
      setTimeout(() => {
        const themeOption = document.querySelector(`.theme-option[data-theme="${savedTheme}"]`);
        if (themeOption) {
          themeOption.classList.add('selected');
        }
      }, 100);
    }
  }
  
  // Append theme switcher to the page
  const themeSwitcher = createThemeSwitcher();
  document.body.appendChild(themeSwitcher);
  
  // Load saved theme preference
  loadThemePreference();
  
  // Add preview animation
  const themeOptions = document.querySelectorAll('.theme-option');
  themeOptions.forEach(option => {
    option.addEventListener('mouseenter', function() {
      const themeName = this.dataset.theme;
      if (themes[themeName]) {
        const previewTheme = themes[themeName];
        document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        document.body.style.backgroundColor = previewTheme.secondaryColor;
        document.body.style.color = previewTheme.textColor;
      }
    });
    
    option.addEventListener('mouseleave', function() {
      document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
      document.body.style.backgroundColor = '';
      document.body.style.color = '';
    });
  });
});