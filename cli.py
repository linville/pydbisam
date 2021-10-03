import argparse
from pydbisam import PyDBISAM


def main():
    parser = argparse.ArgumentParser(
        description="Extract data from DBISAM database tables."
    )
    parser.add_argument(
        "path", metavar="path-to-dat", type=str, help="Path to DBISAM table dat file."
    )
    parser.add_argument(
        "--dump-csv", action="store_true", help="Export the table data as a CSV."
    )

    args = parser.parse_args()

    with PyDBISAM(args.path) as db:
        if args.dump_csv:
            exit("Not yet implemented.")

        db.dump_structure()


if __name__ == "__main__":
    main()
