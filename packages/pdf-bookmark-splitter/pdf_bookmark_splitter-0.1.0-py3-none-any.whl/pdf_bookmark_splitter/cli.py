from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser(description="Split PDF file into chapters based on bookmarks")
    parser.add_argument("file", help="The PDF file to process")
    parser.add_argument("--output-dir", default="chapters", help="The directory to save the chapters")

    return parser.parse_args()
