import requests
import datetime
import json

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

