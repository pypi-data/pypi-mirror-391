# Dexa

<div align="center">

<!-- Project details -->
[![Python support][badge1]][burl1]
[![PyPI Release][badge1a]][burl1]
[![Repository][badge2]][burl2]
[![Releases][badge3]][burl3]
[![Docker][bdocker1]][bdocker2]
[![Licence][blic1]][blic2]
[![Expand your project structure from atoms of code to galactic dimensions.][badge4]][burl4]

<!-- Information on development -->
[![Project type][badge5]][burl5]
[![Project stage][badge6]][burl6]
[![Contributions Welcome][badge7]][burl7]
[![Open issues][badge8]][burl8]
[![Merge Requests][badge9]][burl9]

<!-- Styling policies -->
[![BDD][bbbd1]][bbbd2]
[![Code style: Ruff][badge10]][burl10]
[![Docstrings][bdocstr1]][bdocstr2]
[![Gitmoji][badge11]][burl11]
[![Semantic Line Breaks][badge12]][burl12]

<!-- Development utilities -->
[![Poetry][badge13]][burl13]
[![Pre-commit][badge14]][burl14]
[![Bandit][badge15]][burl15]
[![isort][badge16]][burl16]
[![Editorconfig][badge17]][burl17]

<!-- Open Source benchmarks -->
<!-- UPDATEME by toggling this comment off after replacing your project's index in both anchors below
[![OpenSSF Best Practices][bossf1]][bossf2] -->
<!-- UPDATEME by toggling this comment off after replacing your project's index in both anchors below
[![OSSRank][bossf3]][bossf4] -->

<!-- Quality assurance -->
[![Intended Effort Versioning][badge18]][burl18]
<!-- UPDATEME by toggling this comment off after replacing your project's index in both anchors below
[![Code Quality][bqa1]][bqa2] -->
<!-- UPDATEME by toggling this comment off after replacing your project's index in both anchors below
[![Coverage][badge19]][burl19] -->
[![Pipelines][badge20]][burl20]

_The ultimate terminal RPN calculator_

---

**POWERED BY**

[![Powered by Typer][btyper]][ltyper]
[![Powered by Textual][btextual]][ltextual]
[![Powered by Orbittings][borbittings]][lorbittings]

</div>

## :sunrise_over_mountains: Purpose & Function

**Dexa** is a [Reverse Polish Notation][purpose1] calculator
built for use in the terminal.
It aims to be
the ultimate terminal calculator
for power users,
providing versatile
operations,
quick navigation
and useful customisation options!

This project addresses
the apparent lack of options
for RPN enthusiasts
to perform advanced calculations
in the terminal.
By leveraging tools
from the Python ecosystem,
we hope to provide
a lightweight and modern application
to make RPN calculations
fun and remarkable. :raised_hands:

## :star_struck: Standout Features

We are currently in the
**Planning** stage
of the project,
still defining the scope
of the first milestones
and our development plan.
However, we anticipate
the following features
to be delivered
for users
at some point in the future:

- :zap: Vim-like bindings for navigation;
- :label: A memory stack
  with both
  positional allocation
  and tag-based naming;
- :currency_exchange: Quick dimension conversion tables;
- :art: Customisation options
  for both constants and dimension conversions.

## :inbox_tray: Installation

Use [`pipx`][install1] to install Dexa
in an isolated environment:

```bash
pipx install dexa
```

Then you can run it from the command line:

```bash
dexa --help
```

## :black_joker: How to Use It

You can simply
launch the Dexa
by calling `dexa`
directly.

The top-level command
is also callable
with other options
for fine-grained
control of the application:

> _`dexa [--version | -v] [(--config | -c) <file>]`_
>> **`--version`**
>>
>> **`-v`**
>>
>> Print
>> the current version of the program
>> and exit.
>
>> **`--config`**
>>
>> **`-c`**
>>
>> Specify a custom configuration file
>> to launch the application.

### Manage the Configuration

