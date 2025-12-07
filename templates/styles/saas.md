# SaaS Application Design System

Specialized design system for SaaS products, web applications, and subscription-based services.

**Extends**: base-system.md

## Project Type Identification

Use this template when `project_type` includes:
- `saas_application`
- `web_app`
- `subscription_service`
- `platform`
- `tool`

## Color Extensions

### Brand Colors

Strong, confident colors for SaaS products:

- **Brand-Primary**: #6366F1 (Indigo)
- **Brand-Primary-Light**: #818CF8
- **Brand-Primary-Dark**: #4F46E5
- **Brand-Secondary**: #EC4899 (Pink)
- **Brand-Secondary-Light**: #F472B6
- **Brand-Secondary-Dark**: #DB2777

### Call-to-Action Colors

Optimized for conversions:

- **CTA-Primary**: #10B981 (Green - signup, subscribe, upgrade)
- **CTA-Secondary**: #6366F1 (Indigo - learn more, try demo)
- **CTA-Destructive**: #EF4444 (Red - cancel, delete, downgrade)

### Feature Colors

For highlighting different features/tiers:

- **Feature-Free**: #6B7280 (Gray)
- **Feature-Starter**: #3B82F6 (Blue)
- **Feature-Professional**: #8B5CF6 (Purple)
- **Feature-Enterprise**: #0F172A (Dark/Premium)

## Marketing & Landing Page Components

### Hero Section

```
Container: relative overflow-hidden bg-gradient-to-br from-brand-primary to-brand-secondary
Content: max-w-7xl mx-auto px-4 py-20 lg:py-32
Heading: text-4xl lg:text-6xl font-bold text-white mb-6 leading-tight
Subheading: text-xl lg:text-2xl text-white/90 mb-8 max-w-3xl
CTA Group: flex gap-4 flex-wrap
  Primary CTA: bg-cta-primary text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-cta-primary/90 shadow-xl
  Secondary CTA: bg-white/10 text-white border-2 border-white px-8 py-4 rounded-lg backdrop-blur-sm hover:bg-white/20
```

### Feature Card

```
Container: bg-white rounded-xl border border-neutral-200 p-8 hover:shadow-lg transition-shadow
Icon Container: w-12 h-12 rounded-lg bg-brand-primary/10 flex items-center justify-center mb-4
  Icon: w-6 h-6 text-brand-primary
Title: text-xl font-semibold text-neutral-900 mb-2
Description: text-neutral-600 leading-relaxed
Learn More: text-brand-primary font-medium hover:text-brand-primary-dark mt-4 inline-flex items-center gap-1
```

### Pricing Card

```
Container: bg-white rounded-xl border-2 border-neutral-200 p-8 hover:scale-105 transition-transform
Featured: border-brand-primary shadow-xl relative
  Badge: absolute -top-4 left-1/2 -translate-x-1/2 bg-brand-primary text-white px-4 py-1 rounded-full text-sm font-medium
Plan Name: text-2xl font-bold text-neutral-900 mb-2
Price: text-5xl font-bold text-neutral-900 mb-1
  Currency: text-2xl font-semibold text-neutral-600
  Period: text-lg text-neutral-600 font-normal
Description: text-neutral-600 mb-6
Feature List: space-y-3 mb-8
  Feature: flex items-start gap-2
    Icon: w-5 h-5 text-cta-primary (checkmark)
    Text: text-neutral-700
CTA Button: w-full bg-cta-primary text-white py-3 rounded-lg font-semibold hover:bg-cta-primary/90
  Featured: bg-brand-primary hover:bg-brand-primary-dark
```

### Social Proof Section

```
Container: bg-neutral-50 py-12 px-4
Title: text-center text-sm font-semibold text-neutral-600 uppercase tracking-wide mb-8
Logo Grid: grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-8 items-center
  Logo: grayscale opacity-60 hover:opacity-100 hover:grayscale-0 transition-all
```

### Testimonial Card

```
Container: bg-white rounded-xl border border-neutral-200 p-6 shadow-sm
Quote: text-neutral-700 leading-relaxed mb-4 text-lg
  Quote Marks: text-brand-primary text-4xl font-serif
Author Section: flex items-center gap-3
  Avatar: w-12 h-12 rounded-full bg-neutral-200
  Name: font-semibold text-neutral-900
  Title: text-sm text-neutral-600
Rating: flex gap-1 text-warning mb-3
  Star: ★ (filled stars)
```

## Application Components

### App Header/Navigation

```
Container: bg-white border-b border-neutral-200 sticky top-0 z-50 backdrop-blur-sm bg-white/95
Content: max-w-7xl mx-auto px-4 h-16 flex items-center justify-between
Logo: font-bold text-xl text-brand-primary
Nav Links: hidden lg:flex gap-6
  Link: text-neutral-600 hover:text-neutral-900 font-medium transition-colors
  Active: text-brand-primary font-semibold
Actions: flex items-center gap-3
  Login: text-neutral-700 hover:text-neutral-900 font-medium
  Signup: bg-brand-primary text-white px-4 py-2 rounded-lg font-medium hover:bg-brand-primary-dark
Mobile Menu: lg:hidden
```

