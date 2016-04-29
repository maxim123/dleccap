#!/usr/bin/python

"""
get-lec.py

Maxim Aleksa
maximal@umich.edu

Downloads lectures for a course.

Usage: ./dleccap.py
"""

# command-line arguments
import argparse
# HTTP stuff
# import cookielib
# import urllib
# import urllib2
import requests
# import json
import json
# file system access
import os
# I/O
import sys
# file downloads
import wget
# password input
from getpass import getpass
# parsing HTML
# pip install beautifulsoup4
from bs4 import BeautifulSoup

# globals
session = requests.Session()

"""
Prints message in red.
"""
def print_error(message):
    print '\033[31m{}\033[0m'.format(str(message))

"""
Prints message in yellow.
"""
def print_warning(message):
    print '\033[33m{}\033[0m'.format(str(message))

"""
Prints message in green.
"""
def print_success(message):
    print '\033[32m{}\033[0m'.format(str(message))


"""
Finds string between two substrings.

Thanks to http://stackoverflow.com/questions/3368969/find-string-between-two-substrings
"""
def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except:
        return None


"""
Authenticates user for specified service.
"""
def authenticate_for(service, username, password):
    # URL
    authentication_url = "https://weblogin.umich.edu/cosign-bin/cosign.cgi"

    # POST parameters
    data_to_post = {
        "service": service,
        "required": "",
        "login": username,
        "password": password
    }

    # get cookie
    p = session.get("https://weblogin.umich.edu")

    # authenticate
    p = session.post(authentication_url, data_to_post)


"""
Gets leccap cookie via CTools.
Returns site ID.
"""
def get_cookie_and_site_id_from_ctools(url):

    # check auth status
    if not session.cookies.get("cosign-weblogin"):
        print_warning("Authentication required.")
        authenticate("cosign-ctools")

    try:
        # get CTools leccap page
        p = session.get(url)

        # find url of page that gets cookie
        soup = BeautifulSoup(p.text, "html.parser")
        iframe = soup.find("iframe")
        iframeURL = "https://ctools.umich.edu" + iframe.get("src")

        # find form that gets cookie
        p = session.get(iframeURL)
        soup = BeautifulSoup(p.text, "html.parser")
        form = soup.find(id="ltiLaunchForm")
        inputs = form.find_all("input")
        data_to_post = {}
        for input_element in inputs:
            data_to_post[input_element.get("name")] = input_element.get("value")

        # get cookie
        auth_url = form.get("action")
        p = session.post(auth_url, data_to_post)

        # get site ID
        soup = BeautifulSoup(p.text, "html.parser")
        recording_url = soup.find("div", {"class": "recording"}).find("div", {"class": "play-link"}).find("a").get("href")
        return get_site_id_from_view_url("https://leccap.engin.umich.edu" + recording_url)

    except:
        return None


"""
Gets leccap cookie via Canvas.
Returns site ID.
"""
def get_cookie_and_site_id_from_canvas(url):

    # check auth status
    if not session.cookies.get("cosign-weblogin"):
        print_warning("Authentication required.")
        authenticate("cosign-shibboleth.umich.edu")

    try:
        # get Canvas leccap page
        p = session.get(url)
        # print p.text
        # find form on the page that will get the cookie
        soup = BeautifulSoup(p.text, "html.parser")
        form = soup.find("form")

        inputs = form.find_all("input")
        data_to_post = {}
        for input_element in inputs:
            data_to_post[input_element.get("name")] = input_element.get("value")

        print data_to_post

        # get cookie
        auth_url = form.get("action")
        p = session.post(auth_url, data_to_post)

        print p.text

        # get site ID
        soup = BeautifulSoup(p.text, "html.parser")
        recording_url = soup.find("div", {"class": "recording"}).find("div", {"class": "play-link"}).find("a").get("href")
        return get_site_id_from_view_url("https://leccap.engin.umich.edu" + recording_url)

    except:
        return None


"""
Gets username and password from user.
"""
def authenticate(service=None):
    # get auth data from user
    username = raw_input("Uniqname: ")
    password = getpass("Password: ")

    print "Authenticating...\n"

    if not service:
        services = ["cosign-ctools", "cosign-shibboleth.umich.edu", "cosign-leccap.engin"]
        for service in services:
            authenticate_for(service, username, password)
    else:
        authenticate_for(service, username, password)


"""
Gets information about a recording from its ID.
"""
def get_recording_from_id(recording_id):
    # URL
    recording_info_url = "https://leccap.engin.umich.edu/leccap/viewer/api/product/?rk=" + recording_id

    # check auth status
    if not session.cookies.get("cosign-weblogin"):
        print_warning("Authentication required.")
        authenticate()

    try:
        # get recording info
        r = session.get(recording_info_url)
        recording_info = json.loads(r.text)
        return recording_info
    except:
        print r.text
        return None


