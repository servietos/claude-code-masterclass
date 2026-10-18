import argparse

from db import init_db
from rentals import add_bike, list_open, rent_bike, return_bike


def main():
    parser = argparse.ArgumentParser(prog="app.py")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add-bike")
    p.add_argument("label")
    p.add_argument("frame_size")

    p = sub.add_parser("rent")
    p.add_argument("label")
    p.add_argument("name")
    p.add_argument("phone")
    p.add_argument("--days", type=int, default=1)

    p = sub.add_parser("return")
    p.add_argument("label")

    sub.add_parser("open")

    args = parser.parse_args()
    init_db()

    if args.command == "add-bike":
        add_bike(args.label, args.frame_size)
        print(f"added {args.label}")
    elif args.command == "rent":
        due = rent_bike(args.label, args.name, args.phone, args.days)
        print(f"{args.label} due {due.isoformat()}")
    elif args.command == "return":
        fee = return_bike(args.label)
        print(f"{args.label} returned, late fee {fee / 100:.2f}")
    elif args.command == "open":
        for row in list_open():
            print(f"{row['label']}\t{row['name']}\t{row['phone']}\t{row['due_at']}")


if __name__ == "__main__":
    main()
