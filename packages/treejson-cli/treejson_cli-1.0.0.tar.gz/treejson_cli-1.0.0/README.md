# Abstract
It shows the nested directory structure in JSON or YAML.

Japanse document is [here](docs/README_JP.md).

# How to install
`pip install treejson-cli`

## Package Dependencies

The following packages may not work properly if they are not installed:

- [PyYAML](https://pypi.org/project/PyYAML/): Most popular YAML parser for Python.

# How to run
`treejson <directory>`

The directory structure is compiled into JSON and output to standard output.

## Options

Detail document is [here](docs/formal_document.md).

`[-h|--help]`

Shows help message.

`[-v|--version]`

Shows version message.

`[-y|--yaml]`

Outputs as a YAML format.

`[-a|-all]`

Visits hidden file.

`[-d|--depth] <depth>`

Specifies the depth of tree oftraversal.

If depth=0, it shows current directory.

`[-f|--file] <output_file>`

Outputs as a JSON or YAML file.

## Examples
- `treejson tests/sample`
  ```
  {'sample': [{'parent01': [{'child01_01': ['grandchild01.txt']}, {'child01_02': ['grandchild02.txt']}, 'child01_03.txt']}, {'parent02': [{'child02_01': ['grandchild02_01.txt']}]}]}
  ```
- `treejson tests/sample -f tests/output.json`

  [tests/output.json](tests/output.json)

- `treejson tests/sample -yf tests/output.yaml`

  [tests/output.yaml](tests/output.yaml)
