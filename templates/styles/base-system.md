# Base Design System

Universal design tokens and patterns for professional web applications.

## Color Tokens

### Primary Colors
- **Primary**: #4B5FEA (Professional Blue)
- **Primary-Light**: #6B7FFF
- **Primary-Dark**: #3B4FD0
- **Primary-50**: #EEF0FE
- **Primary-100**: #D6DBFD
- **Primary-200**: #B5BFFC
- **Primary-500**: #4B5FEA
- **Primary-700**: #3B4FD0
- **Primary-900**: #2B3FB0

### Secondary Colors
- **Secondary**: #8B5CF6 (Purple Accent)
- **Secondary-Light**: #A78BFA
- **Secondary-Dark**: #7C3AED

### Semantic Colors
- **Success**: #10B981 (Green)
- **Success-Light**: #34D399
- **Success-Dark**: #059669
- **Warning**: #F59E0B (Amber)
- **Warning-Light**: #FBBF24
- **Warning-Dark**: #D97706
- **Error**: #EF4444 (Red)
- **Error-Light**: #F87171
- **Error-Dark**: #DC2626
- **Info**: #3B82F6 (Blue)
- **Info-Light**: #60A5FA
- **Info-Dark**: #2563EB

### Neutral/Gray Scale
- **Neutral-50**: #F9FAFB
- **Neutral-100**: #F3F4F6
- **Neutral-200**: #E5E7EB
- **Neutral-300**: #D1D5DB
- **Neutral-400**: #9CA3AF
- **Neutral-500**: #6B7280
- **Neutral-600**: #4B5563
- **Neutral-700**: #374151
- **Neutral-800**: #1F2937
- **Neutral-900**: #111827

### Background Colors
- **BG-Base**: #FFFFFF (White)
- **BG-Subtle**: #F9FAFB (Neutral-50)
- **BG-Muted**: #F3F4F6 (Neutral-100)
- **BG-Dark**: #111827 (Neutral-900)

## Typography Scale

### Font Families
- **Sans**: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif
- **Mono**: "JetBrains Mono", "Fira Code", "Courier New", monospace

### Headings
- **H1**: 2rem (32px) / font-bold / line-height: 1.2 / letter-spacing: -0.02em
- **H2**: 1.625rem (26px) / font-semibold / line-height: 1.3 / letter-spacing: -0.01em
- **H3**: 1.375rem (22px) / font-semibold / line-height: 1.4
- **H4**: 1.125rem (18px) / font-medium / line-height: 1.5

### Body Text
- **Body-Large**: 1.125rem (18px) / font-normal / line-height: 1.6
- **Body**: 1rem (16px) / font-normal / line-height: 1.5
- **Body-Small**: 0.875rem (14px) / font-normal / line-height: 1.5
- **Caption**: 0.75rem (12px) / font-normal / line-height: 1.4

### Font Weights
- **Light**: 300
- **Normal**: 400
- **Medium**: 500
- **Semibold**: 600
- **Bold**: 700

## Spacing System

Based on 4px base unit for consistent rhythm.

- **xs**: 4px (0.25rem)
- **sm**: 8px (0.5rem)
- **md**: 12px (0.75rem)
- **lg**: 16px (1rem)
- **xl**: 24px (1.5rem)
- **2xl**: 32px (2rem)
- **3xl**: 48px (3rem)
- **4xl**: 64px (4rem)
- **5xl**: 96px (6rem)

## Border Radius

- **none**: 0px
- **sm**: 4px (0.25rem)
- **md**: 6px (0.375rem)
- **lg**: 8px (0.5rem)
- **xl**: 12px (0.75rem)
- **2xl**: 16px (1rem)
- **full**: 9999px (circular)

## Shadows

- **sm**: 0 1px 2px 0 rgba(0, 0, 0, 0.05)
- **md**: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)
- **lg**: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)
- **xl**: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)
- **2xl**: 0 25px 50px -12px rgba(0, 0, 0, 0.25)
- **inner**: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)

## Component Patterns

### Card
```
Base: bg-white rounded-lg shadow-sm border border-neutral-200 p-6
Hover: hover:shadow-md transition-shadow duration-200
```

### Button
```
Primary: bg-primary text-white rounded-md px-4 py-2 font-medium hover:bg-primary-dark transition-colors
Secondary: bg-neutral-200 text-neutral-900 rounded-md px-4 py-2 font-medium hover:bg-neutral-300
Outline: border-2 border-primary text-primary rounded-md px-4 py-2 font-medium hover:bg-primary-50
Ghost: text-neutral-700 hover:bg-neutral-100 rounded-md px-4 py-2 font-medium
Disabled: opacity-50 cursor-not-allowed
Sizes: sm (px-3 py-1.5 text-sm), md (px-4 py-2), lg (px-6 py-3 text-lg)
```

### Input
```
Base: rounded-md border border-neutral-300 px-3 py-2 text-neutral-900 placeholder:text-neutral-400
Focus: focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
Error: border-error focus:ring-error
Disabled: bg-neutral-100 cursor-not-allowed opacity-60
```

### Badge
```
Base: inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
Success: bg-success-100 text-success-800
Warning: bg-warning-100 text-warning-800
Error: bg-error-100 text-error-800
Info: bg-info-100 text-info-800
Neutral: bg-neutral-100 text-neutral-800
```

