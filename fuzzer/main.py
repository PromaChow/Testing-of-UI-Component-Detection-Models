from tqdm import tqdm
from utils import get_css_classes, load_seed_html
from css_rl_learner import CSSRLLearner

def main():
    weights = [0.8]
    for w in weights:
        for i in range(5, 6):
            for variants in tqdm(range(1, 8)):
                with open(f'/Users/promachowdhury/whatBreaksIt/m3-dataset/seeds/variants_{variants}/index.css', encoding='utf-8') as f:
                    contents = f.read()
                    css_class = get_css_classes(contents)

                html_content = load_seed_html(f'/Users/promachowdhury/whatBreaksIt/m3-dataset/seeds/variants_{variants}/index.html')
                
                learner = CSSRLLearner(
                    css=css_class,
                    initial_html=html_content,
                    icon_folder_path="/Users/promachowdhury/whatBreaksIt/m3-dataset/material-design-icons",
                    image_folder_path="/Users/promachowdhury/whatBreaksIt/downloaded_images/",
                    output=f"data_{w}_{i}",
                    num=variants,
                    w1=w
                )

                learner.learn(episodes=500, steps_per_episode=50)

if __name__ == "__main__":
    main()