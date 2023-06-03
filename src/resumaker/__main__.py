from argparse import ArgumentParser

from .resumaker import resumake


def main():
    p = ArgumentParser()
    p.add_argument("meta_resume")
    p.add_argument("--scale", "-s", type=float, default=1.0)
    args = p.parse_args()
    resumake(args.meta_resume, scale=args.scale)


if __name__ == "__main__":
    raise SystemExit(main())
