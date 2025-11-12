import sys

from cvo251102lib import hello


def main() -> None:
    if len(sys.argv) > 1:
        print(hello(someone=sys.argv[1]))
    else:
        print(hello())


def lambda_handler(event: dict, context: object) -> dict:
    if "someone" in event["queryStringParameters"]:
        print(hello(someone=event["queryStringParameters"]["someone"]))
    else:
        print(hello())

    return {"message": "Success!"}
