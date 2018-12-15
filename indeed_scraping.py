from bs4 import BeautifulSoup
from geonames_api_username import username
from datetime import datetime
import requests
import csv
import json
import psycopg2
import psycopg2.extras
import re


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG = True

class Cache:
    def __init__(self, filename):
        """Load cache from disk, if present"""
        self.filename = filename
        try:
            with open(self.filename, 'r') as cache_file:
                cache_json = cache_file.read()
                self.cache_diction = json.loads(cache_json)
        except:
            self.cache_diction = {}

    def _save_to_disk(self):
        """Save cache to disk"""
        with open(self.filename, 'w') as cache_file:
            json.dump(self.cache_diction, cache_file, indent = 4)

    def _has_entry_expired(self, timestamp_str, expire_in_days):
        """Check if cache timestamp is over expire_in_days old"""

        # gives current datetime
        now = datetime.now()

        # datetime.strptime converts a formatted string into datetime object
        cache_timestamp = datetime.strptime(timestamp_str, DATETIME_FORMAT)

        # subtracting two datetime objects gives you a timedelta object
        delta = now - cache_timestamp
        delta_in_days = delta.days


        # now that we have days as integers, we can just use comparison
        # and decide if cache has expired or not
        if delta_in_days > expire_in_days:
            return True # It's been longer than expiry time
        else:
            return False

    def get(self, identifier):
        """If unique identifier exists in the cache and has not expired, return the data associated with it from the request, else return None"""
        identifier = identifier.upper() # Assuming none will differ with case sensitivity here
        if identifier in self.cache_diction:
            data_assoc_dict = self.cache_diction[identifier]
            if self._has_entry_expired(data_assoc_dict['timestamp'],data_assoc_dict['expire_in_days']):
                if DEBUG:
                    print("Cache has expired for {}".format(identifier))
                # also remove old copy from cache
                del self.cache_diction[identifier]
                self._save_to_disk()
                data = None
            else:
                data = data_assoc_dict['values']
        else:
            data = None
        return data

    def set(self, identifier, data, expire_in_days):
        """Add identifier and its associated values (literal data) to the cache, and save the cache as json"""
        identifier = identifier.upper() # make unique
        self.cache_diction[identifier] = {
            'values': data,
            'timestamp': datetime.now().strftime(DATETIME_FORMAT),
            'expire_in_days': expire_in_days
        }

        self._save_to_disk()


indeed_baseurl = "https://www.indeed.com/jobs?"
geonames_baseurl = "http://api.geonames.org/postalCodeSearchJSON?"
skillset = {} # a dictionary that stores all the skills and the number of times they appear
job_names = [] # a list that stores all the nonrepetitive job titles
job_classes = [] # a list that stores all the nonrepetitive job classes


class Job():
    def __init__(self, title, company, skills, url, city=None, state=None):
        self.title = title
        self.company = company
        self.skills = skills
        self.url = url
        self.city = city
        self.state = state

        self.lat = None
        self.lng = None

    def __str__(self):
        return "{} ({}): {}, {}".format(self.title, self.company, self.city, self.state)


# load the skills from the csv file into a blank dictionary
def load_skills():
    with open("skills.csv", encoding='utf-8-sig') as skills_csv:
        skills = list(csv.reader(skills_csv, delimiter = ","))
    for skill in skills:
        skillset[skill[0]] = 0


# Use the passed base url, parameters dictionary, and private keys list to generate
# and return a String that can be used as the unique key for the JSON format caching file
def cache_key_generator(baseurl, params_dict, private_keys=["key"]):
    alphabetized_keys = sorted(params_dict.keys())
    params_pairs = []
    for key in alphabetized_keys:
        if key not in private_keys:
            params_pairs.append("{}-{}".format(key, params_dict[key]))
    return baseurl + "_".join(params_pairs)


# Get the HTML format job postings either from the caching file or the web
# given the passed jobs batch number and return the job postings data formatted
# as a BeautifulSoup object
def get_job_postings(jobs_batch_num):
    print("Processing the {}/1000th batch of jobs".format(jobs_batch_num + 10))
    # generate the parameters dictionary that can be used to get the HTML format
    # job postings either from the caching file or the web
    params_dict = {"q": "data intern", "l": "United States"}
    if jobs_batch_num != 0:
        params_dict["start"] = jobs_batch_num

    # check the caching file first to see whether the data is already on hand
    cache_key = cache_key_generator(indeed_baseurl, params_dict)
    cache = Cache("job_postings.json")
    job_postings_html = cache.get(cache_key)

    # get the job posting data from the web if the data is not on hand
    # and cache the data afterward
    if not job_postings_html:
        job_postings_html = requests.get(indeed_baseurl, params = params_dict).text
        cache.set(cache_key, job_postings_html, 15)

    # return the job postings data formatted as a BeautifulSoup object
    return BeautifulSoup(job_postings_html, 'html.parser')


