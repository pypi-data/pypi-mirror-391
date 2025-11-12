---
description: mkdocs_fedi_comment allows commenting from the Fediverse on mkdocs generated sites.
---

# Comments for static sites

Consider a generated static site, e.g. this one. Wouldn't it be nice
if you could comment from the Fediverse on it? Well you can! Just copy
the URL of this page into your Fediverse application search and look
up an object, you can comment on, to add comments here.

## Usage

This package does not enable comments for a mkdocs site by
itself. It requires a server to store comments. More on this in
[technical comments](#technical-comments). For an example, check
out [comments](https://bovine.codeberg.page/comments/).

### Installation

Currently, this plugin needs to be installed from 
[pypi](https://pypi.org/project/mkdocs-fedi-comments/)

```bash
pip install mkdocs-fedi-comments
```

### Configuration

The following shows a minimal configuration file for mkdocs. This configuration
causes links according to [FEP-22b6: Linking an ActivityPub Object to a HTML page and back](https://fediverse.codeberg.page/fep/fep/22b6/) to be created and a component
to be embedded in the output that displays the comments.


```yaml title="mkdocs.yml"
site_url: https://bovine.codeberg.page/mkdocs_fedi_comments
theme:
  - name: material
plugins:
  - fedi-comments:
      base_path: https://comments.bovine.social/
```

#### site_url

Setting site_url is necessary to compute the ids used to make
requests to the comments server. See [link_maker](./reference/link_maker.md).

!!! warning
    Running `mkdocs serve` works with `site_url` not set, but `mkdocs build`
    will fail.

#### plugins.fedi_comments.base_path

`base_path` is the URL your comment tracking system can be reached at.
[comments](https://bovine.codeberg.page/comments/) is an example of
such a system.

### Configuring the actor

The configuration so far enables us to link to a comments tracking
system and retrieve the comments collection from there. This plugin
also provides a mechanism to specify the properties of the
corresponding actor.

```yaml title="mkdocs.yml"
plugins:
  - fedi-comments:
      base_path: https://comments.bovine.social/
      actor:
        name: mkdocs-fedi-comments
        handle: mkdocs_fedi_comments
        summary: This mkdocs plugins provides the ability to allow commenting from the Fediverse through an external service.
        icon: https://bovine.codeberg.org/mkdocs_fedi_comments/assets/icon.png
```

Here the properties `summary` and `icon` would be optional.
These properties will be exposed through the
[fedi-actor.json](./fedi-actor.json) file.

The comment tracking system is informed through the existence of a

```html
<link rel="fedi-actor" 
  href="https://bovine.codeberg.org/mkdocs_fedi_comments/fedi-actor.json" 
  type="application/json">
```

tag of the existence of the `fedi-actor.json` file.

### Disabling for files


As demonstrated on [Page without comments](./nocomment.md), one
can disable comments on certain pages by adding the following
to its header section.

```yaml
---
fedi_comment:
    disable: true
---
```

## Technical comments

As already mentioned earlier, this plugin does not provide functionality
to comment. It just

* provides a link to an object to comment on
* provides functionality to display the comments

For these things to work, one needs a server with a well defined API.
An example of this is [comments](https://bovine.codeberg.page/comments/),
which provides its OpenAPI specification.

One can see this API specification reflected in the [link_maker](./reference/link_maker.md)
used by this package. Similarly, the TypeScript code used to display
comments relies on an [SDK](https://codeberg.org/bovine/-/packages/npm/@bovine%2Fcomments-api/) generated from the OpenAPI document from above.

### Replacing comments

I have started documenting the technical details needed to build
the server component at 
[FEP-136c: Comment Tracking Services](https://bovine.codeberg.page/comments/136c/fep-136c/).

### Working with other themes than mkdocs-material

We use the [overrides mechanism of mkdocs-material](https://squidfunk.github.io/mkdocs-material/customization/?h=overri#extending-the-theme) to inject HTML snippets into
the markup, for the snippets see [overrides](https://codeberg.org/bovine/mkdocs_fedi_comments/src/branch/main/mkdocs_fedi_comments/overrides).

Adapting this plugin to other themes, would require replacing this mechanism.

### Development

* [storybook for the comments component](https://bovine.codeberg.page/mkdocs_fedi_comments/@storybook)