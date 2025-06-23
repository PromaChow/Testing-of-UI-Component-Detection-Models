# Web UI Generation and Screenshot Tool

This project consists of two main components:

1. A Python-based CSS/HTML generator using reinforcement learning
2. A JavaScript-based HTML-to-image converter

## Part 1: CSS/HTML Generator (Python)

### Prerequisites

```bash
pip install numpy beautifulsoup4 tqdm cssutils
```

### Project Structure

```
css_generator/
├── css_evaluator.py      # CSS evaluation logic
├── css_modifier.py       # CSS modification functions
├── css_rl_learner.py    # Main reinforcement learning implementation
├── resource_manager.py   # Manages icons and images
├── utils.py             # Utility functions
└── main.py             # Entry point
```

### Configuration

Update the paths in `main.py`:

```python
# Change these paths to match your setup
SEEDS_PATH = '/path/to/seeds/'
ICONS_PATH = '/path/to/material-design-icons/'
IMAGES_PATH = '/path/to/downloaded_images/'
OUTPUT_PATH = '/path/to/output/'
```

### Running the Generator

```bash
python main.py
```

This will:

1. Load seed HTML/CSS files
2. Generate variations using reinforcement learning
3. Save generated variants in the output directory

### Output Structure

```
output/
├── data_0.7_5/
│   ├── variants_1/
│   │   ├── best/
│   │   └── checkpoints/
│   ├── variants_2/
│   └── ...
```

## Part 2: HTML-to-Image Converter (JavaScript)

### Prerequisites

```bash
npm install puppeteer express
```

### Project Structure

```
html_to_image/
├── html_converter.js    # Main conversion logic
├── server.js           # Static file server
└── main.js            # Entry point
```

### Configuration

Update the paths in `main.js`:

```javascript
// Change this to your input directory
const mainDirectories = ["/path/to/generated/variants"];

// Update dimensions if needed
const VARIANT_DIMENSIONS = {
  variants_1: { width: 412, height: 1036 },
  // ... add more variants as needed
};
```

### Running the Converter

```bash
node main.js
```

This will:

1. Process all HTML files in the input directories
2. Generate PNG screenshots for each file
3. Save images in the respective output directories

### Output Structure

```
output/
├── variants_1/
│   ├── variant1.png
│   ├── variant2.png
│   └── ...
├── variants_2/
└── ...
```

## Complete Workflow

1. First, run the Python generator:

```bash
cd css_generator
python main.py
```

2. Then, use the JavaScript converter to create images:

```bash
cd html_to_image
node main.js
```

## Notes

- The Python generator uses reinforcement learning to create variations of web UIs while maintaining design guidelines
- The JavaScript converter uses Puppeteer to create high-quality screenshots of the generated UIs
- Make sure all paths are correctly set up before running either component
- Each variant can have different dimensions, which are specified in the JavaScript configuration

## Troubleshooting

### Common Issues:

1. **Path Issues**:

   - Ensure all paths are absolute or correctly referenced relative to the execution directory
   - Check file permissions in input/output directories

2. **Memory Issues**:

   - If processing large numbers of files, you might need to increase Node.js memory limit:

   ```bash
   node --max-old-space-size=4096 main.js
   ```

3. **Port Conflicts**:
   - The default port is 3000. If it's in use, change it in the JavaScript configuration:
   ```javascript
   port: 3000; // Change to another port if needed
   ```

# Testing-of-UI-Component-Detection-Models

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

| Deviation   | Score | Quality    |
| ----------- | ----- | ---------- |
| Exact match | 1.0   | Perfect    |
| ±2px        | 0.8   | Good       |
| ±4px        | 0.6   | Acceptable |
| ±8px        | 0.3   | Poor       |

## Elevation Guidelines (Material Design)

### Component Elevation Levels

| Component                                                       | Expected Elevation |
| --------------------------------------------------------------- | ------------------ |
| FAB/DatePicker/Dialog/Search/TimePicker                         | 6dp                |
| Bottom App Bar/Dropdown/Menu/Navigation Bar/Top App Bar/Tooltip | 3dp                |
| Chip/Banner/Sheet/Elevated/Lowered/Slider Handle                | 1dp                |
| Default components                                              | 0dp                |

### Scoring System

| Deviation | Score | Quality    |
| --------- | ----- | ---------- |
| ±0.5dp    | 1.0   | Perfect    |
| ±1dp      | 0.8   | Good       |
| ±2dp      | 0.5   | Acceptable |
| ±3dp      | 0.2   | Poor       |

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

| Deviation | Score |
| --------- | ----- |
| ±1px      | 1.0   |
| ±2px      | 0.8   |
| ±4px      | 0.6   |

#### Line Height Deviation

| Deviation | Score                |
| --------- | -------------------- |
| ±2px      | 1.0                  |
| ±4px      | 0.8                  |
| ±6px      | 0.6                  |
| >6px      | e^(-dev/6) (min 0.2) |

#### Font Weight Deviation

| Deviation | Score |
| --------- | ----- |
| ±50       | 1.0   |
| ±100      | 0.8   |
| ±200      | 0.6   |

## Overall Evaluation

```
Final guideline score = (contrast + radius + elevation + typography) / 4
```

Each guideline contributes equally to the overall design quality assessment.
