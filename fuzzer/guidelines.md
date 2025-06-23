# CSS Design Guidelines & Evaluation Standards

## Color Contrast Guidelines (WCAG)

### Contrast Ratio Standards

| Contrast Ratio | Score | Compliance Level | Description               |
| -------------- | ----- | ---------------- | ------------------------- |
| 7.0+           | 1.0   | AAA              | Perfect accessibility     |
| 4.5+           | 0.8   | AA               | Good accessibility        |
| 3.0+           | 0.6   | AA Large         | Acceptable for large text |
| <3.0           | 0.2   | Fail             | Poor accessibility        |

### Calculation

```
Contrast ratio = (lighter luminance + 0.05) / (darker luminance + 0.05)
```

## Border Radius Guidelines (Material Design)

### Component-Specific Values

| Component                                       | Expected Radius |
| ----------------------------------------------- | --------------- |
| FAB/Extended FAB                                | 28px            |
| Bottom Sheet/Side Sheet/Navigation Drawer Modal | 16px            |
| Card/Dialog                                     | 12px            |
| Bottom Sheet Header/Navigation Drawer           | 8px             |
| Chip/Helper/Menu/Tooltip Light/Snackbar         | 4px             |
| Time Picker/Menu Item/Tooltip Dark              | 0px             |
| Default components                              | 4px             |

### Scoring System

| Deviation   | Score      | Quality             |
| ----------- | ---------- | ------------------- |
| Exact match | 1.0        | Perfect             |
| ±2px        | 0.8        | Good                |
| ±4px        | 0.6        | Acceptable          |
| ±8px        | 0.3        | Poor                |
| >8px        | e^(-dev/8) | Very Poor (min 0.1) |

## Elevation Guidelines (Material Design)

### Component Elevation Levels

| Component                                                       | Expected Elevation |
| --------------------------------------------------------------- | ------------------ |
| FAB/DatePicker/Dialog/Search/TimePicker                         | 6dp                |
| Bottom App Bar/Dropdown/Menu/Navigation Bar/Top App Bar/Tooltip | 3dp                |
| Chip/Banner/Sheet/Elevated/Lowered/Slider Handle                | 1dp                |
| Default components                                              | 0dp                |

### Scoring System

| Deviation | Score      | Quality             |
| --------- | ---------- | ------------------- |
| ±0.5dp    | 1.0        | Perfect             |
| ±1dp      | 0.8        | Good                |
| ±2dp      | 0.5        | Acceptable          |
| ±3dp      | 0.2        | Poor                |
| >3dp      | e^(-dev+3) | Very Poor (min 0.1) |

## Typography Guidelines (Material Design)

### Font Size Standards

| Element               | Font Size |
| --------------------- | --------- |
| H1/Headline Large     | 32px      |
| H2/Headline Medium    | 28px      |
| H3/Headline Small     | 24px      |
| H4/Title Large        | 22px      |
| H5/Title Medium       | 16px      |
| H6/Title Small        | 14px      |
| Body Large            | 16px      |
| Body Medium           | 14px      |
| Caption/Label Small   | 12px      |
| Overline/Label Medium | 11px      |
| Default               | 14px      |

### Font Weight Standards

| Element Type             | Font Weight  |
| ------------------------ | ------------ |
| Headlines/Titles/Buttons | 500 (medium) |
| Overline/Caption         | 400 (normal) |
| Default                  | 400 (normal) |

### Line Height Standards

**Formula**: Font size × 1.5  
**Example**: 16px font → 24px line height

### Typography Scoring

#### Font Size Deviation

| Deviation | Score                |
| --------- | -------------------- |
| ±1px      | 1.0                  |
| ±2px      | 0.8                  |
| ±4px      | 0.6                  |
| >4px      | e^(-dev/4) (min 0.2) |

#### Line Height Deviation

| Deviation | Score                |
| --------- | -------------------- |
| ±2px      | 1.0                  |
| ±4px      | 0.8                  |
| ±6px      | 0.6                  |
| >6px      | e^(-dev/6) (min 0.2) |

#### Font Weight Deviation

| Deviation | Score                  |
| --------- | ---------------------- |
| ±50       | 1.0                    |
| ±100      | 0.8                    |
| ±200      | 0.6                    |
| >200      | e^(-dev/200) (min 0.2) |

## Overall Evaluation

```
Final guideline score = (contrast + radius + elevation + typography) / 4
```

Each guideline contributes equally to the overall design quality assessment.
