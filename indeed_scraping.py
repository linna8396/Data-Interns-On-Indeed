from bs4 import BeautifulSoup
from caching import Cache
import requests

indeed_baseurl = "https://www.indeed.com/jobs?"

# Use the passed base url, parameters dictionary, and private keys list to generate
# and return a String that can be used as the unique key for the JSON format caching file
def cache_key_generator(baseurl, params_dict, private_keys=["key"]):
    alphabetized_keys = sorted(params_dict.keys())
    params_pairs = []
    for key in alphabetized_keys:
        if key not in private_keys:
            res.append("{}-{}".format(key, params_dict[key]))
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
    if not job_postings_web:
        job_postings_html = requests.get(indeed_baseurl, params = params_dict).text
        cache.set(url, result, 15)

    # return the job postings data formatted as a BeautifulSoup object
    return BeautifulSoup(job_postings_html, 'html.parser')


def indeed_scraping():
    jobs_batch_num = 0
    #while True: # 这个条件记得改
        # scrape这一页
        raw_data = get_job_postings(num_jobs)
        # process data

        #jobs_batch_num += 10 # update the number for a new batch of job postings

indeed_scraping()
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
