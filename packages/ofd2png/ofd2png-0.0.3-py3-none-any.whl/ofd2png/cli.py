import argparse
import sys
from . import convert_file, convert_folder
# 使用包的对外 API，避免直接依赖 converter 内部实现

def main():
    parser = argparse.ArgumentParser(description='OFD to PNG Converter')
    subparsers = parser.add_subparsers(dest='command')

    single = subparsers.add_parser('single', help='Convert a single OFD file to PNG(s)')
    single.add_argument('ofd_path', help='Path to the OFD file')

    batch = subparsers.add_parser('batch', help='Convert all OFD files in a directory')
    batch.add_argument('input_dir', help='Path to the input directory containing .ofd files')

    args = parser.parse_args()

    try:
        if args.command == 'single':
            convert_file(args.ofd_path)
        elif args.command == 'batch':
            convert_folder(args.input_dir)
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