# Get the HTML format single posting detail either from the caching file or the web
# given the passed url and return the detail of that posting formatted
# as a BeautifulSoup object
def get_single_posting(url):
    cache = Cache("detail_pages.json")
    posting = cache.get(url)

    if not posting:
        posting = requests.get(url).text
        cache.set(url, posting, 15)

    return BeautifulSoup(posting, 'html.parser')


# Get the JSON format geolocation infomation either from the caching file or the
# GeoNames API given the passed city name and return the latitude and longitude
# of that city in a tuple
def get_geo_data(city):
    params_dict = {"placename": city, "username": username, "country": "us", "maxRows": 1}

    cache_key = cache_key_generator(geonames_baseurl, params_dict)
    cache = Cache("geo_info.json")
    geo_info = cache.get(cache_key)

    if not geo_info:
        geo_info = json.loads(requests.get(geonames_baseurl, params = params_dict).text)
        cache.set(cache_key, geo_info, 100)

    try:
        lat = geo_info['postalCodes'][0]['lat']
        lng = geo_info['postalCodes'][0]['lng']
    except:
        lat = lng = None

    return lat, lng


# Process the data on the single job postings webpage and store the data
# in the Job class
def process_job_postings(raw_data):
    # find all job postings on the page
    job_postings = raw_data.find_all("div", class_ = "jobsearch-SerpJobCard")

    # find the detailed information for each job posting
    for job_posting in job_postings:
        try:
            name = job_posting.find("a", attrs = {'data-tn-element': "jobTitle"}).text
            if name not in job_names:
                job_names.append(name)

                # exclude the job postings related to software engineering
                if "software engineer" not in name.lower():
                    print("!!!!!!!" + name)
                    company_name = job_posting.find("span", class_ = "company").text.strip()
                    location = job_posting.find(class_ = "location").text
                    location_split = location.split(",")
                    if len(location_split) > 1:
                        city = location.split(",")[0]
                        state = location.split(",")[1][1:3]

                    else:
                        city = state = None
                    url = "https://www.indeed.com" + job_posting.find("a", attrs = {'data-tn-element': "jobTitle"})['href']
                    posting = get_single_posting(url).find("div", class_ = "jobsearch-JobComponent-description").text.lower()

                    skills_for_single_posting = []
                    for skill in skillset:
                        if skill == 'r' or skill == 'aws':
                            if re.search("([\.\,\s]|^)" + skill + "($|[\.\,\s])", posting):
                                skillset[skill] += 1
                                skills_for_single_posting.append(skill)
                        else:
                            if skill in posting:
                                skillset[skill] += 1
                                skills_for_single_posting.append(skill)
                    if len(skills_for_single_posting) > 0:
                        job = Job(name, company_name, skills_for_single_posting, url, city, state)
                        job_classes.append(job)
                        print(str(job))

        except:
            pass

    print("-" * 100)

# Scrape all the data intern job postings in the United States from Indeed.com,
# process the data, and store the data into the database
def indeed_scrape_and_store():
    jobs_batch_num = 0
    while jobs_batch_num <= 990: # that's the end of all pages
        # scrape the single page
        raw_data = get_job_postings(jobs_batch_num)
        # process data on the webpage and add it to the database
        process_job_postings(raw_data)
        # update the number for a new batch of job postings
        jobs_batch_num += 10


    # try to make the database connection
    try:
        conn = psycopg2.connect("dbname='job_postings' user=") # No password on the databases yet -- wouldn't want to save that in plain text, anyway
        # Remember: need to, at command prompt or in postgres GUI: createdb test507_music (or whatever db name is in line ^)
        print("Success connecting to database")
    except:
        print("Unable to connect to the database. Check server and credentials.")
        exit() # stop running the program if there is no database connection

    cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # create a table called data_jobs in the job_postings database
    cur.execute("DROP TABLE IF EXISTS data_jobs")
    cur.execute('''CREATE TABLE IF NOT EXISTS data_jobs(
    job_title VARCHAR(64) PRIMARY KEY, company_name VARCHAR(64), city VARCHAR(64),
    state VARCHAR(64), latitude float(18), longitude float(18), url TEXT, skills VARCHAR(1280))''')

    for job in job_classes:
        if job.city != None:
            job.lat, job.lng = get_geo_data(job.city)
        query = """INSERT INTO data_jobs(job_title, company_name, city, state, latitude, longitude, url, skills) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"""
        print("insert")
        cur.execute(query + " ON CONFLICT DO NOTHING",(job.title, job.company, job.city, job.state, job.lat, job.lng, job.url, job.skills,))

    conn.commit()
