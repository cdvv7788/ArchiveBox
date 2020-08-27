import subprocess
import json

from .fixtures import *

def test_depth_flag_is_accepted(process, disable_extractors_dict):
    arg_process = subprocess.run(["archivebox", "add", "http://127.0.0.1:8080/static/example.com.html", "--depth=0"],
                                  capture_output=True, env=disable_extractors_dict)
    assert 'unrecognized arguments: --depth' not in arg_process.stderr.decode("utf-8")


def test_depth_flag_fails_if_it_is_not_0_or_1(process, disable_extractors_dict):
    arg_process = subprocess.run(
        ["archivebox", "add", "--depth=5", "http://127.0.0.1:8080/static/example.com.html"],
        capture_output=True,
        env=disable_extractors_dict,
    )
    assert 'invalid choice' in arg_process.stderr.decode("utf-8")
    arg_process = subprocess.run(
        ["archivebox", "add", "--depth=-1", "http://127.0.0.1:8080/static/example.com.html"],
        capture_output=True,
        env=disable_extractors_dict,
    )
    assert 'invalid choice' in arg_process.stderr.decode("utf-8")


def test_depth_flag_0_crawls_only_the_arg_page(tmp_path, process, disable_extractors_dict):
    arg_process = subprocess.run(
        ["archivebox", "add", "--depth=0", "http://127.0.0.1:8080/static/example.com.html"],
        capture_output=True,
        env=disable_extractors_dict,
    )
    
    archived_item_path = list(tmp_path.glob('archive/**/*'))[0]
    with open(archived_item_path / "index.json", "r") as f:
        output_json = json.load(f)
    assert output_json["base_url"] == "127.0.0.1:8080/static/example.com.html"


def test_depth_flag_1_crawls_the_page_AND_links(tmp_path, process, disable_extractors_dict):
    arg_process = subprocess.run(
        ["archivebox", "add", "--depth=1", "http://127.0.0.1:8080/static/example.com.html"],
        capture_output=True,
        env=disable_extractors_dict,
    )
    
    with open(tmp_path / "index.json", "r") as f:
        archive_file = f.read()
    assert "http://127.0.0.1:8080/static/example.com.html" in archive_file
    assert "http://127.0.0.1:8080/static/iana.org.html" in archive_file


def test_overwrite_flag_is_accepted(process, disable_extractors_dict):
    subprocess.run(
        ["archivebox", "add", "--depth=0", "http://127.0.0.1:8080/static/example.com.html"],
        capture_output=True,
        env=disable_extractors_dict,
    )
    arg_process = subprocess.run(
        ["archivebox", "add", "--overwrite", "http://127.0.0.1:8080/static/example.com.html"],
        capture_output=True,
        env=disable_extractors_dict,
    )
    assert 'unrecognized arguments: --overwrite' not in arg_process.stderr.decode("utf-8")
    assert 'favicon' in arg_process.stdout.decode('utf-8'), 'archive methods probably didnt run, did overwrite work?'

def test_add_updates_history_json_index(tmp_path, process, disable_extractors_dict):
    subprocess.run(
        ["archivebox", "add", "--depth=0", "http://127.0.0.1:8080/static/example.com.html"],
        capture_output=True,
        env=disable_extractors_dict,
    )

    with open(tmp_path / "index.json", "r") as f:
        output_json = json.load(f)
    assert output_json["links"][0]["history"] != {}

def test_add_link(tmp_path, process, disable_extractors_dict):
    disable_extractors_dict.update({"USE_WGET": "true"})
    os.chdir(tmp_path)
    add_process = subprocess.run(['archivebox', 'add', 'http://127.0.0.1:8080/static/example.com.html'],
                                  capture_output=True, env=disable_extractors_dict)
    archived_item_path = list(tmp_path.glob('archive/**/*'))[0]

    assert "index.json" in [x.name for x in archived_item_path.iterdir()]

    with open(archived_item_path / "index.json", "r") as f:
        output_json = json.load(f)
    assert "Example Domain" == output_json['history']['title'][0]['output']

    with open(tmp_path / "index.html", "r") as f:
        output_html = f.read()
    assert "Example Domain" in output_html

def test_add_link_support_stdin(tmp_path, process, disable_extractors_dict):
    disable_extractors_dict.update({"SAVE_TITLE": "true"})
    os.chdir(tmp_path)
    stdin_process = subprocess.Popen(["archivebox", "add"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                      env=disable_extractors_dict)
    stdin_process.communicate(input="http://127.0.0.1:8080/static/example.com.html".encode())
    archived_item_path = list(tmp_path.glob('archive/**/*'))[0]

    assert "index.json" in [x.name for x in archived_item_path.iterdir()]

    with open(archived_item_path / "index.json", "r") as f:
        output_json = json.load(f)
    assert "Example Domain" == output_json['history']['title'][0]['output']
