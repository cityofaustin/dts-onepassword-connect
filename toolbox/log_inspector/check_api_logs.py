import os
import json
from datetime import datetime

import requests
import dateutil.parser
from dotenv import load_dotenv

load_dotenv()

OP_API_TOKEN = os.getenv("OP_API_TOKEN")
OP_CONNECT = os.getenv("OP_CONNECT")

ip_set = set()


def main():
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OP_API_TOKEN}",
    }

    fetch_data_from_connect_server(
        base_url=OP_CONNECT, limit=50, start_offset=0, end_offset=1000, headers=headers
    )

    print("\nVisitor IP Set:")
    print(ip_set)


def add_ip(ip):
    global ip_set
    if ip not in ip_set:
        ip_set.add(ip)


def fetch_data_from_connect_server(base_url, limit, start_offset, end_offset, headers):
    offset = start_offset
    while offset <= end_offset:
        url = f"{base_url}?limit={limit}&offset={offset}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = json.loads(response.text)

            # print the raw response JSON data
            # print(json.dumps(data, indent=4))

            for request in data:
                # Convert the timestamp from ISO 8601 format to CLF date format
                timestamp = dateutil.parser.isoparse(request["timestamp"])
                clf_date = timestamp.strftime("%d/%b/%Y:%H:%M:%S %z")

                # Print the log entry in the CLF format
                print(
                    f"{request['actor']['requestIp']} {request['actor']['userAgent']} {request['actor']['id']} [{clf_date}] \"{request['action']} {request['resource']['type']} HTTP/1.1\" 200 -"
                )

                add_ip(request["actor"]["requestIp"])
        else:
            print(
                f"Failed to fetch data from {url}, status code: {response.status_code}"
            )
        offset += limit


if __name__ == "__main__":
    main()