The `dexa config` command provides
additional subcommands
to manipulate
the settings
for your Dexa installation:

> _`dexa config get [--path <file>] [--secret | -s] KEY`_
>> **`KEY`**
>>
>> The configuration key
>> to be retrieved. **[required]**
>
>> **`--path`**
>>
>> Specify
>> a custom configuration file.
>
>> **`--secret`**
>>
>> **`-s`**
>>
>> Retrieve configuration
>> from the secret manager instead.

> _`dexa config set [--path <file>] [--secret | -s] KEY VALUE`_
>> **`KEY`**
>>
>> The configuration key
>> to be retrieved. **[required]**
>
>> **`VALUE`**
>>
>> The value to be stored
>> with the key. **[required]**
>
>> **`--path`**
>>
>> Specify
>> a custom configuration file.
>
>> **`--secret`**
>>
>> **`-s`**
>>
>> Store configuration
>> in the secret manager instead.

> _`dexa config extend [--path <file>] [--secret | -s] [--create-on-missing | -c] KEY VALUE`_
>> **`KEY`**
>>
>> The configuration key
>> to be extended. **[required]**
>
>> **`VALUE`**
>>
>> The value to be appended
>> to the key. **[required]**
>
>> **`--path`**
>>
>> Specify
>> a custom configuration file.
>
>> **`--secret`**
>>
>> **`-s`**
>>
>> Store configuration
>> in the secret manager instead.
>
>> **`--create-on-missing`**
>>
>> **`-c`**
>>
>> Add the provided value
>> in an array
>> if the setting is not set.
>> Will raise an error
>> otherwise.

> _`dexa config unset [--path <file>] [--secret | -s] KEY`_
>> **`KEY`**
>>
>> The configuration key
>> to be removed. **[required]**
>
>> **`--path`**
>>
>> Specify
>> a custom configuration file.
>
>> **`--secret`**
>>
>> **`-s`**
>>
>> Retrieve configuration
>> from the secret manager instead.

## :reminder_ribbon: Contributing

There are several ways
to contribute to Dexa.
Refer to our [`CONTRIBUTING` guide][burl7]
for all relevant details.

Currently,
we are seeking help
to tackle areas of focus
that are more pressing
to our project's progress
and would make an immediate difference
in helping us achieve our [mission][contributing1].

Here are some key contributions
your can help us with
right now:

- Provide input in [design discussions][contributing2]
  to define the desired features of Dexa.
<!-- DEFINE additional areas of assistance as development progresses -->

## :ship: Releases

You can see
the list of available releases
on the [GitLab Releases][release1] page.

We follow [Intended Effort Versioning][release2] specification,
details can be found in our [`CONTRIBUTING` guide][burl18].

## :shield: Licence

[![Licence][blic1]][blic2]

This project is licenced
under the terms of the **MIT License**.
See [LICENCE][blic2] for more details.

## :page_with_curl: Citation

We provide a [`CITATION.cff`][cite1] file
to make it easier to cite this project
in your paper.

## :women_with_bunny_ears: Similar Projects

- The [`dc`][similar1] command-line program
  is the original RPN terminal calculator,
  created more than 50 years ago
  at Bell Labs;
- [T-REX][similar2] is a RPN calculator
  implemented in Ruby;
- [Squiid][similar3] is
  a modern calculator
  written in Rust
  with support for RPN,
  along with a mathematical expression parser;
- [HP-15C][similar4] is a simulator
  for the iconic scientific calculator
  from Hewlett-Packard.

Also, a great inspiration
for Dexa comes from
the [RealCalc][similar4] Android app,
arguably the best mobile RPN calculator
out there.
Check it out
if you have the chance. :wink:

## Credits [![Expand your project structure from atoms of code to galactic dimensions.][badge4]][burl4]

This project was generated with [Galactipy][burl4].

<!-- Anchors -->

