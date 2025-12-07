# Analytics Platform Design System

Specialized design system for data analytics platforms, dashboards, and business intelligence applications.

**Extends**: base-system.md

## Project Type Identification

Use this template when `project_type` includes:
- `data_analytics_platform`
- `dashboard`
- `business_intelligence`
- `reporting_tool`
- `metrics_platform`

## Color Extensions

### Data Visualization Colors

Primary data palette for charts, graphs, and visualizations:

- **Data-Primary**: #3B82F6 (Chart Blue)
- **Data-Secondary**: #10B981 (Chart Green)
- **Data-Tertiary**: #F59E0B (Chart Amber)
- **Data-Quaternary**: #8B5CF6 (Chart Purple)
- **Data-Quinary**: #EF4444 (Chart Red)
- **Data-Senary**: #06B6D4 (Chart Cyan)

### KPI & Metric Colors

Semantic colors for metrics and KPIs:

- **KPI-Positive**: #10B981 (Green - growth, increase, success)
- **KPI-Negative**: #EF4444 (Red - decline, decrease, error)
- **KPI-Neutral**: #6B7280 (Gray - no change, neutral)
- **KPI-Warning**: #F59E0B (Amber - threshold warning)

### Heatmap Colors

For heatmaps and intensity visualizations:

- **Heat-Cold**: #3B82F6 (Blue)
- **Heat-Cool**: #06B6D4 (Cyan)
- **Heat-Neutral**: #10B981 (Green)
- **Heat-Warm**: #F59E0B (Amber)
- **Heat-Hot**: #EF4444 (Red)

### Chart Background

- **Chart-BG**: #FFFFFF (White)
- **Chart-Grid**: #E5E7EB (Neutral-200)
- **Chart-Axis**: #9CA3AF (Neutral-400)

## Dashboard Components

### KPI Card

Large metric display with trend indicators:

```
Container: bg-white rounded-lg shadow-sm border border-neutral-200 p-6 hover:shadow-md transition-shadow
Label: text-sm font-medium text-neutral-600 uppercase tracking-wide mb-2
Value: text-3xl font-bold text-neutral-900 mb-1
Change: flex items-center gap-1 text-sm
  Positive: text-kpi-positive
  Negative: text-kpi-negative
  Neutral: text-kpi-neutral
Icon: w-12 h-12 rounded-full flex items-center justify-center mb-4
  Primary: bg-primary-100 text-primary-700
  Success: bg-success-100 text-success-700
  Warning: bg-warning-100 text-warning-700
```

### Chart Container

Wrapper for chart visualizations:

```
Container: bg-white rounded-lg shadow-sm border border-neutral-200 p-6
Header: flex items-center justify-between mb-4 pb-4 border-b border-neutral-200
Title: text-lg font-semibold text-neutral-900
Chart Area: min-h-[300px] lg:min-h-[400px]
```

### Stats Grid

Grid layout for multiple KPIs:

```
Grid: grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6
Compact: grid grid-cols-2 lg:grid-cols-4 gap-4
```

### Filter Panel

Controls for filtering dashboard data:

```
Container: bg-neutral-50 rounded-lg p-4 mb-6
Layout: flex flex-wrap gap-4 items-center
Label: text-sm font-medium text-neutral-700 mb-1
Select: rounded-md border-neutral-300 focus:border-primary focus:ring-primary
Date Range: flex gap-2 items-center
```

### Data Table

Tabular data display with sorting/filtering:

```
Container: bg-white rounded-lg shadow-sm border border-neutral-200 overflow-hidden
Table: w-full
Header: bg-neutral-50 border-b-2 border-neutral-200
  Cell: px-6 py-3 text-left text-xs font-semibold text-neutral-700 uppercase tracking-wider
Row: border-b border-neutral-200 hover:bg-neutral-50 transition-colors
  Cell: px-6 py-4 text-sm text-neutral-900
Striped: odd:bg-white even:bg-neutral-50
Sortable Header: cursor-pointer hover:bg-neutral-100 select-none
Pagination: flex items-center justify-between px-6 py-3 bg-neutral-50 border-t border-neutral-200
```

### Trend Indicator

Small component showing increase/decrease:

```
Container: inline-flex items-center gap-1 text-sm font-medium
Positive: text-kpi-positive
  Icon: ↑ (arrow-up) or ▲ (triangle-up)
Negative: text-kpi-negative
  Icon: ↓ (arrow-down) or ▼ (triangle-down)
Neutral: text-kpi-neutral
  Icon: → (arrow-right) or - (minus)
```

