from argparse import ArgumentParser

from .resumaker import resumake


def main():
    p = ArgumentParser()
    p.add_argument("org_resume")
    p.add_argument("--scale", "-s", type=float, default=1.0)
    p.add_argument("--template", "-t", type=str, default="console")
    args = p.parse_args()
    resumake(args.org_resume, scale=args.scale, template=args.template)


if __name__ == "__main__":
    raise SystemExit(main())