### Sidebar Navigation

```
Container: w-64 bg-white border-r border-neutral-200 h-screen sticky top-0 flex flex-col
Header: p-4 border-b border-neutral-200
  Logo: font-bold text-xl text-brand-primary
Nav: flex-1 py-4 overflow-y-auto
  Section: px-3 mb-6
    Heading: text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-2 px-3
    Links: space-y-1
      Link: flex items-center gap-3 px-3 py-2 rounded-lg text-neutral-700 hover:bg-neutral-100 transition-colors
        Icon: w-5 h-5
        Text: font-medium
      Active: bg-brand-primary/10 text-brand-primary font-semibold
Footer: p-4 border-t border-neutral-200
  User Profile: flex items-center gap-3 p-2 rounded-lg hover:bg-neutral-50
```

### Settings Panel

```
Container: max-w-4xl mx-auto py-8 px-4
Header: mb-8
  Title: text-3xl font-bold text-neutral-900 mb-2
  Description: text-neutral-600
Sections: space-y-8
  Section: bg-white rounded-lg border border-neutral-200 p-6
    Section Title: text-xl font-semibold text-neutral-900 mb-4 pb-4 border-b border-neutral-200
    Setting Row: flex items-center justify-between py-4 border-b border-neutral-100 last:border-0
      Label: flex-1
        Title: font-medium text-neutral-900
        Description: text-sm text-neutral-600 mt-1
      Control: Toggle/Select/Input
```

### Notification Toast

```
Container: fixed bottom-4 right-4 z-50 bg-white rounded-lg shadow-2xl border border-neutral-200 p-4 max-w-sm
  Success: border-l-4 border-cta-primary
  Error: border-l-4 border-error
  Info: border-l-4 border-info
Content: flex gap-3 items-start
  Icon: w-5 h-5 flex-shrink-0
    Success: text-cta-primary
    Error: text-error
    Info: text-info
  Text: flex-1
    Title: font-semibold text-neutral-900 mb-1
    Message: text-sm text-neutral-600
  Close: text-neutral-400 hover:text-neutral-600
```

### Empty State (Onboarding)

```
Container: flex flex-col items-center justify-center min-h-[400px] text-center p-8
Illustration: w-64 h-64 mb-6 (SVG/image)
Title: text-2xl font-bold text-neutral-900 mb-2
Description: text-neutral-600 max-w-md mb-6
CTA: bg-brand-primary text-white px-6 py-3 rounded-lg font-semibold hover:bg-brand-primary-dark
Secondary Action: text-brand-primary hover:text-brand-primary-dark font-medium mt-3
```

## Form Components

### Form Layout

```
Container: space-y-6
Form Group: space-y-2
  Label: block text-sm font-medium text-neutral-900 mb-1
  Input: w-full rounded-lg border border-neutral-300 px-4 py-3 focus:border-brand-primary focus:ring-2 focus:ring-brand-primary/20
  Helper Text: text-sm text-neutral-600 mt-1
  Error Text: text-sm text-error mt-1 flex items-center gap-1
    Icon: w-4 h-4
```

### Multi-Step Form

```
Progress Bar: mb-8
  Steps: flex justify-between
    Step: flex-1 relative
      Number: w-8 h-8 rounded-full border-2 bg-white flex items-center justify-center font-semibold
        Active: border-brand-primary text-brand-primary
        Complete: bg-brand-primary text-white border-brand-primary
        Inactive: border-neutral-300 text-neutral-400
      Label: text-sm font-medium mt-2
      Connector: h-0.5 bg-neutral-200 absolute top-4 left-1/2 w-full
        Complete: bg-brand-primary
```

### Toggle Switch

```
Container: relative inline-flex h-6 w-11 items-center rounded-full transition-colors
  Off: bg-neutral-300
  On: bg-brand-primary
Knob: inline-block h-4 w-4 rounded-full bg-white transition-transform
  Off: translate-x-1
  On: translate-x-6
```

## Dashboard Components for SaaS

### Stat Widget

```
Container: bg-white rounded-lg border border-neutral-200 p-6
Label: text-sm font-medium text-neutral-600 mb-1
Value: text-3xl font-bold text-neutral-900 mb-2
Change: flex items-center gap-1 text-sm
  Positive: text-cta-primary
  Negative: text-error
Sparkline: mt-4 h-12 (mini line chart)
```

### Activity Feed

