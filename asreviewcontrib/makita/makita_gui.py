import importlib.resources as resources
from pathlib import Path
from typing import Literal

import streamlit as st
from asreview import config as ASREVIEW_CONFIG
from streamlit.components.v1 import html

# https://gist.github.com/toolittlecakes/cf1a5d734cbf5b0b2581c28b2530fec2


def st_fixed_container(
    *,
    height: int | None = None,
    border: bool | None = None,
    mode: Literal["fixed", "sticky"] = "fixed",
    position: Literal["top", "bottom"] = "top",
    margin: str | None = None,
    key: str | None = None,
):
    if margin is None:
        margin = {"top": "2.875rem", "bottom": "0"}[position]

    fixed_container_css = """

div[data-testid="stVerticalBlockBorderWrapper"]:has(div.fixed-container-{id}):not(:has(div.not-fixed-container)){{
    background-color: transparent;
    position: {mode};
    width: inherit;
    background-color: inherit;
    {position}: {margin};
    z-index: 999;

}}

div[data-testid="stVerticalBlockBorderWrapper"]:has(div.fixed-container-{id}):not(:has(div.not-fixed-container)) div[data-testid="stVerticalBlock"]:has(div.fixed-container-{id}):not(:has(div.not-fixed-container)) > div[data-testid="element-container"] {{
    display: none;
}}


div[data-testid="stVerticalBlockBorderWrapper"]:has(div.not-fixed-container):not(:has(div[class^='fixed-container-'])) {{
    display: none;
}}
""".strip()

    fixed_container = st.container()
    non_fixed_container = st.container()
    css = fixed_container_css.format(
        mode=mode,
        position=position,
        margin=margin,
        id=key,
    )
    with fixed_container:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='fixed-container-{key}'></div>",
            unsafe_allow_html=True,
        )
    with non_fixed_container:
        st.markdown(
            "<div class='not-fixed-container'></div>",
            unsafe_allow_html=True,
        )

    opaque_container_js = """
const root = parent.document.querySelector('.stApp');
let lastBackgroundColor = null;


function updateContainerBackground(currentBackground) {
    parent.document.documentElement.style.setProperty('--background-color', currentBackground);
    ;
}

function checkForBackgroundColorChange() {
    const style = window.getComputedStyle(root);
    const currentBackgroundColor = style.backgroundColor;
    if (currentBackgroundColor !== lastBackgroundColor) {
        lastBackgroundColor = currentBackgroundColor; // Update the last known value
        updateContainerBackground(lastBackgroundColor);
    }
}

const observerCallback = (mutationsList, observer) => {
    for(let mutation of mutationsList) {
        if (mutation.type === 'attributes' && (mutation.attributeName === 'class' || mutation.attributeName === 'style')) {
            checkForBackgroundColorChange();
        }
    }
};

const main = () => {
    checkForBackgroundColorChange();

    const observer = new MutationObserver(observerCallback);
    observer.observe(root, { attributes: true, childList: false, subtree: false });
}

// main();
document.addEventListener("DOMContentLoaded", main);
""".strip()

    opaque_container_css = """

:root {{
    --background-color: #ffffff; /* Default background color */
}}


div[data-testid="stVerticalBlockBorderWrapper"]:has(div.opaque-container-{id}):not(:has(div.not-opaque-container)) div[data-testid="stVerticalBlock"]:has(div.opaque-container-{id}):not(:has(div.not-opaque-container)) > div[data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: var(--background-color);
    width: 100%;
}}



div[data-testid="stVerticalBlockBorderWrapper"]:has(div.opaque-container-{id}):not(:has(div.not-opaque-container)) div[data-testid="stVerticalBlock"]:has(div.opaque-container-{id}):not(:has(div.not-opaque-container)) > div[data-testid="element-container"] {{
    display: none;
}}


div[data-testid="stVerticalBlockBorderWrapper"]:has(div.not-opaque-container):not(:has(div[class^='opaque-container-'])) {{
    display: none;
}}
""".strip()

    with fixed_container:
        opaque_container = st.container()
        non_opaque_container = st.container()
        with opaque_container:
            html(f"<script>{opaque_container_js}</script>", scrolling=False, height=0)
            st.markdown(
                f"<style>{opaque_container_css.format(id=key)}</style>",
                unsafe_allow_html=True)
            st.markdown(
                f"<div class='opaque-container-{key}'></div>",
                unsafe_allow_html=True,
            )
        with non_opaque_container:
            st.markdown(
                "<div class='not-opaque-container'></div>",
                unsafe_allow_html=True,
            )

        return opaque_container.container(height=height, border=border)


