import { defineConfig, presetAttributify, presetUno, presetIcons } from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons(),
  ],
  shortcuts: {
    // Card shortcuts
    'strategy-card': 'bg-[rgba(26,39,68,0.8)] border border-[#2A3F5F] rounded-lg p-6 m-4 transition-all duration-300 text-left hover:translate-y-[-5px] hover:shadow-lg hover:border-[#00FFFF]',
    'info-card': 'bg-[rgba(26,39,68,0.8)] border border-[#2A3F5F] border-l-4 border-l-[#00FFFF] rounded-md p-6 my-4 text-left',
    'info-card-warning': 'border-l-[#FF4444]!',
    'info-card-success': 'border-l-[#00FF88]!',

    // Text shortcuts
    'page-title': 'text-[#FFD700]',
    'page-description': 'text-[#B0C4DE] text-lg',
    'section-title': 'text-xl',
    'subsection-title': 'text-lg text-[#00FFFF]',
    'content-text': 'text-[#B0C4DE] text-base leading-relaxed',
    'hero-title': 'text-4xl bg-gradient-to-br from-[#FFD700] to-white bg-clip-text text-transparent',

    // Layout shortcuts
    'grid-two-col': 'grid grid-cols-2 gap-6',
    'grid-three-col': 'grid grid-cols-3 gap-6',
    'grid-auto': 'grid grid-cols-[repeat(auto-fit,minmax(250px,1fr))] gap-6',
  },
  theme: {
    colors: {
      'neon-yellow': '#FFD700',
      'neon-cyan': '#00FFFF',
      'electric-blue': '#0080FF',
      'navy-dark': '#0A1628',
      'navy-medium': '#1A2744',
      'navy-light': '#2A3F5F',
      'accent-gold': '#FFA500',
      'warning-red': '#FF4444',
      'success-green': '#00FF88',
      'text-primary': '#FFFFFF',
      'text-secondary': '#B0C4DE',
      'text-muted': '#708090',
    },
  },
})