## Layout Patterns

### Dashboard Grid

Responsive grid for dashboard widgets:

```
Main Grid: grid grid-cols-1 lg:grid-cols-12 gap-6
KPI Row: lg:col-span-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6
Main Chart: lg:col-span-8
Sidebar: lg:col-span-4
Full Width: lg:col-span-12
Half Width: lg:col-span-6
Third Width: lg:col-span-4
```

### Sidebar Layout

Dashboard with filters/navigation sidebar:

```
Container: flex gap-6
Sidebar: w-64 flex-shrink-0 space-y-6
  Sticky: sticky top-20 self-start
Main: flex-1 min-w-0
```

### Two-Column Dashboard

Side-by-side comparison layout:

```
Grid: grid grid-cols-1 lg:grid-cols-2 gap-6
Equal Columns: Each chart/table gets 50% on desktop
```

## Chart Styling Guidelines

### Bar/Column Charts

```
Bar Fill: data-primary (blue)
Multiple Series: data-primary, data-secondary, data-tertiary
Hover: Lighten by 10%
Grid Lines: chart-grid color, 1px stroke
Axis Labels: text-sm text-neutral-600
```

### Line Charts

```
Line Stroke: data-primary, 2px width
Area Fill: data-primary with 20% opacity
Multiple Lines: Use data palette in order
Points: 4px radius on hover
Grid: Horizontal lines only (chart-grid)
```

### Pie/Donut Charts

```
Segments: Use full data palette (6 colors)
Hover: Scale up 1.05x
Labels: text-sm font-medium text-neutral-900
Percentages: text-xs text-neutral-600
```

### Heatmap

```
Cell: rounded-sm border border-white
Scale: heat-cold → heat-hot (5 steps)
Hover: border-2 border-neutral-900
Labels: text-xs font-medium
```

## Map Visualization

For geographic data visualization:

### Map Container

```
Container: bg-white rounded-lg shadow-sm border border-neutral-200 overflow-hidden
Map: min-h-[500px] lg:min-h-[600px] relative
Controls: absolute top-4 right-4 z-10 space-y-2
```

### Map Markers

```
Default: w-3 h-3 rounded-full bg-primary border-2 border-white shadow-md
Cluster: w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center font-bold text-sm
Hover: scale-110 shadow-lg transition-transform
Selected: w-4 h-4 bg-primary-dark border-4 border-primary-light
```

### Map Popup

```
Container: bg-white rounded-lg shadow-xl p-4 min-w-[200px] max-w-[300px]
Arrow: Pointing to marker location
Title: font-semibold text-neutral-900 mb-2
Content: text-sm text-neutral-700 space-y-1
Actions: flex gap-2 mt-3 pt-3 border-t border-neutral-200
```

### Map Legend

```
Container: bg-white rounded-lg shadow-md p-4 absolute bottom-4 left-4 z-10
Title: font-semibold text-neutral-900 mb-3 text-sm
Items: space-y-2
  Item: flex items-center gap-2 text-xs text-neutral-700
  Color: w-3 h-3 rounded-full
```

## Export & Actions

### Export Button

```
Primary: bg-primary text-white rounded-md px-4 py-2 font-medium hover:bg-primary-dark
  Icon: Download icon (↓)
Secondary: border border-neutral-300 text-neutral-700 rounded-md px-4 py-2 hover:bg-neutral-50
  Icon: Export/share icon
```

### Date Range Picker

```
Container: flex items-center gap-2 border border-neutral-300 rounded-md px-3 py-2 bg-white
Icon: Calendar icon (📅)
Text: text-sm text-neutral-900
Separator: text-neutral-400 mx-2 (-)
Dropdown: Absolute positioned below trigger
```

### Refresh Button

```
Button: text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100 rounded-md p-2
Icon: Refresh/reload icon (↻) with rotation animation on click
Auto-refresh Indicator: text-xs text-neutral-500 flex items-center gap-1
```

## Data States

### Loading State

```
Skeleton: animate-pulse bg-neutral-200 rounded
  KPI Card: h-32 rounded-lg
  Chart: h-80 rounded-lg
  Table Row: h-12 rounded
Spinner: border-4 border-neutral-200 border-t-primary rounded-full w-8 h-8 animate-spin
```

### Empty State

