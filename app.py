import atexit
import os

from flask import Flask, request
from MongoDB import mongodb

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get("MONGODB_URI")

user_service = mongodb.UserService()
job_service = mongodb.JobService()


# RETURN USER ERROR, USER_EXISTS, EXISTING_USER
@app.route('/users/user_exists/', methods=["POST"])
def user_exists():
    data = request.form
    email = data.get("email")
    return user_service.user_exists(email)


# RETURN INSERTED USER
@app.route('/users/register_user/', methods=["POST"])
def register_user():
    data = request.form
    print(data)

    name = data.get("name")
    email = data.get("email")
    venmo_id = data.get("venmo_id")

    return user_service.register_user(name, email, venmo_id)


# RETURN FOUND USER
@app.route("/users/find_user/", methods=["GET"])
def find_user():
    user_id = request.args.get('user_id')
    return user_service.find_user_by_id(user_id)


# RETURN INSERTED JOB
@app.route('/jobs/create_job/', methods=["POST"])
def create_job():
    data = request.form

    title = data.get("title")
    description = data.get("description")
    reward = int(data.get("reward"))
    helpee_id = data.get("helpee_id")

    return job_service.create_job(title, description, reward, helpee_id)


# RETURN FOUND JOB
@app.route("/jobs/find_job/", methods=["GET"])
def find_job():
    job_id = request.args.get('job_id')
    return job_service.find_job_by_id(job_id)


@app.route("/jobs/select_job/", methods=["POST"])
def select_job():
    data = request.form

    job_id = data.get("job_id")
    helper_id = data.get("helper_id")

    return job_service.select_job(job_id, helper_id)


@app.route("/jobs/approve_job/", methods=["POST"])
def approve_job():
    data = request.form

    job_id = data.get("job_id")
    helper_auth_id = data.get("helper_auth_id")

    return job_service.approve_job(job_id, helper_auth_id)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


def shutdown_clients():
    user_service._CLIENT.close()
    job_service._CLIENT.close()


if __name__ == '__main__':
    atexit.register(shutdown_clients)
    app.run(debug=True)
