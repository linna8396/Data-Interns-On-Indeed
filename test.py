from indeed_scraping import *
from visualization import *
import unittest

class TestDataScrapingAndStoring(unittest.TestCase):
    def test_job_exist(self):
        try:
            conn = psycopg2.connect("dbname='job_postings' user=") # No password on the databases yet -- wouldn't want to save that in plain text, anyway
            # Remember: need to, at command prompt or in postgres GUI: createdb test507_music (or whatever db name is in line ^)
            print("Success connecting to database")
        except:
            print("Unable to connect to the database. Check server and credentials.")
            exit() # stop running the program if there is no database connection

        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

        cur.execute("SELECT job_title, company_name, city, state FROM data_jobs WHERE job_title = 'Data Science Internship - Zoro'")
        job = cur.fetchone()
        name = len(job) > 0
        company = job[1] == "Grainger"
        city = job[2] == "Buffalo Grove"
        state = job[3] == "IL"
        self.assertTrue(name and company and city and state)


    def test_whether_contains_wrong_posting(self):
        try:
            conn = psycopg2.connect("dbname='job_postings' user=") # No password on the databases yet -- wouldn't want to save that in plain text, anyway
            # Remember: need to, at command prompt or in postgres GUI: createdb test507_music (or whatever db name is in line ^)
            print("Success connecting to database")
        except:
            print("Unable to connect to the database. Check server and credentials.")
            exit() # stop running the program if there is no database connection

        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

        cur.execute("SELECT job_title, company_name, city, state FROM data_jobs WHERE job_title = 'Software Engineer Intern (Summer 2019)'")
        job = cur.fetchone()
        self.assertTrue(job == None)


    def test_geo_data(self):
        try:
            conn = psycopg2.connect("dbname='job_postings' user=") # No password on the databases yet -- wouldn't want to save that in plain text, anyway
            # Remember: need to, at command prompt or in postgres GUI: createdb test507_music (or whatever db name is in line ^)
            print("Success connecting to database")
        except:
            print("Unable to connect to the database. Check server and credentials.")
            exit() # stop running the program if there is no database connection

        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

        cur.execute("SELECT job_title, city, latitude, longitude FROM data_jobs WHERE job_title = 'Data Science Internship - Zoro'")
        job = cur.fetchone()
        self.assertTrue(get_geo_data(job[1])[0] - job[2] < 0.01)
        self.assertTrue(get_geo_data(job[1])[1] - job[3] < 0.01)


    def test_repetitive_data(self):
        self.assertTrue(len(job_names) == len(set(job_names)))


    def test_whether_contains_wrong_skills(self):
        try:
            conn = psycopg2.connect("dbname='job_postings' user=") # No password on the databases yet -- wouldn't want to save that in plain text, anyway
            # Remember: need to, at command prompt or in postgres GUI: createdb test507_music (or whatever db name is in line ^)
            print("Success connecting to database")
        except:
            print("Unable to connect to the database. Check server and credentials.")
            exit() # stop running the program if there is no database connection

        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

        cur.execute("SELECT job_title, skills FROM data_jobs WHERE job_title = 'Data Science Intern' AND company_name = 'Adobe'")

        job = cur.fetchone()
        skills = job[1][1:-1].split(",")
        self.assertTrue("r" not in skills)


    def test_skills(self):
        try:
            conn = psycopg2.connect("dbname='job_postings' user=") # No password on the databases yet -- wouldn't want to save that in plain text, anyway
            # Remember: need to, at command prompt or in postgres GUI: createdb test507_music (or whatever db name is in line ^)
            print("Success connecting to database")
        except:
            print("Unable to connect to the database. Check server and credentials.")
            exit() # stop running the program if there is no database connection

        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

        cur.execute("SELECT job_title, skills FROM data_jobs WHERE job_title = 'Intern - Data Analytics - Business Systems'")
        skills = cur.fetchone()[1]
        self.assertTrue("tableau" in skills)


    def test_blank_skills(self):
        try:
            conn = psycopg2.connect("dbname='job_postings' user=") # No password on the databases yet -- wouldn't want to save that in plain text, anyway
            # Remember: need to, at command prompt or in postgres GUI: createdb test507_music (or whatever db name is in line ^)
            print("Success connecting to database")
        except:
            print("Unable to connect to the database. Check server and credentials.")
            exit() # stop running the program if there is no database connection

        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

        cur.execute("SELECT job_title FROM data_jobs WHERE skills = ''")
        job = cur.fetchall()
        self.assertTrue(len(job) == 0)


    def test_handling_wrong_geodata(self):
        self.assertEqual((None, None), get_geo_data("rtyuio"))


class TestVisualizing(unittest.TestCase):

    # we can't test to see if the visualizations are correct, but we can test that
    # the functions don't return an error.
    def test_show_job_map(self):
        try:
            draw_bar_chart()
        except:
            self.fail()

    def test_show_nearby_map(self):
        try:
            draw_job_map()
        except:
            self.fail()


if __name__ == '__main__':
    unittest.main()
