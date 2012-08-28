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

### To Heroku

Note that you will need to install the [Heroku toolbelt](https://toolbelt.heroku.com/) to carry out the `heroku` commands below. In addition, you will need a Heroku account.

#### Create the application on Heroku

*Skip this step if the application is already deployed*

This is heavily based on [this
tutorial](https://devcenter.heroku.com/articles/python#deploy-to-heroku).

    # replace {app-name} with the name of your app
    heroku create {app-name}
    # you may want a larger db (dev is 20k rows)
    heroku addons:add heroku-postgresql:dev
    heroku config:set YOURTOPIA_SETTINGS=/app/heroku_settings.py
    git push heroku master
    heroku ps:scale web=1

To have your db working correctly you may need to work out the right db to connect to e.g.:

    heroku pg:info
    # find the db name available to you
    heroku pg:promote {db-name}

#### To deploy (already created):

Push to heroku git repo:

    git push heroku master

*Note*: if you didn't do the create you will need to add the heroku remote:

    git remote add heroku git@heroku.com:italia-yourtopia.git

#### Adding collaborators:

    heroku sharing:add joe@example.com

#### Setting the domain name

Do the following:

    heroku domains:add {your-domain-name}

Now CNAME your domain to {myapp}.herokuapp.com


### To OKFN servers (deprecated)

Use Fabric and the fabfile:

    fab deploy:{service-name}[,{port}] --host ... --user ...

This can be used for both initial deployment and upgrades.

