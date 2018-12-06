from bs4 import BeautifulSoup
from caching import Cache
from geonames_api_username import username
import requests
import csv
import json

indeed_baseurl = "https://www.indeed.com/jobs?"
geonames_baseurl = "http://api.geonames.org/postalCodeSearchJSON?"
skillset = {}

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


def process_job_postings(raw_data):
    # find all job postings on the page
    job_postings = raw_data.find_all("div", class_ = "jobsearch-SerpJobCard")

    csvref = open("jobs.csv", "w")
    csvref.write("job_name,company_name,city,state,latitude,longitude,url,skills_required\n")
    # find the detailed information for each job posting
    for job_posting in job_postings:
        # try:
        name = job_posting.find("a", attrs = {'data-tn-element': "jobTitle"}).text
        # exclude the job postings related to software engineering
        if "software engineer" not in name.lower():
            company_name = job_posting.find("span", class_ = "company").text.strip()
            location = job_posting.find(class_ = "location").text
            location_split = location.split(",")
            if len(location_split) > 1:
                city = location.split(",")[0]
                state = location.split(",")[1][1:3]
                lat, lng = get_geo_data(city)
            else:
                city = state = lat = lng = None
            url = "https://www.indeed.com" + job_posting.find("a", attrs = {'data-tn-element': "jobTitle"})['href']
            posting = get_single_posting(url).find("div", class_ = "jobsearch-JobComponent-description").text
            skills_for_single_posting = []
            for skill in skillset:
                if skill in posting:
                    skillset[skill] += 1
                    skills_for_single_posting.append(skill)

        csvref.write('"{}","{}","{}","{}","{}","{}","{}","{}"\n'.format(name, company_name, city, state, lat, lng, url, skills_for_single_posting))
        # except:
        #     pass
    csvref.close()
    print(skillset)
    return None

def indeed_scraping():
    jobs_batch_num = 0
    #while True: # 这个条件记得改
        # scrape这一页
    raw_data = get_job_postings(jobs_batch_num)
    process_job_postings(raw_data)
        # process data

        #jobs_batch_num += 10 # update the number for a new batch of job postings
load_skills()
indeed_scraping()


# 在网上获取数据的debug部分
# def requestURL(baseurl, params = {}):
#     # This function accepts a URL path and a params diction as inputs.
#     # It calls requests.get() with those inputs,
#     # and returns the full URL of the data you want to get.
#     req = requests.Request(method = 'GET', url = baseurl, params = params)
#     prepped = req.prepare()
#     return prepped.url
#
# print(params)
# print(requestURL(some_base_url, some_params_dictionary))
