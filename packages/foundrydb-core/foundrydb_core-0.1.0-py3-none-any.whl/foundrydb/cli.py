# in cli.py
from foundrydb.database import Database


def main():
    db = Database("foundries/cli_demo")
    print("FoundryDB CLI ready. Type '.exit' to quit.")
    while True:
        sql = input("foundrydb> ").strip()
        if sql in (".exit", "exit", "quit"):
            break
        result = db.execute(sql)
        if result:
            for row in result:
                print(row)