[badge1]: https://img.shields.io/pypi/pyversions/dexa?style=for-the-badge
[badge1a]: https://img.shields.io/pypi/v/dexa?style=for-the-badge&logo=pypi&color=3775a9
[badge2]: https://img.shields.io/badge/GitLab-0B2640?style=for-the-badge&logo=gitlab&logoColor=white
[badge3]: https://img.shields.io/gitlab/v/release/nummertopia%2Fdexa?style=for-the-badge&logo=semantic-release&color=FFCA28
[badge4]: https://img.shields.io/badge/made%20with-galactipy%20%F0%9F%8C%8C-179287?style=for-the-badge&labelColor=193A3E
[badge5]: https://img.shields.io/badge/project%20type-toy-blue?style=for-the-badge
[badge6]: https://img.shields.io/pypi/status/dexa?style=for-the-badge&logo=theplanetarysociety&label=stage
[badge7]: https://img.shields.io/static/v1.svg?label=Contributions&message=Welcome&color=0059b3&style=for-the-badge
[badge8]: https://img.shields.io/gitlab/issues/open/nummertopia%2Fdexa?style=for-the-badge&color=fca326
[badge9]: https://img.shields.io/gitlab/merge-requests/open/nummertopia%2Fdexa?style=for-the-badge&color=6fdac9
[badge10]: https://img.shields.io/badge/code%20style-ruff-261230?style=for-the-badge&labelColor=grey
[badge11]: https://img.shields.io/badge/%F0%9F%98%9C_gitmoji-ffdd67?style=for-the-badge
[badge12]: https://img.shields.io/badge/sembr-FF6441?style=for-the-badge&logo=apmterminals&logoColor=white
[badge13]: https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json&style=for-the-badge
[badge14]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=for-the-badge
[badge15]: https://img.shields.io/badge/security-bandit-yellow?style=for-the-badge
[badge16]: https://img.shields.io/badge/imports-isort-1674b1?style=for-the-badge&labelColor=ef8336
[badge17]: https://img.shields.io/badge/Editorconfig-E0EFEF?style=for-the-badge&logo=editorconfig&logoColor=000
[badge18]: https://img.shields.io/badge/effver-0097a7?style=for-the-badge&logo=semver
<!-- TODO Replace the hash `d5402a91aa7b4234bd1c19b5e86a63be` with your project ID in the "Codacy Badge" section available at https://app.codacy.com/gl/nummertopia/dexa/settings
[badge19]: https://img.shields.io/codacy/coverage/d5402a91aa7b4234bd1c19b5e86a63be?style=for-the-badge&logo=codacy -->
[badge20]: https://img.shields.io/gitlab/pipeline-status/nummertopia%2Fdexa?branch=master&style=for-the-badge&logo=gitlab&logoColor=white&label=master

[burl1]: https://pypi.org/project/dexa/
[burl2]: https://gitlab.com/nummertopia/dexa
[burl3]: https://gitlab.com/nummertopia/dexa/-/releases
[burl4]: https://kutt.it/7fYqQl
[burl5]: https://project-types.github.io/#toy
[burl6]: https://gitlab.com/nummertopia/dexa/-/blob/master/ROADMAP.md#development-stages
[burl7]: https://gitlab.com/nummertopia/dexa/-/blob/master/CONTRIBUTING.md
[burl8]: https://gitlab.com/nummertopia/dexa/-/issues
[burl9]: https://gitlab.com/nummertopia/dexa/-/merge_requests
[burl10]: https://gitlab.com/nummertopia/dexa/-/blob/master/CONTRIBUTING.md#codestyle
[burl11]: https://gitlab.com/nummertopia/dexa/-/blob/master/CONTRIBUTING.md#commit-customs
[burl12]: https://gitlab.com/nummertopia/dexa/-/blob/master/CONTRIBUTING.md#semantic-line-breaks
[burl13]: https://python-poetry.org/
[burl14]: https://gitlab.com/nummertopia/dexa/-/blob/master/.pre-commit-config.yaml
[burl15]: https://bandit.readthedocs.io/en/latest/
[burl16]: https://pycqa.github.io/isort/
[burl17]: https://gitlab.com/nummertopia/dexa/-/blob/master/.editorconfig
[burl18]: https://gitlab.com/nummertopia/dexa/-/blob/master/CONTRIBUTING.md#versioning-customs
[burl19]: https://app.codacy.com/gl/nummertopia/dexa/coverage
[burl20]: https://gitlab.com/nummertopia/dexa/-/pipelines

