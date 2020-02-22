# IFQ

Library to download ilfattoquotidiano.it issues in PDF.

## Usage

```python
from datetime import date
from ifq import Scraper

username = ''  # your ifq username
password = ''  # your ifq password

scraper = Scraper(username, password)

path_to_pdf_file = scraper.download_pdf(date.today())
```

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

> What things you need to install the software and how to install them

You need to install `pipenv` to handle the dependencies.

```
$ pip install pipenv
```

### Installing

> A step by step series of examples that tell you how to get a development env running

Install all the dependencies (prod and dev):

```
$ pipenv install -dev
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Maurizio Branca** - *Initial work* - [zmoog](https://github.com/zmoog)

See also the list of [contributors](https://github.com/your/project/

## License

This project is licensed under the Apache License Version 2.0 - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

A great "thank you!" to the all authors of lxml and requests to creating such a powerful and easy to use tools.
