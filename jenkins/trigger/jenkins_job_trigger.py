#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, GoodData

import requests
import time
import sys
import os

from urllib.parse import urljoin, urlparse


DOCUMENTATION = r'''
---
module: jenkins_job_trigger
short_description: A custom module to trigger job in Jenkins
version_added: "1.0.0"
description: A custom module to trigger job in Jenkins.
options:
    jenkins_server:
        description: Jenkins Server URL
        type: str
    job_folder:
        description: Folder of the job to build
        type: str
    job_name:
        description: Name of job to build
        required: true
        type: str
    job_parameters:
        description: Job build parameters in dict syntax
        type: dict
    use_crumb:
        description: Use crumb
        default: true
        type: bool
    wait_for_finish:
        description: Wait for the build to be finished. Exit 0 when build is successfully triggered and run.
        default: true
        type: bool
    client_cert_pem:
        description: Path to client certificate in pem format for authentication with Jenkins Server
        type: str
'''


class JenkinsJobTrigger(object):
    def __init__(self, jenkins_server, job_name, job_parameters, client_cert_pem=None,
                 job_folder=None, use_crumb=True, wait_for_finish=True):
        self.jenkins_server = jenkins_server
        self.job_folder = job_folder
        self.job_name = job_name
        self.job_parameters = job_parameters
        self.use_crumb = use_crumb
        self.wait_for_finish = wait_for_finish
        self.ss = requests.Session()
        if client_cert_pem:
            self.ss.cert = client_cert_pem
        if self.use_crumb:
            self.ss.headers.update(self.get_crumb())

    def get_crumb(self):
        get_crumb_url = urljoin(self.jenkins_server, 'crumbIssuer/api/json')
        get_crumb_req = self.ss.get(get_crumb_url)
        jenkins_crumb = dict()

        try:
            jenkins_crumb[get_crumb_req.json()['crumbRequestField']] = get_crumb_req.json()['crumb']
        except Exception as e:
            if get_crumb_req.status_code == 401:
                raise Exception('Unauthorized [401]: check for your cert login')
            else:
                raise Exception(e)

        return jenkins_crumb

    def jenkins_build_job(self):
        if self.job_folder is not None:
            job_suburl = '/%s' % self.job_folder
        else:
            job_suburl = ''
        build_job_url = urljoin(self.jenkins_server, 'job%s/job/%s/buildWithParameters' % (job_suburl, self.job_name))
        job_build_req = self.ss.post(build_job_url, params=self.job_parameters)

        queue_item_path = urlparse(job_build_req.headers['Location']).path
        build_started_path = urlparse(self.search_queue_item(queue_item_path)).path

        return self.check_build_status(build_started_path)

    def search_queue_item(self, queue_item_path):
        queue_item_url = urljoin(self.jenkins_server, '%s/api/json' % queue_item_path)
        search_queue_req = self.ss.get(queue_item_url)

        while search_queue_req.json()['why'] is not None:
            time.sleep(4)
            search_queue_req = self.ss.get(queue_item_url)

        return search_queue_req.json()['executable']['url']

    def check_build_status(self, build_started_path):
        build_started_url = urljoin(self.jenkins_server, '%s/api/json' % build_started_path)
        build_status_req = self.ss.get(build_started_url)
        if self.wait_for_finish:
            while build_status_req.json()['building']:
                time.sleep(4)
                build_status_req = self.ss.get(build_started_url)

        build_result = {
            'job_build_status': build_status_req.json()['result'],
            'job_build_url': build_status_req.json()['url']
        }

        return build_result


def main(cert_path, server, folder, job_name, params):
    params = eval(params)

    # This is a temporary workaround as we plan to deprecate
    # Jenkins which needs some of the ZUUL_* variables
    zuul_params = {}
    for k, v in params.items():
        if k.startswith("GH_"):
            zuul_params[k.replace("GH_", "ZUUL_")] = v
    params.update(zuul_params)

    trigger = JenkinsJobTrigger(
        jenkins_server=server,
        job_folder=folder,
        job_name=job_name,
        job_parameters=params,
        client_cert_pem=cert_path
    )

    trigger_result = trigger.jenkins_build_job()
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            print(f'build_status={trigger_result["job_build_status"]}', file=f)
            print(f'url={trigger_result["job_build_url"]}', file=f)
    else:
        print(f'::set-output name=build_status::{trigger_result["job_build_status"]}')
        print(f'::set-output name=url::{trigger_result["job_build_url"]}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
