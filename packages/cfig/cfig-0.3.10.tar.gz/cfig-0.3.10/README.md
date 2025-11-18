<div align="center">
<img alt="" src="https://forge.steffo.eu/steffo/cfig/raw/branch/main/.media/icon-512.png" height="128" style="border-radius: 100%;">
<hgroup>
<h1>Cfig</h1>
<p>Configuration helper for Python</p>
</hgroup>
</div>

## Example

```python
import cfig

config = cfig.Configuration()

@config.required()
def MAX_USERS(val: str) -> int:
    """The maximum number of users that will be able to login to this application."""
    try:
        return int(val)
    except (ValueError, TypeError):
        raise cfig.InvalidValueError("Not an int.")

if __name__ == "__main__":
    config.cli()
```

```console
$ python -m myproject.mydefinitionmodule
===== Configuration =====

MAX_USERS       → Required, but not set.
The maximum number of users that will be able to login to this application.

===== End =====

```

See the [quickstart guide] for more information.

[quickstart guide]: https://artifacts.steffo.eu/steffo/cfig/v0.3.9/docs/quickstart.html#

## Why?

To make containerizing applications less of a pain.

## Links

### Tools

<a href="https://www.python.org/">
    <img alt="Written in Python" title="Written in Python" src="https://img.shields.io/badge/language-python-3775a9" height="30px">
</a>
&hairsp;
<a href="https://www.sphinx-doc.org/en/master/">
    <img alt="Prose with Sphinx" title="Prose with Sphinx" src="https://img.shields.io/badge/prose-sphinx-0a507a" height="30px">
</a>
&hairsp;
<a href="https://docs.pytest.org/en/stable/">
    <img alt="Testing with pytest" title="Testing with pytest" src="https://img.shields.io/badge/testing-pytest-00a0e4" height="30px">
</a>

### Packaging

<a href="https://pypi.org/project/cfig">
    <img alt="Available on PyPI" title="Available on PyPI" src="https://img.shields.io/pypi/v/cfig?label=pypi&color=ffd242" height="30px">
</a>
&hairsp;
<a href="https://forge.steffo.eu/steffo/-/packages/pypi/cfig">
    <img alt="Available on Forgejo Packages" title="Available on Forgejo Packages" src="https://img.shields.io/badge/forgejo%20packages-latest-ff6600" height="30px">
</a>

### Documentation

<a href="https://artifacts.steffo.eu/steffo/cfig/">
    <img alt="Documentation available" title="Documentation available" src="https://img.shields.io/website?url=https%3A%2F%2Fartifacts.steffo.eu%2Fsteffo%2Fcfig%2F&up_color=175d36&up_message=available&down_message=error&label=documentation" height="30px">
</a>
&hairsp;
<a href="https://opensource.org/license/MIT">
    <img alt="Licensed under MIT license" title="Licensed under MIT license" src="https://img.shields.io/badge/license-MIT-3da638" height="30px">
</a>

### Development

<a href="https://forge.steffo.eu/steffo/cfig">
    <img alt="Code repository" title="Code repository" src="https://img.shields.io/gitea/last-commit/steffo/cfig?gitea_url=https%3A%2F%2Fforge.steffo.eu&color=374351" height="30px">
</a>
&hairsp;
<a href="https://forge.steffo.eu/steffo/cfig/releases">
    <img alt="Releases" title="Releases" src="https://img.shields.io/gitea/v/release/steffo/cfig?gitea_url=https%3A%2F%2Fforge.steffo.eu&label=last+release&color=374351" height="30px">
</a>
&hairsp;
<a href="https://forge.steffo.eu/steffo/cfig/issues">
    <img alt="Issues" title="Issues" src="https://img.shields.io/gitea/issues/open/steffo/cfig?gitea_url=https%3A%2F%2Fforge.steffo.eu&label=issues&color=374351" height="30px">
</a>
&hairsp;
<a href="https://forge.steffo.eu/steffo/cfig/pulls">
    <img alt="Pull requests" title="Pull requests" src="https://img.shields.io/gitea/pull-requests/open/steffo/cfig?gitea_url=https%3A%2F%2Fforge.steffo.eu&color=374351" height="30px">
</a>
