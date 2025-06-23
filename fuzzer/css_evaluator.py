import colorsys
import re
import math

class CSSEvaluator:
    @staticmethod
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def rgb_to_hex(rgb):
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

    @staticmethod
    def get_relative_luminance(color):
        r, g, b = CSSEvaluator.hex_to_rgb(color)
        r, g, b = r/255, g/255, b/255
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    @staticmethod
    def calculate_contrast_ratio(color1, color2):
        l1 = CSSEvaluator.get_relative_luminance(color1)
        l2 = CSSEvaluator.get_relative_luminance(color2)
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)

    @staticmethod
    def extract_number(value):
        try:
            return float(''.join(c for c in value if c.isdigit() or c == '.'))
        except:
            return 0.0

    def evaluate_color_contrast(self, css):
        scores = []
        for selector, properties in css.items():
            bg_color = None
            fg_color = None
            for prop in properties:
                if 'color' in prop['name']:
                    fg_color = list(prop['value'])[0]
                elif 'background-color' in prop['name']:
                    bg_color = list(prop['value'])[0]
            
            if bg_color and fg_color and bg_color.startswith('#') and fg_color.startswith('#'):
                contrast = self.calculate_contrast_ratio(bg_color, fg_color)
                if contrast >= 4.5:
                    scores.append(1.0)
                elif contrast >= 3.0:
                    scores.append(0.7)
                else:
                    scores.append(0.3)
        
        return sum(scores) / len(scores) if scores else 0.5

    def evaluate_border_radius(self, css):
        def get_expected_radius(selector):
            selector = selector.lower()
            if any(x in selector for x in ['fab', 'extended-fab']):
                return 28
            elif any(x in selector for x in ['bottom-sheet', 'side-sheet', 'navigation-drawer-modal']):
                return 16
            elif any(x in selector for x in ['card', 'dialog']):
                return 12
            elif any(x in selector for x in ['bottom-sheet-header', 'navigation-drawer']):
                return 8
            elif any(x in selector for x in ['chip', 'helper', 'menu', 'tooltip-light', 'snackbar']):
                return 4
            elif any(x in selector for x in ['time-picker', 'menu-item', 'tooltip-dark']):
                return 0
            return 4
            
        scores = []
        for selector, properties in css.items():
            for prop in properties:
                if 'border-radius' in prop['name']:
                    radius = self.extract_number(list(prop['value'])[0])
                    expected_radius = get_expected_radius(selector)
                    deviation = abs(radius - expected_radius)
                    
                    if deviation == 0:
                        score = 1.0
                    elif deviation <= 2:
                        score = 0.8
                    elif deviation <= 4:
                        score = 0.6
                    elif deviation <= 8:
                        score = 0.3
                    else:
                        score = max(0.1, math.exp(-deviation/8))
                    
                    scores.append(score)
        
        return sum(scores) / len(scores) if scores else 0.5

    def evaluate_elevation(self, css):
        def get_elevation_dp(shadow_value):
            if not shadow_value:
                return 0
            numbers = [float(n) for n in re.findall(r'-?\d*\.?\d+', shadow_value)]
            return max(numbers) if numbers else 0
            
        def get_expected_elevation(selector):
            selector = selector.lower()
            if any(x in selector for x in ['fab', 'datepicker', 'dialog', 'search', 'timepicker']):
                return 6
            elif any(x in selector for x in ['bottomappbar', 'dropdown', 'menu', 'navigationbar', 
                                        'topappbar', 'tooltip']):
                return 3
            elif any(x in selector for x in ['chip', 'banner', 'sheet', 'elevated', 'lowered', 
                                        'slider-handle']):
                return 1
            return 0

        scores = []
        for selector, properties in css.items():
            for prop in properties:
                if 'box-shadow' in prop['name']:
                    shadow_value = list(prop['value'])[0]
                    current_dp = get_elevation_dp(shadow_value)
                    expected_dp = get_expected_elevation(selector)
                    deviation = abs(current_dp - expected_dp)
                    
                    if deviation <= 0.5:
                        score = 1.0
                    elif deviation <= 1:
                        score = 0.8
                    elif deviation <= 2:
                        score = 0.5
                    elif deviation <= 3:
                        score = 0.2
                    else:
                        score = max(0.1, math.exp(-deviation + 3))
                    
                    scores.append(score)
        
        return sum(scores) / len(scores) if scores else 0.5