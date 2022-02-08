#!/usr/bin/env python3

### VARIABLES
# uncomment/comment which one you use
PROJECT = "paper"
#PROJECT = "waterfall"

VERSION = "1.18.1"
#VERSION = "1.17"

FILENAME = "paper.jar" # DO NOT OVERWRITE 'paper.jar' DIRECTLY
#FILENAME = "waterfall_update.jar" # DO NOT OVERWRITE 'waterfall.jar' DIRECTLY

### DO NOT CHANGE BELOW ###

from urllib import request
from urllib.error import HTTPError, URLError, ContentTooShortError 
import json
import logging
from socket import timeout
import shutil
from hashlib import sha256

def json_to_dict(response):
    return json.loads(response.read().decode('utf-8'))

def get_versions(project):
    url = f"https://papermc.io/api/v2/projects/{project}"
    try:
        logging.info("Fetching versions list...")
        with request.urlopen(url, timeout=30) as response:
            data = json_to_dict(response)
            versions = data['versions']
            return versions
    except (HTTPError, URLError) as e:
        logging.exception(e)
        logging.error("Could not fetch versions list! Check your connection!")
        return None

def get_latest_build(project, version):
    url = f"https://papermc.io/api/v2/projects/{project}/versions/{version}"
    logging.info(f"Selected version: {project.capitalize()} {version}")
    build = None
    try:
        logging.info("Fetching latest build number...")
        with request.urlopen(url, timeout=10) as response:
            data = json_to_dict(response)
            build = data['builds'][-1]
    except timeout:
        logging.error(f"Connection timed out! Check your internet connection and URL! ({url})")
    except HTTPError as e:
        logging.exception(e)
        if (e.code == 500):
            logging.error("Connection timed out! Update server might be down?")
            logging.error(f"URL: {url}")
        if (e.code == 404):
            logging.error("Invalid version number!")
            versions = get_versions(project)
            if versions is not None:
                versions.reverse()
                logging.info(f"Available versions: {versions}")
            logging.info("Please change the selected version in this file's VERSION variable and run the script again!")
    finally:
        return build
        
def get_jar(project, version, build, filename=FILENAME):
    logging.info(f"Latest build: {project}-{version}-{build}")
    url = f"https://papermc.io/api/v2/projects/{project}/versions/{version}/builds/{build}/downloads/{project}-{version}-{build}.jar"
    try:
        with open(filename, 'wb') as out_file:
            logging.info(f"Fetching latest {project}.jar...")
            with request.urlopen(url, timeout=10) as response:
                shutil.copyfileobj(response, out_file)
        logging.info(f"SUCCESS! Latest build saved as {filename}")
        return True
    except PermissionError as e:
        logging.exception(e)
        logging.error("Insufficient write permissions! Could not write file to system!")
        return False
    except timeout:
        logging.error(f"Connection timed out! Check your internet connection and URL! ({url})")
        return False
    except ContentTooShortError as e:
        logging.exception(e)
        logging.error("Download was interrupted!")
        return False
    except (HTTPError, URLError) as e:
        logging.exception(e)
        logging.error("Could not download latest build! Try downloading from the following URL manually:")
        logging.error(f"URL: {url}")
        return False
    
def calculate_sha256(filename):
    with open(filename, "rb") as f:
        sha256_hash = sha256()
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_sha256(project, version, build):
    logging.info(f"Fetching hash for {project}-{version}-{build}.jar")
    url = f"https://papermc.io/api/v2/projects/{project}/versions/{version}/builds/{build}"
    verify_hash = None
    try:
        with request.urlopen(url, timeout=10) as response:
            data = json_to_dict(response)
            verify_hash = data['downloads']['application']['sha256']
    except timeout:
        logging.warning(f"Connection timed out! Could not get SHA256 hash from server!")
    except (HTTPError, URLError, ContentTooShortError) as e:
        logging.exception(e)
        logging.warning("Could not get SHA256 hash from server!")
    finally:
        return verify_hash
        
def verify_sha256(project, version, build, filename=FILENAME):
        logging.info("Calculating hash...")
        check_hash = calculate_sha256(filename)
        logging.info(f"SHA256: {check_hash}")
        verify_hash = get_sha256(project, version, build)
        logging.debug(f"Verification hash: {verify_hash}")
        if verify_hash is None:
            logging.warning("SHA256 verification failed!")
            return False
        elif check_hash == verify_hash:
            logging.info("SHA256 verification success!")
            return True
        else:
            logging.warning(f"SHA256 verification failed! Expected {verify_hash}")
            return False
 
def main():
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    build = get_latest_build(PROJECT, VERSION)
    if build is not None:
        if get_jar(PROJECT, VERSION, build):
            verify_sha256(PROJECT, VERSION, build)

if __name__ == "__main__":
    main()
