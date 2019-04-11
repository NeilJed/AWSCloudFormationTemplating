# AWS CloudFormation Templating Exercise

# About

Small Python Exercise in using Troposphere plus Python to automate [AWS CloudFormation](https://aws.amazon.com/cloudformation) template creation.

The concept is to support "configuration as code" in that templates can be defined as code or files and thus version controlled. The Python script serves as a framework for loading in the template and the customisation data to populate it with and outputing a JSON CloudFront configuration file.

# Exercise features

- Uses JSON Jinja2 (.j2) or Python (.py) templates that use Troposphere.
- Currently uses a single custom parameter (Environment name) for each template but can easily support more.
- Outputs CloudFormation config as JSON.

# Requirements

- Written with Python 3.7
- Requires [Troposphere](https://github.com/cloudtools/troposphere) and [Jinja2](http://jinja.pocoo.org/)

# Usage

```
usage: cftest.py [-h] template outfile environment

positional arguments:
  template     Input template file in Python or Jinja2 format
  outfile      Output JSON config file
  environment  Name of the custom environment name used in the config

optional arguments:
  -h, --help   show this help message and exit
```

## Example

```
$ cftest.py templates/stack.py output.json Production
```

This will use the Python `templates/stack.py` template, write the configuration to `output.json` and use ""Production"" as the environment name inserted into the template.


# Templates

## Customisation Data

For templates, data to be used for customisation is held in the `custom_data` dictionary of key/value pairs.
In the example templates we only have one actual customisable parameter (Environment name) so it's just passed from the command line.

However, it should be trivial to populate this data from a JSON file to add more data.

## Jinja2

Templates using Jinja2 are just tagged CloudFormation JSON files. The custom_data structure is passed to the renderer to populate the template.

## Python

Templates using Python basically use code to create the template. In the included example we're using Troposphere to build the configuration.

Python templates requre a function called `execute_template(custom_data)` which is called once the template is loaded. This function should then create an instance of your template class and return its output as JSON.

In the example, our template has a single class which performs all the creation steps in the `__init__` function and creates CloudFormation elements using specific functions.



