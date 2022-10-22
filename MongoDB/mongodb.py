import os

from pymongo import MongoClient
from Utils import utils


class MongoDBService:

    def __init__(self):
        super().__init__()

        MONGODB_URI = os.environ.get("MONGODB_URI")
        print("MONGO DB URI = ", MONGODB_URI)

        self._CLIENT = MongoClient(MONGODB_URI)
        self._DB = self._CLIENT["PLEASE"]

        self._USERS = self._DB["USERS"]
        self._JOBS = self._DB["JOBS"]


class UserService(MongoDBService):

    def __init__(self):
        super().__init__()

    def user_exists(self, email: str):
        existing_user = self._USERS.find_one({"email": email})
        if existing_user:
            return {"error": "USER WITH EMAIL ALREADY EXISTS", "user_exists": True,
                    "existing_user_id": existing_user.get("user_id")}
        return {"error": None, "user_exists": False, "existing_user_id": None}

    def register_user(self, name: str, email: str, venmo_id: str):
        user_id = utils.generate_user_id()
        auth_id = utils.generate_auth_id()

        document = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "venmo_id": venmo_id,
            "auth_id": auth_id,
            "jobs_posted": [],
            "jobs_helped": [],
            "total_reward": 0,
        }

        inserted_user = self._USERS.insert_one(document=document)

        print("USER CREATED WITH FOLLOWING INFO: ", inserted_user)

        return self.find_user_by_id(user_id)

    def find_user_by_id(self, user_id: str):
        print("FINDING USER WITH ID ", user_id)
        user = self._USERS.find_one({"user_id": user_id})
        return {
            "user_id": user.get("user_id"),
            "name": user.get("name"),
            "email": user.get("email"),
            "venmo_id": user.get("venmo_id"),
            "auth_id": user.get("auth_id"),
            "jobs_posted": user.get("jobs_posted"),
            "jobs_helped": user.get("jobs_helped"),
            "total_reward": user.get("total_reward")
        }

    def job_posted(self, user_id: str, job_id: str):
        self._USERS.update_one({"user_id": user_id}, {
            "$push": {"jobs_posted": job_id}
        })
        return {"job_posted": True}

    def job_helped(self, user_id: str, reward: int, job_id: str):
        self._USERS.update_one({"user_id": user_id}, {
            "$inc": {"total_reward": reward},
            "$push": {"jobs_helped": job_id}
        })
        return {"job_complete": True}


class JobService(MongoDBService):

    def __init__(self):
        super().__init__()

    def create_job(self, title: str, description: str, reward: int, helpee_id: str):

        existing_job = self._JOBS.find_one({"title": title})

        if existing_job:
            return {"error": "JOB WITH SAME TITLE ALREADY EXISTS", "job_created": False, "created_job": None}

        userService = UserService()

        job_id = utils.generate_job_id()

        document = {
            "job_id": job_id,
            "title": title,
            "description": description,
            "reward": reward,
            "helpee_id": helpee_id,
            "helper_id": 0,
            "status": 0
        }

        inserted_job = self._JOBS.insert_one(document=document)

        userService.job_posted(helpee_id, job_id)

        print("USER CREATED WITH FOLLOWING INFO: ", inserted_job)

        return {"error": None, "job_created": True, "created_job": self.find_job_by_id(job_id)}

    def find_job_by_id(self, job_id: str):
        print("FINDING JOB WITH ID ", job_id)
        job = self._JOBS.find_one({"job_id": job_id})
        return {
            "job_id": job.get("job_id"),
            "title": job.get("title"),
            "description": job.get("description"),
            "reward": job.get("reward"),
            "helpee_id": job.get("helpee_id"),
            "helper_id": job.get("helper_id"),
            "status": job.get("status")
        }

    def select_job(self, job_id: str, helper_id: str):
        result = self._JOBS.find_one_and_update({"job_id": job_id}, {
            "$set": {"helper_id": helper_id, "status": 1}
        })
        return {'job_selected': True, "selected_job": self.find_job_by_id(job_id)}

    def approve_job(self, job_id: str, helper_auth_id: str):
        job = self.find_job_by_id(job_id)
        helper_id = job.get("helper_id")

        if not helper_id:
            return {"job_approved": False, "error": "THE JOB HASN'T BEEN SELECTED YET", "approved_job": None}

        userService = UserService()

        helper = userService.find_user_by_id(helper_id)

        if helper.get("auth_id") == helper_auth_id:
            print("AUTH ID APPROVED")
            self._JOBS.update_one({"job_id": job_id}, {
                "$set": {"status": 2}
            })

            print("TODO --- SEND VENMO PAYMENT TO", helper.get("venmo_id"))

            userService.job_helped(helper.get("user_id"), job.get("reward"), job_id)
        else:
            return {"job_approved": False, "error": "AUTH CODE DOES NOT MATCH", "approved_job": None}

        return {"job_approved": True, "error": None, "approved_job": self.find_job_by_id(job_id)}
