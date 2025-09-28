import os
import yaml
import shutil
import markdown
from jinja2 import Environment, FileSystemLoader


# Load all YAML files into a single structured dictionary
def load_yaml_data(data_dir="data"):
    site_data = {}

    for file in os.listdir(data_dir):
        if not file.endswith(".yaml") and not file.endswith(".yml"):
            continue

        section_name = os.path.splitext(file)[0]
        print("Loading section:", section_name)
        path = os.path.join(data_dir, file)

        with open(path) as f:
            content = yaml.safe_load(f)

        site_data[section_name] = content

    if "me" in site_data and "bio" in site_data["me"]:
        site_data["me"]["bio"] = markdown.markdown(site_data["me"]["bio"])

    return site_data

# Render all pages using Jinja2
def render_site(site_data, templates_dir="templates", output_dir="docs"):
    env = Environment(loader=FileSystemLoader(templates_dir))
    # Register custom filter
    env.filters['markdownify'] = lambda text: markdown.markdown(text)
    cv_template = env.get_template("cv.html")
    index_template = env.get_template("index.html")

    os.makedirs(output_dir, exist_ok=True)

    all_items_for_index = []

    # Load all templates in the templates directory
    for template_file in os.listdir(templates_dir):
        if not template_file.endswith(".html"):
            continue

        template_name = os.path.splitext(template_file)[0]
        print("Loading template:", template_name)

        with open(os.path.join(output_dir, template_file), "w") as f:
            f.write(index_template.render(data=site_data))

    print("Site generated in:", output_dir)

if __name__ == "__main__":
    output_dir = "docs"
    data = load_yaml_data("data")
    render_site(data, templates_dir="templates", output_dir=output_dir)
    shutil.copytree("static", output_dir, dirs_exist_ok=True)
