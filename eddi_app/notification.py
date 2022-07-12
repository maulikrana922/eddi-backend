import requests
import datetime
import json
# from pyfcm import FCMNotification
# push_service = FCMNotification(api_key="AAAAM5_RpBI:APA91bHFuextvmhZyyu0dAirqqpPFqnmN14HbRhoiTNqhcadSboOMrjUPzLedK_yX45Q7lydrgVHn1q5LvnwoZUZZRNJ8PPgfpcrlT5DvXUi7i02GJj4G3jncZQLgXuGL_1sds1t16NP")



def send_notification(sender, receiver, message, sender_type=None, receiver_type=None):
    print('nxvdbsnp noti send',sender, receiver, message)
    try:
        url = "https://testyourapp.online:5001"
        # url = "http://localhost:4000/"
        payload = json.dumps({
        "type": "type1",
        "json": {
            'sender': sender,
            'receiver': [i for i in receiver],
            'initials': "initials",
            # "sender_type": sender_type,
            # "receiver_type" : receiver_type,
            "message": message,
            "created_date_time" : str(datetime.datetime.now())
        }
        })
        headers = {
        'Content-Type': 'application/json'
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response, "responseeesees")
        except Exception as ex:
            print(ex,"exexe")
    except Exception as ex:
        print(ex,"ececece")

def send_push_notification(receivers,message):
    try:
        for receiver in receivers:
            payload = {
                "to":receiver,
                "notification": {
                "title": "You Got New Notification",
                "body": message
                }
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": "key=AAAAM5_RpBI:APA91bHFuextvmhZyyu0dAirqqpPFqnmN14HbRhoiTNqhcadSboOMrjUPzLedK_yX45Q7lydrgVHn1q5LvnwoZUZZRNJ8PPgfpcrlT5DvXUi7i02GJj4G3jncZQLgXuGL_1sds1t16NP"
            }
            try:
                response = requests.post('https://fcm.googleapis.com/fcm/send',json=payload,headers=headers,)
                print(response, "responseeesees")
            except Exception as ex:
                print(ex,"exexe")
    except Exception as ex:
        print(ex,"exec")