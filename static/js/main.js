document.addEventListener('DOMContentLoaded', function() {
  // Mobile menu toggle with animation
  const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
  const mainNav = document.querySelector('.main-nav');
  
  if (mobileMenuToggle && mainNav) {
    mobileMenuToggle.addEventListener('click', function() {
      this.classList.toggle('active');
      mainNav.classList.toggle('active');
      
      // Handle the dropdown menus in mobile view
      const dropdowns = document.querySelectorAll('.dropdown');
      dropdowns.forEach(dropdown => {
        const link = dropdown.querySelector('a');
        const submenu = dropdown.querySelector('.dropdown-menu');
        
        if (!link.dataset.hasListener) {
          link.addEventListener('click', function(e) {
            // Only prevent default in mobile view
            if (window.innerWidth <= 768) {
              e.preventDefault();
              dropdown.classList.toggle('active');
              
              // Create ripple effect
              const rect = link.getBoundingClientRect();
              const ripple = document.createElement('span');
              ripple.className = 'ripple-effect';
              ripple.style.left = `${e.clientX - rect.left}px`;
              ripple.style.top = `${e.clientY - rect.top}px`;
              link.appendChild(ripple);
              
              // Remove ripple after animation completes
              setTimeout(() => ripple.remove(), 600);
            }
          });
          link.dataset.hasListener = 'true';
        }
      });
    });
  }
  
  // Add subtle bounce animation to nav items on page load
  const navItems = document.querySelectorAll('.main-nav > ul > li');
  navItems.forEach((item, index) => {
    setTimeout(() => {
      item.style.animation = 'navItemBounce 0.5s forwards';
    }, 100 * index);
  });
  
  // Add hover animation for desktop navigation
  if (window.innerWidth > 768) {
    navItems.forEach(item => {
      item.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-3px)';
      });
      
      item.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
      });
    });
  }
  
  // Comment reply functionality
  const replyLinks = document.querySelectorAll('.comment-reply-link');
  
  replyLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const commentId = this.getAttribute('data-comment-id');
      const replyForm = document.querySelector(`.reply-form[data-parent-id="${commentId}"]`);
      
      // Hide any other active reply forms
      document.querySelectorAll('.reply-form.active').forEach(form => {
        if (form !== replyForm) {
          form.classList.remove('active');
        }
      });
      
      // Toggle this reply form
      replyForm.classList.toggle('active');
      
      // Set the parent_id value in the form
      const parentIdInput = replyForm.querySelector('input[name="parent_id"]');
      if (parentIdInput) {
        parentIdInput.value = commentId;
      }
    });
  });
  
  // Social sharing buttons
  const shareButtons = document.querySelectorAll('.share-button');
  
  shareButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      
      const platform = this.getAttribute('data-platform');
      const url = encodeURIComponent(window.location.href);
      const title = encodeURIComponent(document.title);
      
      let shareUrl = '';
      
      switch(platform) {
        case 'facebook':
          shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
          break;
        case 'twitter':
          shareUrl = `https://twitter.com/intent/tweet?url=${url}&text=${title}`;
          break;
        case 'linkedin':
          shareUrl = `https://www.linkedin.com/shareArticle?mini=true&url=${url}&title=${title}`;
          break;
        case 'email':
          shareUrl = `mailto:?subject=${title}&body=${url}`;
          break;
      }
      
      if (shareUrl) {
        window.open(shareUrl, '_blank', 'width=600,height=400');
      }
    });
  });
  
  // Lazy load images
  const lazyImages = document.querySelectorAll('img[data-src]');
  
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
          imageObserver.unobserve(img);
        }
      });
    });
    
    lazyImages.forEach(img => {
      imageObserver.observe(img);
    });
  } else {
    // Fallback for browsers without IntersectionObserver
    lazyImages.forEach(img => {
      img.src = img.dataset.src;
      img.removeAttribute('data-src');
    });
  }
  
  // Flash messages auto-close
  const flashMessages = document.querySelectorAll('.alert');
  
  flashMessages.forEach(message => {
    setTimeout(() => {
      message.style.opacity = '0';
      setTimeout(() => {
        message.remove();
      }, 500);
    }, 5000);
  });
  
  // Article card hover effect
  const articleCards = document.querySelectorAll('.article-card');
  
  articleCards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.querySelector('.article-image img').style.transform = 'scale(1.05)';
    });
    
    card.addEventListener('mouseleave', function() {
      this.querySelector('.article-image img').style.transform = 'scale(1)';
    });
  });
  
  // Sticky header behavior
  const header = document.querySelector('.site-header');
  let lastScrollTop = 0;
  
  window.addEventListener('scroll', function() {
    let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    if (scrollTop > lastScrollTop && scrollTop > 200) {
      // Scrolling down, hide header
      header.style.transform = 'translateY(-100%)';
    } else {
      // Scrolling up, show header
      header.style.transform = 'translateY(0)';
    }
    
    lastScrollTop = scrollTop;
  });
  
  // Search form validation
  const searchForm = document.querySelector('.search-form');
  
  if (searchForm) {
    searchForm.addEventListener('submit', function(e) {
      const searchInput = this.querySelector('input[name="query"]');
      
      if (!searchInput.value.trim()) {
        e.preventDefault();
        searchInput.classList.add('is-invalid');
      } else {
        searchInput.classList.remove('is-invalid');
      }
    });
  }
  
  // Apply custom theme colors if available
  const applyCustomColors = () => {
    const root = document.documentElement;
    
    // Check if theme colors are available in the page
    const themeColors = window.themeColors;
    
    if (themeColors) {
      if (themeColors.primaryColor) {
        root.style.setProperty('--primary-color', themeColors.primaryColor);
      }
      if (themeColors.secondaryColor) {
        root.style.setProperty('--secondary-color', themeColors.secondaryColor);
      }
      if (themeColors.accentColor) {
        root.style.setProperty('--accent-color', themeColors.accentColor);
      }
      if (themeColors.textColor) {
        root.style.setProperty('--text-color', themeColors.textColor);
      }
      if (themeColors.linkColor) {
        root.style.setProperty('--link-color', themeColors.linkColor);
      }
    }
  };
  
  applyCustomColors();
});
