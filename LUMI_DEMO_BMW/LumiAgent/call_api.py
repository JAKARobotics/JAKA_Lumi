import argparse
import sys

import requests


def main():
    parser = argparse.ArgumentParser(
        description="Send a number string to the local grasp API."
    )
    parser.add_argument(
        "number",
        help="Number string to send (expected: 1, 2, or 3).",
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:12123/grasp",
        help="API endpoint URL.",
    )
    parser.add_argument(
        "--method",
        choices=["get", "post"],
        default="get",
        help="HTTP method to use.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Send the number in a JSON body (server-side code currently checks for an int).",
    )
    args = parser.parse_args()

    try:
        if args.json:
            value = int(args.number) if args.number.isdigit() else args.number
            response = requests.request(
                args.method,
                args.url,
                json={"number": value},
                timeout=5,
            )
        else:
            params_or_data = {"number": args.number}
            if args.method == "get":
                response = requests.get(args.url, params=params_or_data, timeout=5)
            else:
                response = requests.post(args.url, data=params_or_data, timeout=5)
    except requests.RequestException as exc:
        print(f"Request failed: {exc}")
        sys.exit(1)

    print(f"Status: {response.status_code}")
    print(f"Body: {response.text}")


if __name__ == "__main__":
    main()