"""
Returns site ID of a recording viewable at specified URL.
"""
def get_site_id_from_view_url(url):
    # followed by recording ID
    str3 = "//leccap.engin.umich.edu/leccap/viewer/r/"

    recording = get_recording_from_id(url.split(str3, 1)[1])
    if not recording:
        return None
    else:
        return recording["sitekey"]


"""
Parses url and retrieves ID of the recordings site.
"""
def get_site_id(url):
    # followed by site ID
    str1 = "//leccap.engin.umich.edu/leccap/site/"
    str2 = "//leccap.engin.umich.edu/leccap/viewer/s/"
    # followed by recording ID
    str3 = "//leccap.engin.umich.edu/leccap/viewer/r/"
    # CTools page
    str4 = "//ctools.umich.edu/portal/site/"
    # Canvas page
    str5 = "//umich.instructure.com/courses/"

    # parse
    if str1 in url:
        return url.split(str1, 1)[1]
    elif str2 in url:
        return url.split(str2, 1)[1]
    elif str3 in url:
        # more complicated
        return get_site_id_from_view_url(url)
    elif str4 in url:
        return get_cookie_and_site_id_from_ctools(url)
    elif str5 in url:
        print_error(":( Cannot download recordings published to Canvas (yet)!")
        return
        # return get_cookie_and_site_id_from_canvas(url)
    else:
        return None


"""
Gets recordings for a site with the specified ID.
"""
def get_recordings_for_site(site_id):
    # URL
    site_contents_url = "https://leccap.engin.umich.edu/leccap/viewer/api/recordings/?sk=" + site_id

    # check auth status
    if not session.cookies.get("cosign-weblogin"):
        print_warning("Authentication required.")
        authenticate()

    try:
        # get recordings data
        r = session.get(site_contents_url)
        recordings = json.loads(r.text)
        return recordings
    except:
        return None


def download_recoding(recording, dest_folder=None):
    # construct url
    url = "https:%s%s/%s.%s" % (recording["mediaPrefix"],
                                recording["sitekey"],
                                recording["info"]["movie_exported_name"],
                                recording["info"]["movie_type"])

    if dest_folder is None:
        dest_folder = os.path.realpath(recording["sitename"])

    title = recording["title"].replace("/", "-")
    filename = "%s.%s" % (title, recording["info"]["movie_type"])
    destination = os.path.join(dest_folder, filename)

    # download!
    wget.download(url, out=destination)

def main():
    # parse command-line arguments
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    # ask for any URL
    ctools_sample_url = "https://ctools.umich.edu/portal/site/123/page/456"
    canvas_sample_url = "https://umich.instructure.com/courses/123/external_tools/1262"
    leccap_sample_url1 = "https://leccap.engin.umich.edu/leccap/site/123"
    leccap_sample_url2 = "https://leccap.engin.umich.edu/leccap/viewer/r/123"
    leccap_sample_url3 = "https://leccap.engin.umich.edu/leccap/viewer/s/123"
    print "Please enter a URL of any video in the recording series.\n"
    # print "If from Canvas, URL should look like\n%s\n" % (canvas_sample_url)
    print "If from CTools, URL should look like\n%s\n" % (ctools_sample_url)
    print "If neither from Canvas or from CTools, URL should look like\n%s or\n%s or\n%s\n" % (leccap_sample_url1, leccap_sample_url2, leccap_sample_url3)
    any_url = raw_input()
    print

    # parse side ID
    site_id = get_site_id(any_url)
    if not site_id:
        print_error(":( Could not parse URL.")
        print "This could happen becuase the URL is invalid, because username or password is invalid, or becuase you do not have access to the recordings."
        return

    # get recordings for site
    print "Getting recordings info...\n"
    recordings = get_recordings_for_site(site_id)
    if not recordings:
        print_error(":( Could not get recordings.")
        print "This could happen becuase username or password is invalid, or becuase you do not have access to the recordings."
        return
    elif len(recordings) == 0:
        print_error(":( No recordings available.")
        return

    print "%i recording%s available:" % (len(recordings), ("s" if (len(recordings) != 1) else ""))

    # print lecture info
    for index, recording in enumerate(recordings):
        print "%i\t(%s)\t%s" % (index + 1, recording["date"], recording["title"])
    print

    # which recordings to download?
    print "Which recording would you like to download?"
    input = raw_input("Enter a number between %i and %i, or press Enter to download all: " % (1, len(recordings)))
    try:
        input_as_int = int(input)
        if input_as_int < 1 or input_as_int > len(recordings):
            raise Exception("Invalid input")
        recordings = recordings[input_as_int - 1 : input_as_int]
    except:
        if input != "":
            # user did not press enter
            print_error(":( Invalid input")
            return

    # create folder for recordings
    course = recordings[0]["sitename"]
    directory = course
    if not os.path.exists(directory):
        os.makedirs(directory)

    # download files
    for index, recording in enumerate(recordings):
        print "(%i/%i) Downloading %s ..." % (index + 1, len(recordings), recording["title"])
        download_recoding(recording)
        print

    print_success("Finished!")


if __name__ == '__main__':
    main()
