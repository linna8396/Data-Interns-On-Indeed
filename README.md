*Linna Qiao, University of Michigan, School of Information, Data Science*

# Project Overview
This project scrapes Indeed.com for all job postings related to data internships, which include information about the job title, company name, salary, region, URL, and skills required for each job posting. The gathered pieces of data will then be stored into a database and also into a dictionary that stores the skill names as keys and their occurrences as values. Finally, the program will generate a map showing all job postings across the U.S. and also a bar chart that visualizes all the data related skills and their occurrences, sorted from high to low.

## Sample Visualization
### Data Interns Across the U.S.
![jobs_across_US](jobs_across_US.png?raw=true "Data Interns Across the U.S.")
### Data Related Skills & Occurrences
![skills_importance](skills_importance.png?raw=true "Data Related Skills & Occurrences")


# Skills and Tools Involved
1. Webpage scraping (Indeed.com) and processing using BeautifulSoup
2. Used the GeoNames API to get geolocation data for job postings
3. Used PostgreSQL to build the database, store the data, and run queries for future analysis
4. Processed and analyzed data from webpages and the API to obtain meaningful results
5. Used Plot.ly to visualize the analyzed results


# Introduction to the Files
There are a total of 3 python files in this project. These files are:
*  `geonames_api_username.py`
*  `indeed_scraping.py`
*  `visualization.py`

Of those 3 files:

`visualization.py` is the only file you need to run to get the final visualizations from the scraped data;

`indeed_scraping.py` is the supporting file that scrapes and processes the data from Indeed.com;

`geonames_api_username.py` is the file that stores the key for the Geonames API.

The detail about how to use `geonames_api_username.py` will be talked in the *Instructions for Dependencies* section.

The picture files `jobs_across_US.png` and `skills_importance.png` are the examples of the final visualization, with each of them showing all data intern postings across the U.S. and also all the data related skills and their occurrences, separately.

The `skills.csv` file stores all the data skills that are used in the program.

There are also 4 JSON files that will be generated during you run the main file. These files are just used for caching purpose and will not affect running the main file in any way.


# Instructions for Dependencies

### 1. Plot.ly

Plotly is a graphing service that you can work with from Python. It allows you to create many different kinds of graphs, including the ones we will see in this program.

First, you need to go to the official site of Plot.ly: https://plot.ly/ and create an account. You also need to make sure to click on the confirmation email that Plot.ly sends after you create an account, since without this you won’t be able to get an API key that will be needed in this program.

To be able to use Plot.ly from your python programs, you will need to install the Plot.ly module and set up your installation with your private API key. Here are the instructions:

#### 1) Installation
To install Plotly's python package, use the package manager pip inside your terminal.
If you don't have pip installed on your machine, click https://pip.pypa.io/en/latest/installing/ for pip's installation instructions.

`$ pip install plotly`

or

`$ sudo pip install plotly`

#### 2) Set Credentials
After installing the Plot.ly package, you're ready to fire up python:

`$ python`

and set your credentials:

```python
import plotly
plotly.tools.set_credentials_file(username='DemoAccount', api_key='lr1c37zw81')
```

You'll need to replace 'DemoAccount' and 'lr1c37zw81' with your Plotly username and API key.
Find your API key here https://plot.ly/Auth/login/?next=%2Fsettings%2Fapi.

The initialization step places a special .plotly/.credentials file in your home directory. Your ~/.plotly/.credentials file should look something like this:

```JSON
{
    "username": "DemoAccount",
    "stream_ids": ["ylosqsyet5", "h2ct8btk1s", "oxz4fm883b"],
    "api_key": "lr1c37zw81"
}
```

### 2. BeautifulSoup
Since you should already set up `pip` when you finish setting up the Plot.ly. You can also use `pip` to install BeautifulSoup if you don't have it on your computer.

Open your terminal window and type in:

`pip install beautifulsoup4`

and you are all set!

### 3. GeoNames API
1. Visit http://www.geonames.org/login, which is the homepage of GeoNames, and use the "or create a new user account" part to create a new account.
2. Get the confirmation email and activate your account. Please make sure you perform this step, or you cannot get the access for the API.
3. Click your user name on the top right corner on the activation page.
4. Find the "Free Web Services" part on the user page and click "Click here to enable" to activate your API access at the bottom of the page.
5. Copy and paste your username to the `geonames_api_username.py` file.

Now you are good to use the GeoNames API!

### 4. PostgreSQL
(sources credit: https://paper.dropbox.com/doc/Postgres-Database-setup--ATs59yxJEzscphEh38aecIGcAg-N4y2qlUr5BeP1X42Z5suc)
You need to install PostgreSQL on your computer to interact with the database in this program. Here are the steps:

#### 1) Get homebrew
Go to this link: https://brew.sh/
Copy the one line of code that they have on that page, which is:

    `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

Open your Terminal and paste that entire line in. It will run for a while.
It may prompt you for your computer password (or it may not).

#### 2) Install PostgreSQL
First, we use the Homebrew package manager to install the postgresql database. You need to type the following command in your Terminal:

    `brew install postgres`

Then run the following command to start the database server:

    `pg_ctl -D /usr/local/var/postgres start`

after you do this, you may need to open a new Terminal window. But this server will run in the background.

You may need to run that command again in the future — any time you restart your computer and want to use Postgres again (or sometimes the server seems to randomly shut down. No harm done — but need to start it again before relying on a Postgres database! So you’ll want to keep that line close. I always have to look it up myself).

Useful commands for starting/stopping psql db server (in general) — you may want to refer to these in future:
    `pg_ctl -D /usr/local/var/postgres status` # to check status
    `pg_ctl -D /usr/local/var/postgres start` # to start the server
    `pg_ctl -D /usr/local/var/postgres stop` # to stop the server

#### 3) Database Setup
Now you are ready to setup the database we are going to use in this program.
1. Enter the folder that holds this project in the Terminal.
2. Type in and run `createdb job_postings` in the Terminal. YOU MUST ENTER THE EXACT COMMAND.

and you are all set for setting up the database!

#### 4) Interact with Database Using Python
Depending on what you already have installed, you also may need to

    conda install psycopg2

or

    pip install psycopg2 / pip3 install psychopg2

That is the Python library that allows you to interact with PostgreSQL databases in a Python script. And you are all set!


# Now you have grasped all the knowledge needed to run this program! Feel free to explore it and get the insightful result!
