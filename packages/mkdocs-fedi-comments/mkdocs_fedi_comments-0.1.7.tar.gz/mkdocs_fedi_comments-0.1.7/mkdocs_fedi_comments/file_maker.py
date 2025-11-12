import os

from mkdocs.structure.files import File


file_base_path = os.path.dirname(os.path.abspath(__file__))


def logo_file(config):
    return File(
        "FediverseLogo.svg",
        file_base_path,
        os.path.join(config["site_dir"], "assets/images"),
        config["use_directory_urls"],
    )


def javascript_file(config):
    return File(
        "comments.js",
        os.path.join(file_base_path, "assets/dist"),
        os.path.join(config["site_dir"], "assets/javascript"),
        config["use_directory_urls"],
    )
