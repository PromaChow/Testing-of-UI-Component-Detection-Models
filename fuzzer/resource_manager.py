import os
import glob
from pathlib import Path
from collections import defaultdict
import random
import copy

class ResourceManager:
    def __init__(self, icon_folder_path: str, image_folder_path: str):
        self.icon_folder = icon_folder_path
        self.image_folder = image_folder_path
        self.available_icons = self.load_icons()
        self.available_images = self.load_images()
        self.icon_usage = defaultdict(int)
        self.unused_icons = set(self.available_icons.keys())
        self.image_usage = defaultdict(int)
        self.unused_images = set(self.available_images)
        self.current_page_icons = set()
        self.current_page_images = set()

    def load_icons(self):
        icons = {}
        for file in glob.glob(os.path.join(self.icon_folder, '**/*.svg'), recursive=True):
            name = Path(file).stem
            icons[name] = file
        return icons

    def select_icon(self):
        if self.unused_icons:
            selected_name = random.choice(list(self.unused_icons))
            self.unused_icons.remove(selected_name)
        else:
            usage_counts = [(name, count) for name, count in self.icon_usage.items()]
            min_usage = min(usage_counts, key=lambda x: x[1])[1]
            least_used = [name for name, count in usage_counts if count == min_usage]
            selected_name = random.choice(least_used)
        
        icon_path = self.available_icons[selected_name]
        return selected_name, icon_path

    def load_images(self):
        images = set()
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            images.update(Path(f).name for f in glob.glob(os.path.join(self.image_folder, ext)))
        return images

    def select_image(self):
        if self.unused_images:
            selected = random.choice(list(self.unused_images))
            self.unused_images.remove(selected)
            return selected
        
        available = self.available_images - self.current_page_images
        if available:
            return min(available, key=lambda x: self.image_usage[x])
            
        return min(self.available_images, key=lambda x: self.image_usage[x])

    def get_coverage_stats(self):
        total_icons = len(self.available_icons)
        used_icons = len(self.icon_usage)
        icon_coverage = used_icons / total_icons if total_icons > 0 else 0
        
        return {
            'icons': {
                'total': total_icons,
                'used': used_icons,
                'unused': total_icons - used_icons,
                'coverage': icon_coverage,
                'usage_distribution': dict(self.icon_usage)
            },
            'images': {
                'total': len(self.available_images),
                'used': len(self.image_usage),
                'unused': len(self.unused_images),
                'coverage': len(self.image_usage) / len(self.available_images) if self.available_images else 0,
                'usage_distribution': dict(self.image_usage)
            }
        }

    def process_html(self, html, css):
        new_html = copy.copy(html)
        new_css = css.copy()
        self.current_page_icons.clear()
        
        for img in new_html.find_all('img'):
            src = img.get('src', '')
            
            if src.endswith('.svg'):
                icon_name, icon_content = self.select_icon()
                new_src = f"{self.icon_folder}/{icon_name}.svg"
                img['src'] = new_src
                self.icon_usage[icon_name] += 1
                self.current_page_icons.add(icon_name)
            
            elif any(src.endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                if self.unused_images:
                    new_image = random.choice(list(self.unused_images))
                    self.unused_images.remove(new_image)
                else:
                    new_image = random.choice(list(self.available_images))
                
                img['src'] = f"{self.image_folder}{new_image}"
                self.image_usage[new_image] += 1

        return new_html, new_css