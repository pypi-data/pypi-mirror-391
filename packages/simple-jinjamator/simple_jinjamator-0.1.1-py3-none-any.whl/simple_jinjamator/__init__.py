from .rest_client.api import API
from .rest_client.resource import Resource
from .rest_client.request import make_request
from .rest_client.models import Request
from types import MethodType
import base64
import os
import logging
import time
from time import sleep

class NotImplementedError(Exception):
    pass

class JinjamatorUndefinedRequiredVariableError(Exception):
    pass

class JinjamatorClientTimeoutError(Exception):
    pass

class JinjamatorResource(Resource):
    pass



class JinjamatorClient(object):
    def __init__(self, url, **kwargs):
        self._log = logging.getLogger()
        self._base_url = url

        if self._base_url[:-1] != "/":
            self._base_url + "/"

        self._username = kwargs.get("username", None)
        self._password = kwargs.get("password", None)

        self.api = API(
            api_root_url=url,  # base api url
            params={},  # default params
            headers={},  # default headers
            timeout=10,  # default timeout in seconds
            append_slash=False,  # append slash to final url
            json_encode_body=True,  # encode body as json
            ssl_verify=kwargs.get("ssl_verify", None),
            resource_class=JinjamatorResource,
            log_curl_commands=kwargs.get("log_curl_commands",False)
        )

    def __str__(self):
        return pformat(self.api.get_resource_list())

    def login(self, username, password, provider_name="local"):
        if username:
            self._username = username
        if password:
            self._password = password

        auth_data = self.api.aaa.login(provider_name).post(body={"username": self._username, "password": self._password})
        token = auth_data.get("access_token")
        self.api.headers["Authorization"] = token
        return True


    def wait_for_task(self, id, timeout=360):
        raise NotImplementedError()
        while timeout > 0:
            result = self.api("/dna/intent/api/v1/task")(id).get()
            timeout -= 1
            time.sleep(1)
            if "endTime" in result:
                self._log.debug(result)
                if "additionalStatusURL" in result:
                    return result["additionalStatusURL"]
                else:
                    result

    def get_job_logs(self, job_id):
        res=self.api.jobs(job_id).get()
        return res["log"]

    def get_job_status(self, job_id):
        res=self.api.jobs(job_id).get()
        return res["state"]

    def has_job_finished(self,job_id):
        if self.get_job_status(job_id) in ["SUCCESS","FAILURE"]:
            return True
        return False
            
    def wait_for_job(self,job_id, poll_interval=10, timeout=300):
        waited=0
        while not self.has_job_finished(job_id):
            if waited >= timeout:
                raise JinjamatorClientTimeoutError(f"Timeout waiting for job {job_id} to terminate")
            logging.debug(f"sleeping {poll_interval}s while waiting for job {job_id} to terminate ({waited}/{timeout} waited)")
            sleep(poll_interval)
            waited+=poll_interval
        return True
    
    def download_job_files(self,job_id,target_directory,overwrite=False, create_dir=True):
        res=self.api.jobs(job_id).get()
        for filename in res["files"]:
            self.download(f"{job_id}/{filename}",target_directory + os.path.sep + filename,overwrite=False, create_dir=True)

    def run(self, task, environment=None, task_params={}, **kwargs):
        params={
            "schema-type":"full"
        }

        if environment:
            params["preload-defaults-from-site"]=environment
        
        res=self.api(task).get(params=params)
        default_task_params={}
        missing_task_params=[]

        for k,cfg in res["schema"]["properties"].items():
            if cfg.get("required"):
                if cfg.get("default"):
                    default_task_params[k]=cfg.get("default")
                elif cfg.get("dependencies"):
                    logging.debug(f"dependencies not yet implemented -> ignoring dependent variable {k}")
                    continue
                elif cfg.get("enum"):
                    default_task_params[k]=cfg.get("enum")[0]
                else:
                    missing_task_params.append(k)
        for missing in missing_task_params:
            if missing not in task_params and missing not in kwargs:
                raise JinjamatorUndefinedRequiredVariableError(f"Unable to run task as {missing} is not defined")


        post_params = {k: v for k, v in default_task_params.items() if v != "__redacted__"}
        post_params.update(task_params)
        if kwargs:
            post_params.update(kwargs)
        post_result=self.api(task).post(body=post_params)
        return post_result["job_id"]
      

     


    def upload(self, path):
        with open(path, 'rb') as upload_file:
            res = self.api.files.upload.post(
                files = {'files': upload_file},
            )
            logging.debug(f"uploaded file data: {res}")
            return res["files"][0]["filesystem_path"]



    def download(self, url, path, overwrite=False, create_dir=True):
        dir_name = os.path.dirname(path)
        file_name = os.path.basename(path)
        if dir_name != file_name:
            if not os.path.isdir(dir_name) and not create_dir:
                self._log.error(
                    f"Destination directory {dir_name} not found and create_dir is False"
                )
                return False
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            if os.path.isfile(path) and not overwrite:
                self._log.error(
                    f"Destination file {path} exists and overwrite is False"
                )
                return False
            if os.path.isdir(path):
                self._log.error(
                    f"Destination path {path} exists and is a directory. We expect it beeing a path to the destination file"
                )
                return False

        with open(path, "wb") as fh:
            fh.write(self.api.files.download(url).get(headers={**self.api.headers}))
        return True
