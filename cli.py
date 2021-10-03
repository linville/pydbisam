import argparse
from pydbisam import PyDBISAM


def main():
    parser = argparse.ArgumentParser(description="Extract data from OE archives.")
    parser.add_argument(
        "path", metavar="path-to-dat", type=str, help="Path to OE archive."
    )

    args = parser.parse_args()

    with PyDBISAM(args.path) as db:
        db.dump()


if __name__ == "__main__":
    main()
