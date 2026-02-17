# Dashboard Design SOP

## Goal
Create a beautiful, brand-aligned interactive dashboard displaying AI news articles with modern aesthetics.

## Brand Design System

### Colors
```css
--primary: #A9A4C0;        /* Purple/lavender - accents, highlights */
--background: #010315;     /* Deep navy/black - main background */
--card-bg: #0a0a1f;        /* Slightly lighter for cards */
--text-primary: #ffffff;   /* White text on dark */
--text-secondary: #A9A4C0; /* Purple for secondary text */
--gradient-1: linear-gradient(135deg, #A9A4C0 0%, #ff6b6b 100%); /* Purple to coral */
--gradient-2: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* Purple gradient */
```

### Typography
- **Font Family:** SF Pro Display (fallback: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif)
- **H1:** 38px, bold
- **H2:** 54px, bold (for hero sections)
- **Body:** 18px, regular
- **Small:** 14px, regular

### Spacing
- **Base Unit:** 4px
- **Common Spacing:** 8px, 12px, 16px, 24px, 32px, 48px
- **Container Max Width:** 1200px

### Border Radius
- **Standard:** 15px (all cards, buttons)
- **Small:** 8px (badges, small elements)

## Component Structure

### 1. Header
- Logo (star/diamond shape) on left
- Title: "AI News Dashboard" (H1, 38px)
- Gradient underline or accent
- Sticky positioning on scroll

### 2. Stats Bar (Optional for Phase 1)
- Total articles count
- New articles (last 24h) count
- Source breakdown

### 3. Article Grid
- **Layout:** CSS Grid, 3 columns on desktop, 2 on tablet, 1 on mobile
- **Gap:** 24px between cards
- **Card Structure:**
  - Gradient background (subtle)
  - Source badge (top-left corner)
  - Title (bold, 20px)
  - Summary (if available, 16px, text-secondary)
  - Published date (14px, text-secondary)
  - "NEW" badge if < 24h old
  - Hover effect: lift + glow

### 4. Source Badges
- **Ben's Bites:** Purple gradient background
- **AI Rundown:** Orange/coral gradient background
- **Style:** Small pill shape, 8px radius, 12px text

### 5. "NEW" Badge
- Bright accent color (e.g., #00ff88 or #ff6b6b)
- Pulsing animation
- Position: Top-right of card

## Responsive Breakpoints
- **Mobile:** < 768px (1 column)
- **Tablet:** 768px - 1024px (2 columns)
- **Desktop:** > 1024px (3 columns)

## Animations
- **Card Hover:** 
  - Transform: translateY(-4px)
  - Box-shadow: 0 8px 24px rgba(169, 164, 192, 0.3)
  - Transition: 0.3s ease
- **NEW Badge:** Subtle pulse animation (scale 1 to 1.05)
- **Page Load:** Fade-in cards with stagger effect

## Accessibility
- Semantic HTML (header, main, article, section)
- ARIA labels for interactive elements
- Keyboard navigation support
- Sufficient color contrast (WCAG AA)

## SEO
- Title tag: "AI News Dashboard - Latest from Ben's Bites & AI Rundown"
- Meta description
- Proper heading hierarchy (single H1)
- Unique IDs for all interactive elements

## Design Inspiration Elements
Based on provided design reference:
- Dark background (#010315)
- Gradient cards with depth
- Modern card-based layout
- Professional, clean aesthetic
- Rounded corners (15px)
- Subtle shadows for depth
- Purple and orange/coral accent colors
