# run_streamlit.py
import subprocess

def run_streamlit_app(file_name):
    subprocess.Popen(['streamlit', 'run', file_name])

if __name__ == '__main__':
    run_streamlit_app('main.py')