### Alert
```
Base: rounded-lg border p-4 flex gap-3 items-start
Success: bg-success-50 border-success-200 text-success-900
Warning: bg-warning-50 border-warning-200 text-warning-900
Error: bg-error-50 border-error-200 text-error-900
Info: bg-info-50 border-info-200 text-info-900
```

### Navigation
```
Header: bg-white border-b border-neutral-200 h-16 px-6 flex items-center justify-between sticky top-0 z-50
Nav Link: text-neutral-600 hover:text-neutral-900 px-3 py-2 rounded-md hover:bg-neutral-50
Active: text-primary bg-primary-50 font-medium
```

### Table
```
Table: w-full border-collapse
Header: bg-neutral-50 border-b-2 border-neutral-200 text-left font-semibold text-neutral-700 px-4 py-3
Row: border-b border-neutral-200 hover:bg-neutral-50
Cell: px-4 py-3 text-neutral-900
Striped: odd:bg-white even:bg-neutral-50
```

### Modal/Dialog
```
Overlay: fixed inset-0 bg-neutral-900/50 backdrop-blur-sm z-50
Container: bg-white rounded-xl shadow-2xl max-w-lg mx-auto mt-20 p-6
Header: text-xl font-semibold text-neutral-900 mb-4
Footer: flex gap-3 justify-end mt-6 pt-4 border-t border-neutral-200
```

## Animation & Transitions

### Durations
- **Fast**: 150ms (micro-interactions)
- **Base**: 200ms (standard transitions)
- **Slow**: 300ms (complex animations)
- **Slower**: 500ms (page transitions)

### Easing Functions
- **Ease-In**: cubic-bezier(0.4, 0, 1, 1)
- **Ease-Out**: cubic-bezier(0, 0, 0.2, 1)
- **Ease-In-Out**: cubic-bezier(0.4, 0, 0.2, 1)

### Common Transitions
```
Standard: transition-all duration-200 ease-out
Colors: transition-colors duration-200
Opacity: transition-opacity duration-150
Transform: transition-transform duration-200 ease-out
Shadow: transition-shadow duration-200
```

## Layout Patterns

### Container
```
Max Width: max-w-7xl mx-auto px-4 sm:px-6 lg:px-8
Narrow: max-w-3xl mx-auto px-4
Wide: max-w-full px-8
```

### Grid
```
Responsive: grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6
Dense: grid grid-cols-12 gap-4
```

### Flexbox
```
Center: flex items-center justify-center
Between: flex items-center justify-between
Stack: flex flex-col gap-4
Wrap: flex flex-wrap gap-4
```

## Responsive Breakpoints

- **sm**: 640px (mobile landscape)
- **md**: 768px (tablet)
- **lg**: 1024px (desktop)
- **xl**: 1280px (large desktop)
- **2xl**: 1536px (extra large)

## Dark Mode Support

### Dark Mode Colors
- **BG-Base-Dark**: #0F172A (Slate-900)
- **BG-Subtle-Dark**: #1E293B (Slate-800)
- **BG-Muted-Dark**: #334155 (Slate-700)
- **Text-Dark**: #F1F5F9 (Slate-100)
- **Text-Muted-Dark**: #94A3B8 (Slate-400)

### Dark Mode Usage
```
bg-white dark:bg-slate-900
text-neutral-900 dark:text-slate-100
border-neutral-200 dark:border-slate-700
```

## Accessibility Guidelines

### Color Contrast
- **Normal Text**: Minimum 4.5:1 contrast ratio
- **Large Text** (18px+ or 14px+ bold): Minimum 3:1 contrast ratio
- **UI Components**: Minimum 3:1 contrast ratio

### Focus States
- Always provide visible focus indicators
- Use `focus:ring-2 focus:ring-primary focus:outline-none`
- Ensure focus is never removed without alternative indicator

### Interactive Elements
- Minimum touch target: 44x44px (mobile)
- Clear hover/active states
- Disabled state clearly distinguishable

### Semantic HTML
- Use proper heading hierarchy (h1 → h2 → h3)
- Use semantic elements (nav, main, article, section)
- Provide alt text for images
- Use proper ARIA labels when needed

## Usage Guidelines

### When to Use This System
- Starting a new project without specific branding
- Need professional, neutral design quickly
- Building internal tools or prototypes
- Foundation for custom design systems

### Customization
This base system is designed to be extended. Override color tokens and component patterns as needed while maintaining structural consistency.

### Naming Conventions
- Use semantic names (primary, success, error) over descriptive (blue, green, red)
- Follow BEM-like patterns for custom components
- Prefix custom tokens to avoid conflicts

## Tailwind Config Integration

This design system maps directly to Tailwind CSS configuration:

```js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#4B5FEA',
          light: '#6B7FFF',
          dark: '#3B4FD0',
          50: '#EEF0FE',
          100: '#D6DBFD',
          // ... etc
        },
        // ... all color tokens
      },
      fontSize: {
        // Typography scale
      },
      spacing: {
        // Spacing system
      },
      borderRadius: {
        // Border radius tokens
      },
      boxShadow: {
        // Shadow tokens
      }
    }
  }
}
```