def scan_templates(package, folder_name):
    templates_path = resources.files(package) / folder_name
    if not templates_path.exists():
        return {"scripts": [], "templates": []}

    scripts = [
        f.name[7:-9] for f in templates_path.glob("script_*.template")
    ]
    templates = [
        f.name[9:-13] for f in templates_path.glob("template_*.template")
    ]
    return {"scripts": scripts, "templates": templates}


package_name = "asreviewcontrib.makita"
folder_name = "templates"
available_files = scan_templates(package_name, folder_name)
st.set_page_config(layout="wide")

# Sidebar Configuration
st.sidebar.title("Makita Configuration")
task = st.sidebar.radio("Choose a task:", ["Template Rendering", "Add Scripts"])

# Main Page
st.title("ASReview Makita Tool")

command_output = ""

if task == "Template Rendering":
    st.header("Template Rendering")

    # Inputs for template rendering
    template_name = st.selectbox(
        "Template Name", available_files["templates"] or ["No templates found"]
    )
    source_folder = st.text_input("Source Folder", Path.cwd() / "data")
    project_folder = st.text_input("Project Folder", Path.cwd() / "project-folder")
    job_file_name = st.text_input("Job File Name (optional)", "")
    custom_template = st.text_input("Custom Template (optional)", "")
    platform = st.selectbox("Platform (optional)", ["", "Windows", "Darwin", "Linux"])
    init_seed = st.number_input("Initial Seed", value=535)
    model_seed = st.number_input("Model Seed", value=165)

    # Other options
    skip_wordclouds = st.checkbox("Skip Wordclouds")
    overwrite = st.checkbox("Overwrite Files")
    stop_if = st.text_input("Stop Condition", "min")
    n_runs = st.number_input("Number of Runs", value=1)
    instances_per_query = st.number_input("Instances Per Query", value=ASREVIEW_CONFIG.DEFAULT_N_INSTANCES)  # noqa: E501

    if template_name == 'arfi':
        n_priors = st.number_input("Number of Priors", value=10)
    else:
        n_priors = None

    if template_name == "multimodel":
        st.subheader("Multi-Model Configurations")
        feature_extractors = st.text_area("[Feature Extractors](https://asreview.readthedocs.io/en/stable/reference.html#module-asreview.models.feature_extraction) (one per line)").split("\n")  # noqa: E501
        classifiers = st.text_area("[Classifiers](https://asreview.readthedocs.io/en/stable/reference.html#module-asreview.models.classifiers) (one per line)").split("\n")  # noqa: E501
        query_strategies = st.text_area("[Query Strategies](https://asreview.readthedocs.io/en/stable/reference.html#module-asreview.models.query) (one per line)").split("\n")  # noqa: E501
        balance_strategies = st.text_area("[Balance Strategies](https://asreview.readthedocs.io/en/stable/reference.html#module-asreview.models.balance) (one per line)").split("\n")  # noqa: E501
        impossible_models = st.text_area("Impossible Models (one Classifier and one Feature Extractor per line)").split("\n")  # noqa: E501
        classifier = None
        feature_extractor = None
        query_strategy = None
        balance_strategy = None
    else:
        st.subheader("Single Model Configuration")
        classifiers = None
        feature_extractors = None
        query_strategies = None
        balance_strategies = None
        impossible_models = None
        feature_extractor = st.text_input("[Feature Extractor](https://asreview.readthedocs.io/en/stable/reference.html#module-asreview.models.feature_extraction)", "")  # noqa: E501
        classifier = st.text_input("[Classifier](https://asreview.readthedocs.io/en/stable/reference.html#module-asreview.models.classifiers)", "")  # noqa: E501
        query_strategy = st.text_input("[Query Strategy](https://asreview.readthedocs.io/en/stable/reference.html#module-asreview.models.query)", "")  # noqa: E501
        balance_strategy = st.text_input("[Balance Strategy](https://asreview.readthedocs.io/en/stable/reference.html#module-asreview.models.balance)", "")  # noqa: E501

        # Validate single model inputs
        if " " in classifier:
            st.error("Classifier field should only contain one model name without spaces.")  # noqa: E501
        if " " in feature_extractor:
            st.error("Feature Extractor field should only contain one model name without spaces.")   # noqa: E501
        if " " in query_strategy:
            st.error("Query Strategy field should only contain one model name without spaces.")   # noqa: E501
        if " " in balance_strategy:
            st.error("Balance Strategy field should only contain one model name without spaces.")   # noqa: E501


