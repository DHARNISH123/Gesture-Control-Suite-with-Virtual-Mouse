particlesJS('particles-js', {
  particles: {
    number: { value: 80 },
    color: { value: '#ffffff' },
    shape: { type: 'circle' },
    opacity: { value: 0.4 },
    size: { value: 3 },
    line_linked: {
      enable: true,
      distance: 120,
      color: '#ffffff',
      opacity: 0.4,
      width: 1
    },
    move: { enable: true, speed: 2 }
  },
  interactivity: {
    events: {
      onhover: { enable: true, mode: 'repulse' }
    },
    modes: {
      repulse: { distance: 100 }
    }
  }
});
