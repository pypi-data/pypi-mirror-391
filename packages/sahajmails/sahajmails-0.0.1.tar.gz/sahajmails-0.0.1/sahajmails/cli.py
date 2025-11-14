import argparse
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description='SahajMails CLI')
    subparsers = parser.add_subparsers(dest='command')
    run_parser = subparsers.add_parser('run', help='Run the Streamlit app')
    args = parser.parse_args()

    if args.command == 'run':
        # Launch Streamlit app using subprocess
        try:
            subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'sahajmails/app.py'])
        except Exception as e:
            print(f"Error launching app: {e}")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()