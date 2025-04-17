import pytest
from django_logs_analyser.reports.handlers import HandlersReport


@pytest.fixture
def report():
    return HandlersReport()


def test_process_file(tmp_path, report):
    log = tmp_path / "test.log"
    log.write_text(
        "\n".join([
            "2025-04-01 10:00:00,000 DEBUG django.requests GET /a/ info",
            "2025-04-01 10:00:01,000 INFO django.requests GET /b/ info",
            "2025-04-01 10:00:02,000 WARNING other.logger message",
        ])
    )
    result = report.process_file(str(log))
    assert result["/a/"]["DEBUG"] == 1
    assert result["/b/"]["INFO"] == 1
    assert "/c/" not in result


def test_combine(report):
    r1 = {"/a/": {"DEBUG": 1}, "/b/": {"INFO": 2}}
    r2 = {"/a/": {"DEBUG": 2}, "/c/": {"WARNING": 3}}
    combined = report.combine([r1, r2])
    assert combined["/a/"]["DEBUG"] == 3
    assert combined["/b/"]["INFO"] == 2
    assert combined["/c/"]["WARNING"] == 3


def test_render(report):
    data = {
        "/a/": {"DEBUG": 1, "INFO": 2},
        "/b/": {"INFO": 3},
    }
    output = report.render(data)
    lines = output.splitlines()
    # total 1+2+3=6
    assert lines[0] == "Total requests: 6"
    assert lines[2] == "HANDLER\tDEBUG\tINFO\tWARNING\tERROR\tCRITICAL"
    # строки для /a/ и /b/
    row_a = lines[3].split("\t")
    assert row_a[0] == "/a/"
    assert row_a[1] == "1"
    assert row_a[2] == "2"
    row_b = lines[4].split("\t")
    assert row_b[0] == "/b/"
    assert row_b[1] == "0"
    assert row_b[2] == "3"
    # bottom totals
    bottom = lines[5].split("\t")
    assert bottom[1:] == ["1", "5", "0", "0", "0"]
