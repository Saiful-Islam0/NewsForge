document.addEventListener('DOMContentLoaded', function() {
  // Toggle sidebar on mobile
  const sidebarToggle = document.querySelector('.sidebar-toggle');
  const adminSidebar = document.querySelector('.admin-sidebar');
  
  if (sidebarToggle && adminSidebar) {
    sidebarToggle.addEventListener('click', function() {
      adminSidebar.classList.toggle('active');
      document.body.classList.toggle('sidebar-open');
    });
  }
  
  // Toggle dropdown menus
  const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
  
  dropdownToggles.forEach(toggle => {
    toggle.addEventListener('click', function(e) {
      e.preventDefault();
      const dropdown = this.nextElementSibling;
      
      // Close other dropdowns
      document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
        if (menu !== dropdown) {
          menu.classList.remove('show');
        }
      });
      
      // Toggle this dropdown
      dropdown.classList.toggle('show');
    });
  });
  
  // Close dropdowns when clicking outside
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.dropdown')) {
      document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
        menu.classList.remove('show');
      });
    }
  });
  
  // Confirm delete actions
  const deleteButtons = document.querySelectorAll('.delete-btn');
  
  deleteButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
        e.preventDefault();
      }
    });
  });
  
  // Color picker initialization for theme settings
  const colorInputs = document.querySelectorAll('input[type="color"]');
  
  colorInputs.forEach(input => {
    const preview = document.createElement('div');
    preview.className = 'color-preview';
    preview.style.backgroundColor = input.value;
    
    // Insert preview before the input
    input.parentNode.insertBefore(preview, input);
    
    // Update preview on color change
    input.addEventListener('input', function() {
      preview.style.backgroundColor = this.value;
    });
  });
  
  // Comment approval handling
  const approveButtons = document.querySelectorAll('.approve-comment-btn');
  
  approveButtons.forEach(button => {
    button.addEventListener('click', function() {
      const commentId = this.getAttribute('data-comment-id');
      const form = document.querySelector(`#approve-comment-form-${commentId}`);
      
      if (form) {
        form.submit();
      }
    });
  });
  
  // Media library integration for article editor
  const mediaLibraryBtn = document.querySelector('#media-library-btn');
  const mediaLibraryModal = document.querySelector('#media-library-modal');
  
  if (mediaLibraryBtn && mediaLibraryModal) {
    mediaLibraryBtn.addEventListener('click', function(e) {
      e.preventDefault();
      
      // Display modal
      mediaLibraryModal.style.display = 'block';
      
      // Load media items via AJAX (in a real app)
      // For this example, we'll assume the media items are already in the modal
    });
    
    // Close modal when clicking the close button
    const closeBtn = mediaLibraryModal.querySelector('.close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function() {
        mediaLibraryModal.style.display = 'none';
      });
    }
    
    // Close modal when clicking outside of it
    window.addEventListener('click', function(e) {
      if (e.target === mediaLibraryModal) {
        mediaLibraryModal.style.display = 'none';
      }
    });
    
    // Handle media item selection
    const mediaItems = mediaLibraryModal.querySelectorAll('.media-item');
    
    mediaItems.forEach(item => {
      item.addEventListener('click', function() {
        const mediaUrl = this.getAttribute('data-url');
        
        // Select the media item (add selected class)
        mediaItems.forEach(i => i.classList.remove('selected'));
        this.classList.add('selected');
        
        // Update a hidden input with the selected URL, if needed
        const selectedMediaInput = document.querySelector('#selected_media');
        if (selectedMediaInput) {
          selectedMediaInput.value = mediaUrl;
        }
      });
    });
    
    // Insert selected media into editor
    const insertMediaBtn = mediaLibraryModal.querySelector('#insert-media-btn');
    
    if (insertMediaBtn) {
      insertMediaBtn.addEventListener('click', function() {
        const selectedItem = mediaLibraryModal.querySelector('.media-item.selected');
        
        if (selectedItem) {
          const mediaUrl = selectedItem.getAttribute('data-url');
          const mediaType = selectedItem.getAttribute('data-type');
          
          // If TinyMCE is available, insert into the editor
          if (tinymce && tinymce.activeEditor) {
            if (mediaType === 'image') {
              tinymce.activeEditor.execCommand('mceInsertContent', false, `<img src="${mediaUrl}" alt="Media" />`);
            } else {
              tinymce.activeEditor.execCommand('mceInsertContent', false, `<a href="${mediaUrl}" target="_blank">Download File</a>`);
            }
          }
          
          // Close the modal
          mediaLibraryModal.style.display = 'none';
        } else {
          alert('Please select a media item first.');
        }
      });
    }
  }
  
  // Bulk actions in tables
  const bulkActionSelect = document.querySelector('#bulk-action');
  const bulkApplyBtn = document.querySelector('#apply-bulk-action');
  const checkAllBox = document.querySelector('#check-all');
  
  if (bulkActionSelect && bulkApplyBtn && checkAllBox) {
    // Check/uncheck all items
    checkAllBox.addEventListener('change', function() {
      const checkboxes = document.querySelectorAll('.item-checkbox');
      
      checkboxes.forEach(checkbox => {
        checkbox.checked = this.checked;
      });
    });
    
    // Apply bulk action
    bulkApplyBtn.addEventListener('click', function() {
      const action = bulkActionSelect.value;
      
      if (!action) {
        alert('Please select an action.');
        return;
      }
      
      const selectedItems = Array.from(document.querySelectorAll('.item-checkbox:checked'))
        .map(checkbox => checkbox.value);
      
      if (selectedItems.length === 0) {
        alert('Please select at least one item.');
        return;
      }
      
      // Confirm the action
      if (confirm(`Are you sure you want to ${action} the selected items?`)) {
        // Submit the form for processing
        const bulkForm = document.querySelector('#bulk-action-form');
        
        if (bulkForm) {
          // Create hidden inputs for the selected items
          selectedItems.forEach(item => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'items[]';
            input.value = item;
            bulkForm.appendChild(input);
          });
          
          bulkForm.submit();
        }
      }
    });
  }
  
  // Stats charts for dashboard (if Chart.js is available)
  const statsCanvas = document.querySelector('#stats-chart');
  
  if (window.Chart && statsCanvas) {
    // Sample data - in a real application, this would come from the server
    const statsData = {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [{
        label: 'Views',
        backgroundColor: 'rgba(211, 47, 47, 0.2)',
        borderColor: 'rgba(211, 47, 47, 1)',
        borderWidth: 2,
        data: [150, 220, 180, 270, 320, 250, 300]
      }]
    };
    
    new Chart(statsCanvas, {
      type: 'line',
      data: statsData,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }
  
  // Settings form color preview
  const colorSettings = document.querySelectorAll('.color-setting');
  
  colorSettings.forEach(setting => {
    const input = setting.querySelector('input[type="text"]');
    const preview = setting.querySelector('.color-preview');
    
    if (input && preview) {
      // Initial preview
      preview.style.backgroundColor = input.value;
      
      // Update preview on input change
      input.addEventListener('input', function() {
        preview.style.backgroundColor = this.value;
      });
    }
  });
  
  // Date and time pickers for scheduling
  const dateTimeInputs = document.querySelectorAll('.datetime-picker');
  
  dateTimeInputs.forEach(input => {
    // In a real application, you would initialize a date picker library here
    // For example: flatpickr, bootstrap-datepicker, etc.
    
    // For this example, we'll just add some basic functionality
    input.addEventListener('focus', function() {
      this.type = 'datetime-local';
    });
    
    input.addEventListener('blur', function() {
      if (!this.value) {
        this.type = 'text';
      }
    });
  });
});
