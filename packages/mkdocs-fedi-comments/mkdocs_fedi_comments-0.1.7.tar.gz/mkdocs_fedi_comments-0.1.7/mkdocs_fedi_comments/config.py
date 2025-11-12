from mkdocs.config import base, config_options


class MkdocsFediCommentsConfig(base.Config):
    base_path = config_options.Type(str, default="")
    actor = config_options.Optional(
        config_options.DictOfItems(config_options.Type(str))
    )
