import os

from venmo_api import Client


def format_username(username: str) -> str:
    return username[1:] if username.startswith("@") else username


class VenmoService:

    # STRIP @ AND CONVERT USERNAME TO LOWERCASE
    def __init__(self):
        super().__init__()

        print("ACCESS TOKEN FOR VENMO")
        print(os.environ.get("VENMO_ACCESS_TOKEN"))

        self._CLIENT = Client(
            access_token=os.environ.get("VENMO_ACCESS_TOKEN"))

    # REQUEST PAYMENT TO USER WITH USER_ID
    def requestPayment(self, amount: int, job_title: str, target_venmo_id: str):
        print(amount, job_title, target_venmo_id)
        print("target id", target_venmo_id)
        note = f"PLEASE IS REQUESTING PAYMENT FOR: {job_title}."
        target = self._CLIENT.user.get_user(user_id=format_username(target_venmo_id))
        print("target", target)
        try:
            self._CLIENT.payment.request_money(amount=amount, target_user=target, note=note)
            # return {"message": "PAYMENT REQUEST SUCCESSFUL", "is_valid": True}
            return True
        except Exception as e:
            print(e)
            # return {"message": "PAYMENT REQUEST FAILED", "is_valid": False}
            return False

    # REQUEST PAYMENT TO USER WITH USER_ID
    def sendPayment(self, amount: int, job_title: str, target_venmo_id: str):
        note = f"PLEASE SENT YOU PAYMENT FOR: {job_title}. THANK YOU."
        print("target id", target_venmo_id)
        target = self._CLIENT.user.get_user(user_id=format_username(target_venmo_id))
        print("target", target)
        try:
            self._CLIENT.payment.send_money(amount=amount, target_user=target, note=note)
            # return {"message": "PAYMENT SENT SUCCESSFUL", "is_valid": True}
            return True
        except Exception as e:
            print(e)
            # return {"message": "PAYMENT SENT FAILED", "is_valid": False}
            return False
