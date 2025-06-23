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
                if contrast >= 7.0:
                    scores.append(1.0)
                elif contrast >= 4.5:
                    scores.append(0.8)
                elif contrast >= 3.0:
                    scores.append(0.6)
                else:
                    scores.append(0.2)
        
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
                        score = max(0.1, math.exp(-deviation))
                    
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
                        score = max(0.1, math.exp(-deviation))
                    
                    scores.append(score)
        
        return sum(scores) / len(scores) if scores else 0.5

    def evaluate_typography(self, css):
        def get_expected_font_size(selector):
            selector = selector.lower()
            if any(x in selector for x in ['h1', 'headline1', 'headline-large']):
                return 32
            elif any(x in selector for x in ['h2', 'headline2', 'headline-medium']):
                return 28
            elif any(x in selector for x in ['h3', 'headline3', 'headline-small']):
                return 24
            elif any(x in selector for x in ['h4', 'title1', 'title-large']):
                return 22
            elif any(x in selector for x in ['h5', 'title2', 'title-medium']):
                return 16
            elif any(x in selector for x in ['h6', 'title3', 'title-small']):
                return 14
            elif any(x in selector for x in ['body1', 'body-large']):
                return 16
            elif any(x in selector for x in ['body2', 'body-medium']):
                return 14
            elif any(x in selector for x in ['caption', 'label-small']):
                return 12
            elif any(x in selector for x in ['overline', 'label-medium']):
                return 11
            return 14

        def get_expected_line_height(font_size):
            return font_size * 1.5

        def get_expected_font_weight(selector):
            selector = selector.lower()
            if any(x in selector for x in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'headline', 'title']):
                return 500
            elif any(x in selector for x in ['button', 'btn']):
                return 500
            elif any(x in selector for x in ['overline', 'caption']):
                return 400
            return 400

        scores = []
        for selector, properties in css.items():
            font_size = None
            line_height = None
            font_weight = None
            
            for prop in properties:
                prop_name = list(prop['name'])[0]
                prop_value = list(prop['value'])[0]
                
                if prop_name == 'font-size':
                    font_size = self.extract_number(prop_value)
                elif prop_name == 'line-height':
                    line_height = self.extract_number(prop_value)
                elif prop_name == 'font-weight':
                    font_weight = self.extract_number(prop_value)
            
            if font_size:
                expected_size = get_expected_font_size(selector)
                size_deviation = abs(font_size - expected_size)
                
                if size_deviation <= 1:
                    size_score = 1.0
                elif size_deviation <= 2:
                    size_score = 0.8
                elif size_deviation <= 4:
                    size_score = 0.6
                else:
                    size_score = max(0.2, math.exp(-size_deviation))
                
                scores.append(size_score)
            
            if line_height and font_size:
                expected_lh = get_expected_line_height(font_size)
                lh_deviation = abs(line_height - expected_lh)
                
                if lh_deviation <= 2:
                    lh_score = 1.0
                elif lh_deviation <= 4:
                    lh_score = 0.8
                elif lh_deviation <= 6:
                    lh_score = 0.6
                else:
                    lh_score = max(0.2, math.exp(-lh_deviation))
                
                scores.append(lh_score)
            
            if font_weight:
                expected_weight = get_expected_font_weight(selector)
                weight_deviation = abs(font_weight - expected_weight)
                
                if weight_deviation <= 50:
                    weight_score = 1.0
                elif weight_deviation <= 100:
                    weight_score = 0.8
                elif weight_deviation <= 200:
                    weight_score = 0.6
                else:
                    weight_score = max(0.2, math.exp(-weight_deviation))
                
                scores.append(weight_score)
        
        return sum(scores) / len(scores) if scores else 0.5