```
Container: flex flex-col items-center justify-center min-h-[300px] text-center p-8
Icon: w-16 h-16 text-neutral-400 mb-4
Title: text-lg font-semibold text-neutral-900 mb-2
Description: text-sm text-neutral-600 mb-4
Action: Button to add data or change filters
```

### Error State

```
Container: bg-error-50 border border-error-200 rounded-lg p-6 flex gap-4
Icon: w-12 h-12 text-error-600
Content: flex-1
  Title: font-semibold text-error-900 mb-1
  Message: text-sm text-error-700
  Action: text-sm text-error-600 underline hover:text-error-800 mt-2
```

## Typography for Analytics

### Large Numbers

```
Display: text-4xl lg:text-5xl font-bold text-neutral-900 tabular-nums
With Currency: text-3xl lg:text-4xl font-bold
Percentage: text-3xl lg:text-4xl font-bold
  Symbol: text-2xl text-neutral-600 (%)
```

### Labels

```
Metric Label: text-xs lg:text-sm font-medium text-neutral-600 uppercase tracking-wide
Axis Label: text-xs text-neutral-600
Legend Label: text-sm text-neutral-700
Table Header: text-xs font-semibold text-neutral-700 uppercase tracking-wider
```

### Data Points

```
Chart Values: text-xs font-medium text-neutral-900
Table Cells: text-sm text-neutral-900 tabular-nums
Timestamps: text-xs text-neutral-500
```

## Accessibility for Data

### Chart Alternatives

- Always provide data table view option
- Include ARIA labels for chart regions
- Ensure keyboard navigation for interactive charts
- Provide text summaries of key insights

### Color Blindness

- Never rely on color alone to convey information
- Use patterns/textures in addition to colors
- Provide labels and legends
- Test with colorblind simulation tools

### Screen Readers

- Announce dynamic data updates
- Provide alternative text for chart SVGs
- Use semantic HTML for data tables
- Include skip links for large tables

## Responsive Behavior

### Mobile Dashboard (< 768px)

```
KPI Grid: Single column stack
Charts: Full width, reduced height (250px)
Filters: Accordion or slide-out drawer
Tables: Horizontal scroll with sticky first column
Map: Full width, 300px height minimum
```

### Tablet (768px - 1024px)

```
KPI Grid: 2 columns
Charts: 2-column grid for smaller charts
Full-width charts remain full
Sidebar filters become top bar
```

### Desktop (> 1024px)

```
KPI Grid: 4 columns
Charts: Full dashboard grid (12 columns)
Sidebar filters visible
Hover interactions enabled
```

## Chart Library Recommendations

This design system works best with:

- **Recharts**: React chart library (recommended)
- **Tremor**: React components for dashboards
- **Chart.js**: Flexible charting library
- **D3.js**: For custom visualizations
- **Mapbox**: For map visualizations
- **Leaflet**: Open-source map alternative

## Example Component Combinations

### Executive Dashboard

```
1. KPI Row: 4 metric cards (Revenue, Users, Growth, Churn)
2. Main Chart: Line chart showing trend over time (col-span-8)
3. Breakdown: Pie chart or donut (col-span-4)
4. Data Table: Recent transactions/events (col-span-12)
```

### Analytics Map View

```
1. Filter Bar: Date range + category filters
2. Map: Full width with markers/clusters (60% height)
3. Stats Panel: Sidebar with aggregated metrics (40% height)
4. Data Table: Filtered results below map
```

### Metrics Comparison

```
1. KPI Cards: Current period metrics
2. Two-Column Charts: Side-by-side comparison
3. Trend Table: Detailed breakdown with sparklines
```

## Tailwind Config for Analytics

```js
module.exports = {
  theme: {
    extend: {
      colors: {
        data: {
          primary: '#3B82F6',
          secondary: '#10B981',
          tertiary: '#F59E0B',
          quaternary: '#8B5CF6',
          quinary: '#EF4444',
          senary: '#06B6D4',
        },
        kpi: {
          positive: '#10B981',
          negative: '#EF4444',
          neutral: '#6B7280',
          warning: '#F59E0B',
        },
        heat: {
          cold: '#3B82F6',
          cool: '#06B6D4',
          neutral: '#10B981',
          warm: '#F59E0B',
          hot: '#EF4444',
        },
        chart: {
          bg: '#FFFFFF',
          grid: '#E5E7EB',
          axis: '#9CA3AF',
        }
      }
    }
  }
}
```
