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
            'icon': ['change_icon'],
            'image': ['change_image']
        }
        
        self.q_table = defaultdict(lambda: {action: 0.0 for action in 
                                          sum([acts for acts in self.actions.values()], [])})
        
        self.best_reward = self.calculate_reward(css, initial_html)

    def discretize_state(self, css):
        state_features = {
            'contrast': {'increases': 0, 'decreases': 0, 'avg_value': 0},
            'radius': {'increases': 0, 'decreases': 0, 'avg_value': 0}
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
                
        return new_css, new_html

    def calculate_css_reward(self, css):
        guideline_reward = (
            self.css_evaluator.evaluate_color_contrast(css) + 
            self.css_evaluator.evaluate_border_radius(css) +
            self.css_evaluator.evaluate_elevation(css)
        )
        
        diversity_reward = self.calculate_diversity_reward()

        if random.random() < self.w1:  
            return diversity_reward

        return guideline_reward
    
    def calculate_html_reward(self, html):
        stats = self.resource_manager.get_coverage_stats()
        return (stats['icons']['coverage'] + stats['images']['coverage']) / 2

    def calculate_reward(self, css, html):
        return self.calculate_css_reward(css) + self.calculate_html_reward(html)

    def calculate_diversity_reward(self):
        recent_colors = self.css_modifier.color_history[-50:] if self.css_modifier.color_history else []
        recent_radius = self.css_modifier.radius_history[-50:] if self.css_modifier.radius_history else []
        recent_shadows = self.css_modifier.shadow_history[-50:] if self.css_modifier.shadow_history else []
        
        color_diversity = calculate_shannon_diversity(recent_colors)
        radius_diversity = calculate_shannon_diversity(recent_radius)
        shadow_diversity = calculate_shannon_diversity(recent_shadows)

        return color_diversity + radius_diversity + shadow_diversity

    def save_variant(self, css, html, episode, step, reward, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        variant_prefix = f"variant_e{episode}_s{step}_r{reward:.4f}_{timestamp}"
        
        css_filename = f"{output_dir}/{variant_prefix}.css"
        with open(css_filename, 'w') as f:
            for selector, properties in css.items():
                f.write(f"{selector} {{\n")
                for prop in properties:
                    prop_name = list(prop['name'])[0]
                    prop_value = list(prop['value'])[0]
                    f.write(f"    {prop_name}: {prop_value};\n")
                f.write("}\n\n")
        
        html = update_html_css_reference(html, css_filename)
        html_filename = f"{output_dir}/{variant_prefix}.html"
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html.prettify())
        
        summary_filename = f"{output_dir}/summary.txt"
        with open(summary_filename, 'a') as f:
            f.write(f"\nVariant {timestamp}:\n")
            f.write(f"Episode: {episode}, Step: {step}\n")
            f.write(f"Reward: {reward:.4f}\n")
            f.write("Resource Usage:\n")
            f.write(f"- Icons Used: {len(self.resource_manager.icon_usage)}/{len(self.resource_manager.available_icons)}\n")
            f.write(f"- Images Used: {len(self.resource_manager.image_usage)}/{len(self.resource_manager.available_images)}\n")
            f.write("---\n")

    def learn(self, episodes=100, steps_per_episode=100):
        output_dir = f"{self.output}/variants_{self.num}"
        os.makedirs(output_dir, exist_ok=True)
        episode_rewards = []
        
        best_dir = os.path.join(output_dir, "best")
        checkpoint_dir = os.path.join(output_dir, "checkpoints")
        os.makedirs(best_dir, exist_ok=True)
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        # Initialize variables for adaptive epsilon decay
        reward_window_size = 10
        recent_rewards = []
        base_epsilon_decay = self.epsilon_decay  # Store the original decay rate
        
        for episode in tqdm(range(episodes)):
            current_css = self.current_css.copy()
            current_html = copy.copy(self.current_html)
            episode_reward = 0
            
            for step in range(steps_per_episode):
                current_state = self.discretize_state(current_css)
                category = random.choice(list(self.actions.keys()))
                action = self.select_action(current_state, category)
                new_css, new_html = self.apply_action(current_css, current_html, category, action)
                
                reward = self.calculate_reward(new_css, new_html)
                new_state = self.discretize_state(new_css)
                
                old_q = self.q_table[current_state][action]
                best_future_q = max(self.q_table[new_state].values())
                new_q = (1 - self.learning_rate) * old_q + \
                        self.learning_rate * (reward + self.discount_factor * best_future_q)
                self.q_table[current_state][action] = new_q
                
                if reward > episode_reward:
                    current_css = new_css
                    current_html = new_html
                    episode_reward = reward
                    
                    if reward > self.best_reward:
                        self.best_css = new_css.copy()
                        self.best_html = copy.deepcopy(new_html)
                        self.best_reward = reward
                        self.save_variant(new_css, new_html, episode, step, reward, best_dir)
            
            # Record the episode's best reward
            episode_rewards.append(episode_reward)
            recent_rewards.append(episode_reward)
            
            # Adaptive epsilon decay logic
            if len(recent_rewards) > reward_window_size:
                recent_rewards.pop(0)  # Keep a sliding window
                
                # Calculate trend in recent rewards
                if len(recent_rewards) >= 3:  # Need at least a few points to detect a trend
                    # Simple trend detection - average of newer half vs older half
                    older_half = recent_rewards[:len(recent_rewards)//2]
                    newer_half = recent_rewards[len(recent_rewards)//2:]
                    
                    older_avg = sum(older_half) / len(older_half)
                    newer_avg = sum(newer_half) / len(newer_half)
                    
                    # Adjust epsilon decay based on trend
                    if newer_avg > older_avg * 1.05:  # Rewards improving
                        # Decay faster - explore less, exploit more
                        self.epsilon_decay = base_epsilon_decay * 1.5
                    elif newer_avg < older_avg * 0.95:  # Rewards decreasing
                        # Decay slower - explore more
                        self.epsilon_decay = base_epsilon_decay * 0.5
                    else:  # Rewards stable
                        # Use the base decay rate
                        self.epsilon_decay = base_epsilon_decay
            
            # Apply the adaptive epsilon decay
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
            
            # Optional: Add logging for debugging the adaptive decay
            if episode % 10 == 0:
                avg_reward = sum(recent_rewards) / len(recent_rewards) if recent_rewards else 0
                print(f"Episode {episode}, Avg Reward: {avg_reward:.4f}, Epsilon: {self.epsilon:.4f}, Decay Rate: {self.epsilon_decay:.4f}")
                self.save_variant(current_css, current_html, episode, steps_per_episode, 
                            episode_reward, checkpoint_dir)
                
        plt.plot(episode_rewards)
        plt.xlabel('Episode')
        plt.ylabel('Total Reward')
        plt.title('Reward Progression Over Episodes')
        plt.show()