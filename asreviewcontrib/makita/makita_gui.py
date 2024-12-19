from pathlib import Path

import streamlit as st
from asreview import config as ASREVIEW_CONFIG

from asreviewcontrib.makita.st_fixed_container import st_fixed_container


def scan_templates(folder_path):
    folder = Path(folder_path)
    if not folder.exists():
        return {"scripts": [], "templates": []}

    scripts = [
        f.name[7:-9] for f in folder.glob("script_*.template")
    ]
    templates = [
        f.name[9:-13] for f in folder.glob("template_*.template")
    ]
    return {"scripts": scripts, "templates": templates}


templates_folder = "asreviewcontrib/makita/templates"
available_files = scan_templates(templates_folder)
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
