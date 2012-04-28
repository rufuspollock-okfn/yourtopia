Web app for crowdsourcing preferences about index weighting such as the Human
Development Index. Powers [YourTopia][] site - Global Development beyond GDP.

[YourTopia]: http://yourtopia.net/

## Installing

1. Install Python and pip

2. Install the requirements into a virtualenv:

      virtualenv ~/venv-yourtopia
      pip install -e . 

3. Run the web application:

      python yourtopia/web.py

### Configuration

If you want to modify the default settings:

1. Copy and paste settings\_local.py.tmpl

   * You must locate the file either at settings\_local.py or at a location of
     your choosing and set YOURTOPIA\_SETTINGS environment variable to point to
     your file.

2. Add or amend settings (see instructions in the file)

## Deployment

Use Fabric and the fabfile:

    fab deploy:{service-name}[,{port}] --host ... --user ...

This can be used for both initial deployment and upgrades.

