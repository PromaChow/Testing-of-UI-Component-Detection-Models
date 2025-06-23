import random
import colorsys
from collections import defaultdict

class CSSModifier:
    def __init__(self):
        self.color_history = []
        self.size_history = []
        self.radius_history = []
        self.shadow_history = []
        self.previous_values = defaultdict(dict)

    def modify_contrast(self, css, increase):
        new_css = css.copy()
        for selector, properties in new_css.items():
            bg_color = None
            fg_color = None
            
            for prop in properties:
                if 'color' in prop['name']:
                    fg_color = list(prop['value'])[0]
                elif 'background-color' in prop['name']:
                    bg_color = list(prop['value'])[0]
            
            if bg_color and fg_color and bg_color.startswith('#') and fg_color.startswith('#'):
                bg_rgb = self.hex_to_rgb(bg_color)
                fg_rgb = self.hex_to_rgb(fg_color)
                bg_hsv = colorsys.rgb_to_hsv(*[x/255 for x in bg_rgb])
                fg_hsv = colorsys.rgb_to_hsv(*[x/255 for x in fg_rgb])
                
                if increase:
                    if bg_hsv[2] > fg_hsv[2]:
                        bg_hsv = (bg_hsv[0], bg_hsv[1], min(1.0, bg_hsv[2] * 1.2))
                        fg_hsv = (fg_hsv[0], fg_hsv[1], max(0.0, fg_hsv[2] * 0.8))
                    else:
                        bg_hsv = (bg_hsv[0], bg_hsv[1], max(0.0, bg_hsv[2] * 0.8))
                        fg_hsv = (fg_hsv[0], fg_hsv[1], min(1.0, fg_hsv[2] * 1.2))
                else:
                    bg_hsv = (bg_hsv[0], bg_hsv[1], (bg_hsv[2] + 0.5) / 2)
                    fg_hsv = (fg_hsv[0], fg_hsv[1], (fg_hsv[2] + 0.5) / 2)
                
                bg_rgb = [int(x * 255) for x in colorsys.hsv_to_rgb(*bg_hsv)]
                fg_rgb = [int(x * 255) for x in colorsys.hsv_to_rgb(*fg_hsv)]
                
                for prop in properties:
                    if 'color' in prop['name']:
                        new_color = self.rgb_to_hex(tuple(fg_rgb))
                        prop['value'] = {new_color}
                        self.color_history.append(new_color)
                    elif 'background-color' in prop['name']:
                        new_color = self.rgb_to_hex(tuple(bg_rgb))
                        prop['value'] = {new_color}
                        self.color_history.append(new_color)
        
        return new_css

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb):
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

    def apply_complementary_colors(self, css):
        new_css = css.copy()
        for selector, properties in new_css.items():
            for prop in properties:
                if ('color' in prop['name'] or 'background-color' in prop['name']) and \
                list(prop['value'])[0].startswith('#'):
                    color = list(prop['value'])[0]
                    rgb = self.hex_to_rgb(color)
                    hsv = colorsys.rgb_to_hsv(*[x/255 for x in rgb])
                    comp_hsv = ((hsv[0] + 0.5) % 1.0, hsv[1], hsv[2])
                    comp_rgb = [int(x * 255) for x in colorsys.hsv_to_rgb(*comp_hsv)]
                    new_color = self.rgb_to_hex(tuple(comp_rgb))
                    prop['value'] = {new_color}
                    self.color_history.append(new_color)
        
        return new_css

    def randomize_colors(self, css):
        new_css = css.copy()
        for selector, properties in new_css.items():
            for prop in properties:
                if ('color' in prop['name'] or 'background-color' in prop['name']):
                    h = random.random()
                    s = random.uniform(0.3, 0.7)
                    v = random.uniform(0.3, 0.9)
                    rgb = [int(x * 255) for x in colorsys.hsv_to_rgb(h, s, v)]
                    new_color = self.rgb_to_hex(tuple(rgb))
                    prop['value'] = {new_color}
                    self.color_history.append(new_color)
        return new_css

    def modify_elevation(self, css, increase):
        new_css = css.copy()
        for properties in new_css.values():
            for prop in properties:
                if 'box-shadow' in prop['name']:
                    shadow = list(prop['value'])[0]
                    numbers = [float(n) for n in re.findall(r'-?\d+\.?\d*', shadow)]
                    if numbers:
                        factor = 1.2 if increase else 0.8
                        new_numbers = [n * factor for n in numbers]
                        new_shadow = f"{int(new_numbers[0])}px {int(new_numbers[1])}px {int(new_numbers[2])}px"
                        prop['value'] = {new_shadow}
                        self.shadow_history.append(new_shadow)
        return new_css

    def modify_border_radius(self, css, increase):
        new_css = css.copy()
        for properties in new_css.values():
            for prop in properties:
                if 'border-radius' in prop['name']:
                    radius = self.extract_number(list(prop['value'])[0])
                    if radius:
                        new_radius = radius * (1.2 if increase else 0.8)
                        new_value = f"{int(new_radius)}px"
                        prop['value'] = {new_value}
                        self.radius_history.append(str(int(new_radius)))
        return new_css

    def extract_number(self, value):
        try:
            return float(''.join(c for c in value if c.isdigit() or c == '.'))
        except:
            return 0.0