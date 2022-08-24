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
        except:
            pass
    except:
        pass

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
                "Authorization": "key=AAAAhLIgOxM:APA91bGsAx3RYNFswx3AXcfTz3uDc0LInLp7BQpgcR2vITp53DNspmrX3b5fafFQtxsRktpe7cz9f6x_Nz26Ekwx46s5n7BEy8wLbeazbdPZzKnj8ltEqg3lAduU3mQ0hlLXalc4MdBD"
            }
            try:
                response = requests.post('https://fcm.googleapis.com/fcm/send',json=payload,headers=headers,)
                print(response, "responseeesees")
            except Exception as ex:
                print(ex,"exexe")
    except Exception as ex:
        print(ex,"exec")