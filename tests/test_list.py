import json

from .fixtures import *

def test_list_json(process, disable_extractors_dict):
    subprocess.run(["archivebox", "add", "http://127.0.0.1:8080/static/example.com.html", "--depth=0"],
                                  capture_output=True, env=disable_extractors_dict)
    list_process = subprocess.run(["archivebox", "list", "--json"], capture_output=True)
    output_json = json.loads(list_process.stdout.decode("utf-8"))
    assert output_json[0]["url"] == "http://127.0.0.1:8080/static/example.com.html"


def test_list_json_index(process, disable_extractors_dict):
    subprocess.run(["archivebox", "add", "http://127.0.0.1:8080/static/example.com.html", "--depth=0"],
                                  capture_output=True, env=disable_extractors_dict)
    list_process = subprocess.run(["archivebox", "list", "--json", "--index"], capture_output=True)
    output_json = json.loads(list_process.stdout.decode("utf-8"))
    assert output_json["links"][0]["url"] == "http://127.0.0.1:8080/static/example.com.html"

def test_list_html(process, disable_extractors_dict):
    subprocess.run(["archivebox", "add", "http://127.0.0.1:8080/static/example.com.html", "--depth=0"],
                                  capture_output=True, env=disable_extractors_dict)
    list_process = subprocess.run(["archivebox", "list", "--html"], capture_output=True)
    output_html = list_process.stdout.decode("utf-8")
    assert "<footer>" not in output_html
    assert "http://127.0.0.1:8080/static/example.com.html" in output_html

def test_list_html_index(process, disable_extractors_dict):
    subprocess.run(["archivebox", "add", "http://127.0.0.1:8080/static/example.com.html", "--depth=0"],
                                  capture_output=True, env=disable_extractors_dict)
    list_process = subprocess.run(["archivebox", "list", "--html", "--index"], capture_output=True)
    output_html = list_process.stdout.decode("utf-8")
    assert "<footer>" in output_html
    assert "http://127.0.0.1:8080/static/example.com.html" in output_html

def test_list_index_with_wrong_flags(process):
    list_process = subprocess.run(["archivebox", "list", "--index"], capture_output=True)
    assert "--index can only be used with --json or --html options." in list_process.stderr.decode("utf-8")