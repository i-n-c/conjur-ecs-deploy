#!/usr/bin/python3

# Based on: https://stackoverflow.com/a/48531874/719362

import os
import requests
import re
import sys
import json
import time

# secs for polling Jenkins API
#
QUEUE_POLL_INTERVAL = 1
JOB_POLL_INTERVAL = 15
OVERALL_TIMEOUT = 36006

# job specifics: should be passed in
auth_token = os.environ['JENKINS_AUTH_TOKEN']
jenkins_uri = os.environ['JENKINS_URL']
job_name = os.environ['JENKINS_JOB_NAME']
conjur_image = os.environ['JENKINS_CONJUR_IMAGE']

# start the build
#
start_build_url = \
    f"https://{auth_token}@{jenkins_uri}/job/{job_name}/buildWithParameters"
r = requests.post(start_build_url, data={"CONJUR_IMAGE": conjur_image})

if r.status_code != 201:
    print(f"Error occurred, status code: {r.status_code}")
    print("Headers:")
    print(json.dumps(dict(r.headers), indent=4))
    print("Response:")
    print(r.text)

# from return headers get job queue location
#
m = re.match(r"http.+(queue.+)\/", r.headers['Location'])
if not m:
    # To Do: handle error
    print("Jenkins did not respond with the "
          "queue location when a build was requested")
    sys.exit(1)

# poll the queue looking for job to start
#
queue_id = m.group(1)
job_info_url = f'http://{auth_token}@{jenkins_uri}/{queue_id}/api/json'
elapsed_time = 0
print(f'{time.ctime()} Job {job_name} added to queue: {job_info_url}')
while True:
    queue_info_response = requests.get(job_info_url)
    queue_info = queue_info_response.json()
    task = queue_info['task']['name']
    try:
        job_id = queue_info['executable']['number']
        break
    except Exception:
        print(f"no job ID yet for build: {task}")
        time.sleep(QUEUE_POLL_INTERVAL)
        elapsed_time += QUEUE_POLL_INTERVAL

    if (elapsed_time % (QUEUE_POLL_INTERVAL * 10)) == 0:
        print(f"{time.ctime()}: Job {job_name} "
              "not started yet from {queue_id}")

# poll job status waiting for a result
#
job_url = (f'http://{auth_token}@{jenkins_uri}'
           f'/job/{job_name}/{job_id}/api/json')
start_epoch = int(time.time())
while True:
    print("{}: Job started URL: {}".format(time.ctime(), job_url))
    job = requests.get(job_url).json()
    result = job['result']
    # Some jobs set a result before they complete. The result might change,
    # so wait till the build is complete before reading the result.
    if job['building']:
        print(f"{time.ctime()}: Job: {job_name}#{job_id} still building. "
              f"Polling again in {JOB_POLL_INTERVAL} secs")
    else:
        if result == 'SUCCESS':
            # Do success steps
            print(f"{time.ctime()}: Job: {job_name}#{job_id} Status: {result}")
            break
        elif result == 'FAILURE':
            # Do failure steps
            print(f"{time.ctime()}: Job: {job_name}#{job_id} Status: {result}")
            sys.exit(1)
        elif result == 'ABORTED':
            # Do aborted steps
            print(f"{time.ctime()}: Job: {job_name}#{job_id} Status: {result}")
            sys.exit(1)

    cur_epoch = int(time.time())
    if (cur_epoch - start_epoch) > OVERALL_TIMEOUT:
        print(f"{time.ctime()}: Build didn't complete before timeout"
              f" of {OVERALL_TIMEOUT} secs")
        sys.exit(1)

    time.sleep(JOB_POLL_INTERVAL)
