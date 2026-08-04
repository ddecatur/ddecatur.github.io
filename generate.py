import os
import yaml
import shutil
import markdown
from jinja2 import Environment, FileSystemLoader


MONTHS = {
    name: num
    for num, name in enumerate(
        [
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december",
        ],
        start=1,
    )
}


def month_num(name):
    """Month name -> 1..12; missing/unknown -> 0 so it sorts last within a year."""
    if not name:
        return 0
    return MONTHS.get(str(name).strip().lower(), 0)


def sort_talks(site_data):
    """Sort talks most-recent-first for both the website and the CV.

    Ordering key is (year, month), descending. Talks with no month sort last
    within their year (month_num -> 0). Ties keep original file order (a stable
    sort), so the first-listed of two undated same-year talks is treated as the
    most recent.
    """
    talks = site_data.get("talks")
    if not talks:
        return

    # Preserve file order so stable-sort tie-breaks prefer the first-listed talk.
    original = list(talks)

    # CV: one row per (talk, year), globally sorted by date.
    rows = []
    for talk in original:
        for year in talk.get("years", []):
            row = dict(talk)
            row["year"] = year
            rows.append(row)
    site_data["talks_cv"] = sorted(
        rows,
        key=lambda r: (r["year"], month_num(r.get("month"))),
        reverse=True,
    )

    # Website: one entry per talk, sorted by its most-recent year then month.
    site_data["talks"] = sorted(
        original,
        key=lambda t: (max(t.get("years", [0])), month_num(t.get("month"))),
        reverse=True,
    )


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
        site_data["me"]["bio"] = markdown.markdown(
            site_data["me"]["bio"], extensions=["attr_list"]
        )

    sort_talks(site_data)

    return site_data

# Render all pages using Jinja2
def render_site(site_data, templates_dir="templates", output_dir="docs"):
    env = Environment(loader=FileSystemLoader(templates_dir))
    # Register custom filter
    env.filters['markdownify'] = lambda text: markdown.markdown(text, extensions=["attr_list"])
    cv_template = env.get_template("cv.html")
    index_template = env.get_template("index.html")

    os.makedirs(output_dir, exist_ok=True)

    all_items_for_index = []

    # Load all templates in the templates directory
    for template_file in os.listdir(templates_dir):
        if not template_file.endswith(".html"):
            continue

        template = env.get_template(template_file)
        template_name = os.path.splitext(template_file)[0]
        print("Loading template:", template_name)

        with open(os.path.join(output_dir, template_file), "w") as f:
            f.write(template.render(data=site_data))
        

    print("Site generated in:", output_dir)

if __name__ == "__main__":
    output_dir = "docs"
    data = load_yaml_data("data")
    render_site(data, templates_dir="templates", output_dir=output_dir)
    shutil.copytree("static", output_dir, dirs_exist_ok=True)
