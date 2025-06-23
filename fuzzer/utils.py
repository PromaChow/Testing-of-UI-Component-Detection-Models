import math
from collections import defaultdict
import cssutils
import logging
from bs4 import BeautifulSoup

cssutils.log.setLevel(logging.CRITICAL)

def get_css_classes(css_content):
    css = cssutils.parseString(css_content)
    css_styles = {}
    for rule in css:
        if rule.type == rule.STYLE_RULE:
            rules = []
            for declaration in rule.style:
                rules.append({'name':{declaration.name}, 'value':{declaration.value}})
            css_styles[rule.selectorText] = rules
    return css_styles

def load_seed_html(seed_html_path):
    try:
        with open(seed_html_path, 'r', encoding='utf-8') as f:
            return BeautifulSoup(f.read(), 'html.parser')
    except Exception as e:
        print(f"Error loading seed HTML: {e}")
        return None

def update_html_css_reference(html, new_css_path):
    for link in html.find_all('link'):
        if link.get('rel', [''])[0] == 'stylesheet':
            link['href'] = new_css_path
    return html

def calculate_shannon_diversity(values):
    if not values:
        return 0
        
    frequencies = defaultdict(int)
    for value in values:
        frequencies[value] += 1
            
    total = len(values)
    probabilities = [count/total for count in frequencies.values()]
    return -sum(p * math.log2(p) for p in probabilities)