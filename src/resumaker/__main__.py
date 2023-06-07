from argparse import ArgumentParser

from .resumaker import resumake


def main():
    p = ArgumentParser()
    p.add_argument("org_resume")
    p.add_argument("--scale", "-s", type=float, default=1.0)
    p.add_argument("--template", "-t", type=str, default="console")
    p.add_argument("--ftype", "-f", choices=("html", "pdf"), default="html")
    args = p.parse_args()
    resumake(**vars(args))


if __name__ == "__main__":
    raise SystemExit(main())
