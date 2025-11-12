[![license](https://img.shields.io/badge/license-MIT-brightgreen)](https://spdx.org/licenses/MIT.html)
[![documentation](https://img.shields.io/badge/documentation-html-informational)](https://mk-scaffold.docs.cappysan.dev)
[![pipelines](https://gitlab.com/cappysan/mk-scaffold/badges/main/pipeline.svg)](https://gitlab.com/cappysan/mk-scaffold/pipelines)
[![coverage](https://gitlab.com/cappysan/mk-scaffold/badges/main/coverage.svg)](https://mk-scaffold.docs.cappysan.dev//coverage/index.html)

# mk-scaffold -- make scaffold

A cookiecutter clone. A command-line utility that creates projects from templates.


## Table of contents
1. [Features](#features)  
2. [Installation](#installation)  
3. [Usage](#usage)  
4. [Support & Sponsorship](#support)  
5. [License](#license)  
6. [Links](#links)  


## Features <a name="features"></a>

- Conditional questions.
- Templated answers.
- You don't have to know/write Python code to use.
- Project templates can be in any programming language or markup format:
  Python, JavaScript, Ruby, CoffeeScript, RST, Markdown, CSS, HTML, you name it.
  You can use multiple languages in the same project template.


## Installation <a name="installation"></a>

You can install the latest version from PyPI package repository.

~~~bash
pipx install --force --pip-args="--pre"  mk-scaffold
~~~


## Usage <a name="usage"></a>

Sample command line usage:

~~~bash
mk-scaffold clone git@gitlab.com:cappysan/scaffolds/python-template.git
~~~

Sample scaffold template file `scaffold.yml`:

~~~yml
questions:
  - name: "project_name"
    schema:
      min_length: 1

  - name: "project_short_description"
    schema:
      default: "Lorem ipsum sit dolor amet."
      max_length: 120
~~~


## Support & Sponsorship <a name="support"></a>

You can help support this project, and all Cappysan projects, through the following actions:

- ⭐Star the repository on GitLab, GitHub, or both to increase visibility and community engagement.

- 💬 Join the Discord community: [https://discord.gg/SsY3CAdp4Q](https://discord.gg/SsY3CAdp4Q) to connect, contribute, share feedback, and/or stay updated.

- 🛠️ Contribute by submitting issues, improving documentation, or creating pull requests to help the project grow.

- ☕ Support financially through [Buy Me a Coffee](https://buymeacoffee.com/cappysan), [Patreon](https://www.patreon.com/c/cappysan), [GitHub](https://github.com/sponsors/cappysan), or [Bitcoin (bc1qeq94qyn3vhsc8l38qvuhdxchhm7lr876m6jsdt)](https://addrs.to/pay?token=BTC&address=bc1qeq94qyn3vhsc8l38qvuhdxchhm7lr876m6jsdt&name=cappysan). Your contributions directly sustain ongoing development and maintenance, including server costs.

Your support ensures these projects continue to improve, expand, and remain freely available to everyone.


## License <a name="license"></a>

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Links <a name="links"></a>

  * Documentation: [https://mk-scaffold.docs.cappysan.dev/](https://mk-scaffold.docs.cappysan.dev/)
  * Source code: [https://gitlab.com/cappysan/apps/mk-scaffold](https://gitlab.com/cappysan/apps/mk-scaffold)
  * PyPi: [https://pypi.org/project/mk-scaffold](https://pypi.org/project/mk-scaffold)
  * Discord: [https://discord.gg/SsY3CAdp4Q](https://discord.gg/SsY3CAdp4Q)
