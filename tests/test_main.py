import pytest

from django_logs_analyser.main import run


def test_missing_file(tmp_path, capsys):
    missing = tmp_path / "nofile.log"
    exit_code = run([str(missing), "--report", "handlers"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error: File not found" in captured.err


def test_invalid_report(tmp_path):
    f = tmp_path / "log.log"
    f.write_text("")
    with pytest.raises(SystemExit):
        run([str(f), "--report", "unknown"])


def test_success(tmp_path, capsys):
    f1 = tmp_path / "log1.log"
    f2 = tmp_path / "log2.log"
    f1.write_text(
        "\n".join([
            "2025-04-01 10:00:00,000 INFO django.requests GET /a/ request",
            "2025-04-01 10:00:01,000 DEBUG django.requests GET /b/ request",
        ]),
    )
    f2.write_text(
        "\n".join([
            "2025-04-01 11:00:00,000 INFO django.requests GET /a/ request",
            "2025-04-01 11:00:01,000 WARNING django.requests GET /c/ request",
        ]),
    )
    exit_code = run([str(f1), str(f2), "--report", "handlers"])
    assert exit_code == 0
    captured = capsys.readouterr()
    out_lines = captured.out.strip().splitlines()
    assert out_lines[0] == "Total requests: 4"
    # заголовок на третьей строке
    assert out_lines[2] == "HANDLER\tDEBUG\tINFO\tWARNING\tERROR\tCRITICAL"
    # ручки в алфавитном порядке
    handlers = [line.split("\t")[0] for line in out_lines[3:6]]
    assert handlers == ["/a/", "/b/", "/c/"]
