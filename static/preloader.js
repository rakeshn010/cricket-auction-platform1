/**
 * Preloader - Ensures backend data loads before showing frontend
 * Makes the site feel faster and more professional
 */

class Preloader {
  constructor() {
    this.loadingSteps = [
      'Connecting to server...',
      'Loading auction data...',
      'Preparing dashboard...',
      'Almost ready...'
    ];
    this.currentStep = 0;
    this.progressBar = null;
    this.textElement = null;
  }

  init() {
    // Add loading class to body
    document.body.classList.add('loading');
    
    // Get elements
    this.progressBar = document.querySelector('.preloader-progress-bar');
    this.textElement = document.querySelector('.preloader-subtext');
    
    // Start loading sequence
    this.updateProgress(0);
    this.startLoadingSequence();
  }

  startLoadingSequence() {
    // Update text every 500ms
    const textInterval = setInterval(() => {
      if (this.currentStep < this.loadingSteps.length) {
        this.textElement.textContent = this.loadingSteps[this.currentStep];
        this.currentStep++;
      }
    }, 500);

    // Wait for DOM and critical resources
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        this.onDOMReady(textInterval);
      });
    } else {
      this.onDOMReady(textInterval);
    }
  }

  onDOMReady(textInterval) {
    this.updateProgress(50);
    
    // Wait for all critical resources (images, CSS, JS)
    if (document.readyState === 'complete') {
      this.onFullyLoaded(textInterval);
    } else {
      window.addEventListener('load', () => {
        this.onFullyLoaded(textInterval);
      });
    }
  }

  onFullyLoaded(textInterval) {
    clearInterval(textInterval);
    this.updateProgress(100);
    
    // Small delay to ensure everything is ready
    setTimeout(() => {
      this.hide();
    }, 300);
  }

  updateProgress(percent) {
    if (this.progressBar) {
      this.progressBar.style.width = percent + '%';
    }
  }

  hide() {
    const preloader = document.getElementById('preloader');
    if (preloader) {
      // Fade out preloader
      preloader.classList.add('fade-out');
      
      // Remove loading class, add loaded class
      document.body.classList.remove('loading');
      document.body.classList.add('loaded');
      
      // Remove preloader from DOM after animation
      setTimeout(() => {
        preloader.remove();
      }, 500);
    }
  }
}

// Initialize preloader immediately
const preloader = new Preloader();
preloader.init();
