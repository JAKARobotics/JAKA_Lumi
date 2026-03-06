import lumi_url
import requests
import json
import time


def test():
    # get system infomation
    response = requests.get(lumi_url.LUMI_SYSINFO_URL)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return
    parsed_text_json = json.loads(response.text)
    print(f"JAKA Lumi info: {parsed_text_json}")

    # reset all joint
    response = requests.post(lumi_url.LUMI_RESET_URL, json={})
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return
    print("reset ok")

    # enable all joint
    response = requests.post(lumi_url.LUMI_ENABLE_URL, json={"enable": 1})
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return
    print("enable ok")

    # read position
    response = requests.get(lumi_url.LUMI_GETSTATE_URL)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return
    parsed_text_json = json.loads(response.text)  # Parse the text as JSON
    print(
        f"JAKA Lumi state: {parsed_text_json[0]['pos']},{parsed_text_json[1]['pos']},{parsed_text_json[2]['pos']}"
    )
    parsed_text_json[0]["pos"]

    # home
    response = requests.post(
        lumi_url.LUMI_MOVETO_URL,
        json={"pos": [0.0, 0, 0, 0], "vel": 100, "acc": 100},
    )
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return

    # move to position A blockly
    for i in range(100):
        response = requests.post(
            lumi_url.LUMI_MOVETO_URL,
            json={"pos": [0.0, -100.0, -90.0, -5.0], "vel": 100, "acc": 100},
        )
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return
        print("move to A ok")

        # move to position B blockly
        response = requests.post(
            lumi_url.LUMI_MOVETO_URL,
            json={"pos": [200.0, 100.0, 90.0, 30.0], "vel": 100, "acc": 100},
        )
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return
        print("move to B ok")

    # disable all joint
    time.sleep(2)
    response = requests.post(lumi_url.LUMI_ENABLE_URL, json={"enable": 0})
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return
    print("disable ok")


if __name__ == "__main__":
    test()
