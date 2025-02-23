import os
import zipfile
import glob
import shutil

try:
    import gdown
except ImportError:
    print(
        "The gdown package is required. Use `pip install gdown` to install it."
    )

# This will fetch the lectures from latest wasm branch
LECTURE_INTRO_URL = "https://github.com/QuantEcon/lecture-python-intro/archive/refs/heads/wasm.zip"
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def download_lectures(
    url=None,
    output=None,
    quiet=False,
    unzip=True,
    overwrite=False,
    subfolder=False,
):
    """
    Downloads the lecture folder from GitHub repository and
    returns the output file path.
    """

    if output is None:
        if isinstance(url, str) and url.startswith("http"):
            output = os.path.basename(url)

    out_dir = os.path.abspath(os.path.dirname(output))
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    if isinstance(url, str):
        if os.path.exists(os.path.abspath(output)) and (not overwrite):
            print(
                f"{output} already exists. Skip downloading. Set overwrite=True to overwrite."
            )
            return os.path.abspath(output)

    output = gdown.download(url, output)

    if unzip and output.endswith(".zip"):
        with zipfile.ZipFile(output, "r") as zip_ref:
            if not quiet:
                print("Extracting files...")
            if subfolder:
                basename = os.path.splitext(os.path.basename(output))[0]

                output = os.path.join(out_dir, basename)
                if not os.path.exists(output):
                    os.makedirs(output)
                zip_ref.extractall(output)
            else:
                zip_ref.extractall(os.path.dirname(output))

    return os.path.abspath(output)


def update_pip_line(line):
    line_ = line
    if ("!pip" in line_) and ("install" in line_):
        line_ = line_.replace("!", "").replace("pip", "%pip")
        line_ = line_.replace("--upgrade", "")
    return line_


def update_lectures():
    out_zip = 'qe-lecture-intro-wasm.zip'
    out_zip = download_lectures(LECTURE_INTRO_URL, out_zip)

    in_dir_1 = os.path.abspath(os.path.join(ROOT_DIR, 'lecture-python-intro-wasm'))
    in_dir_2 = os.path.abspath(os.path.join(in_dir_1, 'lectures'))
    out_dir = os.path.abspath(os.path.join(ROOT_DIR, 'book'))

    shutil.copytree(in_dir_2, out_dir, dirs_exist_ok=True)
    cwd = os.getcwd()
    os.chdir(cwd)


    lectures = glob.glob(os.path.abspath(os.path.join(out_dir, '*.md')))

    # Update file lines
    for file in lectures:
        base_name = os.path.basename(file)
        with open(file, 'r') as f:
            lines = f.readlines()

        out_lines = []
        for index, line in enumerate(lines):
            line_ = update_pip_line(line)
            out_lines.append(line_)

        with open(file, 'w') as f:
            f.writelines(out_lines)

    # Update _config.yml file
    source_config = os.path.abspath(os.path.join(ROOT_DIR, '_config_copy.yml'))
    destination_config = os.path.abspath(os.path.join(out_dir, '_config.yml'))
    shutil.copyfile(source_config, destination_config)

    # Remove downloaded folder
    shutil.rmtree('lecture-python-intro-wasm')
    os.remove(out_zip)

if __name__ == '__main__':
    update_lectures()