[blic1]: https://img.shields.io/gitlab/license/nummertopia/dexa?style=for-the-badge
[blic2]: https://gitlab.com/nummertopia/dexa/-/blob/master/LICENCE

<!-- TODO Replace the `100` ID with your project's index at https://www.bestpractices.dev/en
[bossf1]: https://img.shields.io/cii/level/100?style=for-the-badge&logo=linux-foundation&label=openssf%20best%20practices
[bossf2]: https://www.bestpractices.dev/en/projects/100 -->
<!-- TODO Replace the `200` ID with your project's index at https://ossrank.com/
[bossf3]: https://shields.io/endpoint?url=https://ossrank.com/shield/200&style=for-the-badge
[bossf4]: https://ossrank.com/p/200 -->

<!-- TODO Replace the hash `d5402a91aa7b4234bd1c19b5e86a63be` with your project ID in the "Codacy Badge" section available at https://app.codacy.com/gl/nummertopia/dexa/settings
[bqa1]: https://img.shields.io/codacy/grade/d5402a91aa7b4234bd1c19b5e86a63be?style=for-the-badge&logo=codacy
[bqa2]: https://app.codacy.com/gl/nummertopia/dexa/dashboard -->

[btyper]: https://img.shields.io/badge/Typer-black?style=for-the-badge&logo=typer
[ltyper]: https://typer.tiangolo.com/
[btextual]: https://img.shields.io/badge/Textual-272a35?style=for-the-badge&logo=textual
[ltextual]: https://textual.textualize.io/
[borbittings]: https://img.shields.io/badge/orbittings-007A68?style=for-the-badge&logo=orbittings
[lorbittings]: https://gitlab.com/galactipy/orbittings

[purpose1]: https://www.hpmuseum.org/rpn.htm

[install1]: https://pipx.pypa.io/latest/installation/

[contributing1]: https://gitlab.com/nummertopia/dexa/-/blob/master/ROADMAP.md#project-mission
[contributing2]: https://gitlab.com/nummertopia/dexa/-/issues?state=opened&label_name%5B%5D=design%3A%3A%2A&type%5B%5D=issue

[release1]: https://gitlab.com/nummertopia/dexa/-/releases
[release2]: https://jacobtomlinson.dev/effver/

[bdocker1]: https://img.shields.io/gitlab/v/release/nummertopia%2Fdexa?style=for-the-badge&logo=linux-containers&logoColor=C5F4EC&label=image&color=C5F4EC
[bdocker2]: https://gitlab.com/nummertopia/dexa/container_registry

[bdocstr1]: https://img.shields.io/badge/docstrings-numpydoc-4dabcf?style=for-the-badge&labelColor=4d77cf
[bdocstr2]: https://gitlab.com/nummertopia/dexa/-/blob/master/CONTRIBUTING.md#docstring-convention

[bbbd1]: https://img.shields.io/badge/BDD-23D96C?style=for-the-badge&logo=cucumber&logoColor=white
[bbbd2]: https://gitlab.com/nummertopia/dexa/-/blob/master/CONTRIBUTING.md#behaviour-driven-development

[cite1]: https://gitlab.com/nummertopia/dexa/-/blob/master/CITATION.cff

[similar1]: https://www.gnu.org/software/bc/manual/dc-1.05/dc.html
[similar2]: https://github.com/isene/T-REX
[similar3]: https://gitlab.com/ImaginaryInfinity/squiid-calculator/squiid
[similar4]: https://hp-15c-simulator.de/
[similar5]: https://www.quartic-software.co.uk/index.html
