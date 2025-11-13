<div align="center">
<img alt="" src="https://forge.steffo.eu/steffo/telebulk/raw/branch/main/.media/icon-512.png" height="128" style="border-radius: 100%;">
<hgroup>
<h1>Telebulk</h1>
<p>Execute actions on multiple Telegram users or groups</p>
</hgroup>
</div>

## Actions

New actions are added to this tool as needed.  
Because of that, functionality is very limited at the moment.  
Feel free to request any new actions though!

### Available actions list

- Kick (and Unban)

## Usage examples

<details>
<summary>Kick a single user from a single group</summary>

```fish
telebulk --user='12345' --group='67890' --kick
```

</details>

<details>
<summary>Unban a user from all group IDs contained in a file</summary>

```fish
#!/usr/bin/env fish
telebulk --user='12345' --group=(cat unban_groups.txt) --kick
```

</details>

## Links

### Tools

<a href="https://www.python.org/">
    <img alt="Written in Python" title="Written in Python" src="https://img.shields.io/badge/language-python-3775a9" height="30px">
</a>

### Packaging

<a href="https://pypi.org/project/telebulk">
    <img alt="Available on PyPI" title="Available on PyPI" src="https://img.shields.io/pypi/v/telebulk?label=pypi&color=ffd242" height="30px">
</a>
&hairsp;
<a href="https://forge.steffo.eu/steffo/-/packages/pypi/telebulk">
    <img alt="Available on Forgejo Packages" title="Available on Forgejo Packages" src="https://img.shields.io/badge/forgejo%20packages-latest-ff6600" height="30px">
</a>

### Documentation

<a href="https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12">
    <img alt="Licensed under EUPL-1.2" title="Licensed under EUPL-1.2" src="https://img.shields.io/badge/license-EUPL--1.2-003399" height="30px">
</a>

### Development

<a href="https://forge.steffo.eu/steffo/telebulk">
    <img alt="Code repository" title="Code repository" src="https://img.shields.io/gitea/last-commit/steffo/telebulk?gitea_url=https%3A%2F%2Fforge.steffo.eu&color=374351" height="30px">
</a>
&hairsp;
<a href="https://forge.steffo.eu/steffo/telebulk/releases">
    <img alt="Releases" title="Releases" src="https://img.shields.io/gitea/v/release/steffo/telebulk?gitea_url=https%3A%2F%2Fforge.steffo.eu&label=last+release&color=374351" height="30px">
</a>
&hairsp;
<a href="https://forge.steffo.eu/steffo/telebulk/issues">
    <img alt="Issues" title="Issues" src="https://img.shields.io/gitea/issues/open/steffo/telebulk?gitea_url=https%3A%2F%2Fforge.steffo.eu&label=issues&color=374351" height="30px">
</a>
&hairsp;
<a href="https://forge.steffo.eu/steffo/telebulk/pulls">
    <img alt="Pull requests" title="Pull requests" src="https://img.shields.io/gitea/pull-requests/open/steffo/telebulk?gitea_url=https%3A%2F%2Fforge.steffo.eu&color=374351" height="30px">
</a>
