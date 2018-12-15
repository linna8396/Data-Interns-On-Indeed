from indeed_scraping import *
import plotly.plotly as py
import plotly.graph_objs as go


def draw_bar_chart():
    # try to get the skills dictionary from the cache
    # if it is not stored in the cache, run the job scraping and cache the result
    cache = Cache("skillset_dict.json")
    skillset_dict = cache.get("skillset_dict")
    if not skillset_dict:
        load_skills()
        indeed_scrape_and_store()
        cache.set("skillset_dict", skillset, 15)
        skillset_dict = skillset

    # sort the skills based on their number of occurences
    skills_sorted = sorted(skillset_dict, key = lambda skill: skillset_dict[skill], reverse = True)

    skills = []
    occurences = []

    for skill in skills_sorted:
        if skillset_dict[skill] != 0: # exclude the skills with 0 occurence
            skills.append(skill)
            occurences.append(skillset_dict[skill])

    data = [go.Bar(x = skills, y = occurences, text = skills)]
    py.plot(data, filename='Skills Importantce Levels')



def draw_job_map():
    try:
        conn = psycopg2.connect("dbname='job_postings' user=") # No password on the databases yet -- wouldn't want to save that in plain text, anyway
        # Remember: need to, at command prompt or in postgres GUI: createdb test507_music (or whatever db name is in line ^)
        print("Success connecting to database")
    except:
        print("Unable to connect to the database. Check server and credentials.")
        exit() # stop running the program if there is no database connection

    cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # fetch the job title and the geolocation information of that job
    cur.execute("SELECT job_title, latitude, longitude FROM data_jobs")
    lat_vals = []
    lng_vals = []
    text_vals = []
    for job_posting in cur.fetchall():
        job = list(job_posting)
        if job[1] != None: # exclude the job without geolocation information
            text_vals.append(job[0])
            lat_vals.append(job[1])
            lng_vals.append(job[2])

    jobs = [dict(type = "scattergeo",
                 locationmode = 'USA-states',
                 lon = lng_vals,
                 lat = lat_vals,
                 text = text_vals,
                 mode = "markers",
                 marker = dict(size = 13, symbol = "star", color = "rgb(52, 52, 51)"))]

    title = "Job Postings For Data Interns"
    layout = dict(title = title,
                  geo = dict(scope = "usa",
                             projection = dict(type = "albers usa"),
                             lataxis = [min(lat_vals), max(lat_vals)],
                             lonaxis = [min(lng_vals), max(lng_vals)],
                             showland = True,
                             landcolor = "rgb(237, 227, 202)",
                             subunitcolor = "rgb(176, 173, 156)",
                             countrycolor = "rgb(217, 100, 217)",
                             showlakes = True,
                             lakecolor = "rgb(174, 218, 246)",
                             countrywidth = 3,
                             subunitwidth = 3
                            ),
                )
    fig = dict(data = jobs, layout = layout)

    py.plot(fig, validate = False, filename = title)


draw_bar_chart()
draw_job_map()