elif task == "Add Scripts":
    st.header("Add Scripts")
    script_name = st.selectbox(
        "Script Name", available_files["scripts"] or ["No scripts found"]
    )
    add_all = st.checkbox("Add All Scripts")
    scripts_folder = st.text_input("Project Folder path", Path.cwd())

# Sticky footer with the generate button and output
with st_fixed_container(mode="sticky", position="bottom", border=True, key="footer"):
    generate_button = st.button("Generate Command", use_container_width=True)
    if generate_button:
        if task == "Template Rendering":
            command_output = f"asreview makita template {template_name}"
            if job_file_name:
                command_output += f" --job_file {job_file_name}"
            if source_folder:
                command_output += f" --source \"{source_folder}\""
            if project_folder:
                command_output += f" --project_folder \"{project_folder}\""
            if custom_template:
                command_output += f" --template {custom_template}"
            if platform not in ("", None):
                command_output += f" --platform {platform}"
            if init_seed != 535:
                command_output += f" --init_seed {init_seed}"
            if model_seed != 165:
                command_output += f" --model_seed {model_seed}"
            if skip_wordclouds:
                command_output += " --skip_wordclouds"
            if overwrite:
                command_output += " --overwrite"
            if stop_if != 'min':
                command_output += f" --stop_if {stop_if}"
            if n_runs != 1:
                command_output += f" --n_runs {n_runs}"
            if n_priors not in (10, None):
                command_output += f" --n_priors {n_priors}"
            if instances_per_query != ASREVIEW_CONFIG.DEFAULT_N_INSTANCES:
                command_output += f" --instances_per_query {instances_per_query}"
            if feature_extractor:
                command_output += f" --feature_extractor {feature_extractor}"
            if classifier:
                command_output += f" --classifier {classifier}"
            if query_strategy:
                command_output += f" --query_strategy {query_strategy}"
            if balance_strategy:
                command_output += f" --balance_strategy {balance_strategy}"
            if feature_extractors and any(fe.strip() for fe in feature_extractors):
                command_output += f" --feature_extractors {' '.join(feature_extractors)}"  # noqa: E501
            if classifiers and any(c.strip() for c in classifiers):
                command_output += f" --classifiers {' '.join(classifiers)}"
            if query_strategies and any(qs.strip() for qs in query_strategies):
                command_output += f" --query_strategies {' '.join(query_strategies)}"
            if balance_strategies and any(bs.strip() for bs in balance_strategies):
                command_output += f" --balance_strategies {' '.join(balance_strategies)}"  # noqa: E501
            if impossible_models and any(im.strip() for im in impossible_models):
                command_output += f" --impossible_models {' '.join(impossible_models)}"
        elif task == "Add Scripts":
            command_output = "asreview makita add-script"
            if add_all:
                command_output += " --all"
            elif script_name:
                command_output += f" {script_name}"
            if scripts_folder:
                command_output += f" --output \"{Path(scripts_folder) / 'scripts'}\""  # noqa: E501

    st.subheader("Makita (Make It Automatic) Command:")
    st.code(command_output or "No command generated yet", language="powershell")
