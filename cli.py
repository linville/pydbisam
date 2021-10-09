import argparse
from pydbisam import PyDBISAM


def main():
    parser = argparse.ArgumentParser(
        description="Extract data from DBISAM database tables."
    )
    parser.add_argument(
        "path", metavar="path-to-dat", type=str, help="Path to DBISAM table dat file."
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--dump-structure",
        action="store_true",
        help="Dump the table structure to stdout. Default behavior.",
    )
    group.add_argument(
        "--dump-csv", action="store_true", help="Export the table data as a CSV."
    )

    args = parser.parse_args()

    with PyDBISAM(args.path) as db:
        if args.dump_csv:
            print(", ".join(db.fields()))
            for row in db.rows():
                print(", ".join(map(str, row)))
            exit()

        db.dump_structure()


if __name__ == "__main__":
    main()