```
Container: bg-white rounded-lg border border-neutral-200
Header: p-4 border-b border-neutral-200
  Title: font-semibold text-neutral-900
Items: divide-y divide-neutral-100
  Item: p-4 hover:bg-neutral-50 transition-colors
    Time: text-xs text-neutral-500 mb-1
    Content: text-sm text-neutral-700
    User: flex items-center gap-2 mt-2
      Avatar: w-6 h-6 rounded-full bg-neutral-200
      Name: text-sm font-medium text-neutral-900
```

### Integration Card

```
Container: bg-white rounded-lg border border-neutral-200 p-6 flex items-center gap-4
Logo: w-12 h-12 rounded-lg bg-neutral-100 p-2
Info: flex-1
  Name: font-semibold text-neutral-900 mb-1
  Description: text-sm text-neutral-600
Status: flex items-center gap-2 text-sm
  Connected: text-cta-primary font-medium
    Indicator: w-2 h-2 rounded-full bg-cta-primary
  Disconnected: text-neutral-500
Action Button: text-sm font-medium text-brand-primary hover:text-brand-primary-dark
```

## Onboarding & Guides

### Checklist

```
Container: bg-white rounded-lg border border-neutral-200 p-6
Title: font-semibold text-neutral-900 mb-1
Progress: text-sm text-neutral-600 mb-4
Items: space-y-3
  Item: flex items-start gap-3 p-3 rounded-lg hover:bg-neutral-50 cursor-pointer
    Checkbox: w-5 h-5 rounded border-2 flex items-center justify-center
      Unchecked: border-neutral-300
      Checked: bg-cta-primary border-cta-primary text-white
    Content: flex-1
      Title: font-medium text-neutral-900
      Description: text-sm text-neutral-600 mt-0.5
```

### Tooltip

```
Container: absolute z-50 bg-neutral-900 text-white text-sm rounded-lg px-3 py-2 shadow-xl max-w-xs
Arrow: Pointing to trigger element
```

### Banner Notification

```
Container: bg-brand-primary text-white py-3 px-4 flex items-center justify-between
Message: flex items-center gap-3 flex-1
  Icon: w-5 h-5
  Text: font-medium
Action: bg-white/20 hover:bg-white/30 px-4 py-1.5 rounded-md font-medium transition-colors
Dismiss: text-white/80 hover:text-white
```

## Responsive Behavior

### Mobile (< 768px)

```
Hero: Single column, reduced padding
Pricing: Stack cards vertically
Navigation: Hamburger menu with slide-out drawer
Sidebar: Hidden, hamburger menu instead
Forms: Full width inputs, larger touch targets
```

### Tablet (768px - 1024px)

```
Features: 2-column grid
Pricing: 2-3 cards per row
Sidebar: Collapsible with icon-only mode
```

### Desktop (> 1024px)

```
Features: 3-4 column grid
Pricing: All cards in single row (up to 4)
Full sidebar navigation
Hover effects enabled
```

## Animation & Microinteractions

### Page Transitions

```
Enter: opacity-0 → opacity-100, translateY(10px) → translateY(0) over 300ms
Exit: opacity-100 → opacity-0, scale(1) → scale(0.95) over 200ms
```

### Button Hover

```
Scale: hover:scale-105
Shadow: hover:shadow-lg
Colors: Darken by 10%
Duration: 150ms ease-out
```

### Loading States

```
Skeleton: animate-pulse bg-gradient-to-r from-neutral-200 via-neutral-100 to-neutral-200 bg-[length:200%_100%]
Spinner: border-4 border-neutral-200 border-t-brand-primary rounded-full w-8 h-8 animate-spin
Progress Bar: Indeterminate animation, bg-brand-primary
```

## Accessibility

### Focus States

```
All Interactive: focus:outline-none focus:ring-2 focus:ring-brand-primary focus:ring-offset-2
Buttons: focus-visible:ring-2
Links: focus-visible:underline underline-offset-4
```

### Color Contrast

- All text meets WCAG AA standards (4.5:1 minimum)
- Interactive elements meet 3:1 minimum
- Brand colors tested for accessibility

## Tailwind Config for SaaS

```js
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: {
          primary: '#6366F1',
          'primary-light': '#818CF8',
          'primary-dark': '#4F46E5',
          secondary: '#EC4899',
          'secondary-light': '#F472B6',
          'secondary-dark': '#DB2777',
        },
        cta: {
          primary: '#10B981',
          secondary: '#6366F1',
          destructive: '#EF4444',
        },
        feature: {
          free: '#6B7280',
          starter: '#3B82F6',
          professional: '#8B5CF6',
          enterprise: '#0F172A',
        }
      },
      animation: {
        'slide-in': 'slideIn 0.3s ease-out',
        'fade-in': 'fadeIn 0.3s ease-out',
      },
      keyframes: {
        slideIn: {
          '0%': { opacity: 0, transform: 'translateY(10px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        }
      }
    }
  }
}
```
