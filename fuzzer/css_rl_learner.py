import copy
import random
from collections import defaultdict
import os
from datetime import datetime
from tqdm import tqdm
from resource_manager import *
from css_evaluator import *
from css_modifier import *
from utils import *
import matplotlib.pyplot as plt

class CSSRLLearner:
    def __init__(self, css, initial_html, icon_folder_path, image_folder_path, output, num, w1):
        self.output = output
        self.w1 = w1
        self.num = num
        
        self.current_css = css.copy()
        self.best_css = css.copy()
        self.current_html = initial_html
        self.best_html = copy.deepcopy(initial_html)
        
        self.resource_manager = ResourceManager(icon_folder_path, image_folder_path)
        self.css_evaluator = CSSEvaluator()
        self.css_modifier = CSSModifier()
        
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        
        self.actions = {
            'color': ['increase_contrast', 'decrease_contrast', 'complementary', 'random'],
            'elevation': ['increase', 'decrease'],
            'border_radius': ['increase', 'decrease'],
            'typography': ['increase_font_size', 'decrease_font_size', 'increase_line_height', 
                          'decrease_line_height', 'increase_font_weight', 'decrease_font_weight', 'random_typography'],
            'icon': ['change_icon'],
            'image': ['change_image']
        }
        
        self.q_table = defaultdict(lambda: {action: 0.0 for action in 
                                          sum([acts for acts in self.actions.values()], [])})
        
        self.best_reward = self.calculate_total_reward(css, initial_html)

    def discretize_state(self, css):
        state_features = {
            'contrast': {'increases': 0, 'decreases': 0, 'avg_value': 0},
            'radius': {'increases': 0, 'decreases': 0, 'avg_value': 0},
            'typography': {'increases': 0, 'decreases': 0, 'avg_value': 0}
        }
        
        for selector, properties in css.items():
            bg_color = None
            fg_color = None
            for prop in properties:
                if 'color' in prop['name']:
                    fg_color = list(prop['value'])[0]
                elif 'background-color' in prop['name']:
                    bg_color = list(prop['value'])[0]
            
            if bg_color and fg_color:
                contrast = self.css_evaluator.calculate_contrast_ratio(bg_color, fg_color)
                if selector in self.css_modifier.previous_values['contrast']:
                    prev_contrast = self.css_modifier.previous_values['contrast'][selector]
                    change = contrast - prev_contrast
                    if change > 0:
                        state_features['contrast']['increases'] += 1
                    elif change < 0:
                        state_features['contrast']['decreases'] += 1
                state_features['contrast']['avg_value'] += contrast
        
        state_parts = []
        for feature, data in state_features.items():
            inc_bin = min(2, data['increases'] // 2)
            dec_bin = min(2, data['decreases'] // 2)
            avg_bin = min(4, int(data['avg_value'] / 20)) if data['avg_value'] > 0 else 0
            state_parts.append(f"{feature}_{inc_bin}{dec_bin}{avg_bin}")
        
        return "|".join(state_parts)

    def select_action(self, state, category):
        if random.random() < self.epsilon:
            return random.choice(self.actions[category])
        
        q_values = self.q_table[state]
        category_actions = self.actions[category]
        return max(category_actions, key=lambda a: q_values[a])
        
    def apply_action(self, css, html, category, action):
        new_css = css.copy()
        new_html = copy.copy(html)
        
        if category == 'icon' or category == 'image':
            new_html, new_css = self.resource_manager.process_html(new_html, new_css)
        
        elif category == 'color':
            if action == 'increase_contrast':
                new_css = self.css_modifier.modify_contrast(new_css, increase=True)
            elif action == 'decrease_contrast':
                new_css = self.css_modifier.modify_contrast(new_css, increase=False)
            elif action == 'complementary':
                new_css = self.css_modifier.apply_complementary_colors(new_css)
            else:
                new_css = self.css_modifier.randomize_colors(new_css)
                
        elif category == 'elevation':
            new_css = self.css_modifier.modify_elevation(new_css, increase=(action == 'increase'))
                
        elif category == 'border_radius':
            new_css = self.css_modifier.modify_border_radius(new_css, increase=(action == 'increase'))
        
        elif category == 'typography':
            if action == 'increase_font_size':
                new_css = self.css_modifier.modify_font_size(new_css, increase=True)
            elif action == 'decrease_font_size':
                new_css = self.css_modifier.modify_font_size(new_css, increase=False)
            elif action == 'increase_line_height':
                new_css = self.css_modifier.modify_line_height(new_css, increase=True)
            elif action == 'decrease_line_height':
                new_css = self.css_modifier.modify_line_height(new_css, increase=False)
            elif action == 'increase_font_weight':
                new_css = self.css_modifier.modify_font_weight(new_css, increase=True)
            elif action == 'decrease_font_weight':
                new_css = self.css_modifier.modify_font_weight(new_css, increase=False)
            else:
                new_css = self.css_modifier.randomize_typography(new_css)
                
        return new_css, new_html

    def calculate_guideline_reward(self, css):
        contrast_score = self.css_evaluator.evaluate_color_contrast(css)
        radius_score = self.css_evaluator.evaluate_border_radius(css)
        elevation_score = self.css_evaluator.evaluate_elevation(css)
        typography_score = self.css_evaluator.evaluate_typography(css)
        
        return (contrast_score + radius_score + elevation_score + typography_score) / 4

    def calculate_diversity_reward(self):
        recent_colors = self.css_modifier.color_history[-50:] if self.css_modifier.color_history else []
        recent_radius = self.css_modifier.radius_history[-50:] if self.css_modifier.radius_history else []
        recent_shadows = self.css_modifier.shadow_history[-50:] if self.css_modifier.shadow_history else []
        recent_font_sizes = self.css_modifier.font_size_history[-50:] if self.css_modifier.font_size_history else []
        recent_line_heights = self.css_modifier.line_height_history[-50:] if self.css_modifier.line_height_history else []
        recent_font_weights = self.css_modifier.font_weight_history[-50:] if self.css_modifier.font_weight_history else []
        
        color_diversity = calculate_shannon_diversity(recent_colors)
        radius_diversity = calculate_shannon_diversity(recent_radius)
        shadow_diversity = calculate_shannon_diversity(recent_shadows)
        font_size_diversity = calculate_shannon_diversity(recent_font_sizes)
        line_height_diversity = calculate_shannon_diversity(recent_line_heights)
        font_weight_diversity = calculate_shannon_diversity(recent_font_weights)

        return (color_diversity + radius_diversity + shadow_diversity + 
                font_size_diversity + line_height_diversity + font_weight_diversity) / 6

    def calculate_resource_reward(self, html):
        stats = self.resource_manager.get_coverage_stats()
        return (stats['icons']['coverage'] + stats['images']['coverage']) / 2

    def calculate_total_reward(self, css, html):
        guideline_reward = self.calculate_guideline_reward(css)
        diversity_reward = self.calculate_diversity_reward()
        resource_reward = self.calculate_resource_reward(html)
        
        if random.random() < self.w1:
            final_reward = diversity_reward
        else:
            final_reward = guideline_reward
        
        final_reward += resource_reward
        
        return final_reward

    def save_variant(self, css, html, episode, step, reward, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now