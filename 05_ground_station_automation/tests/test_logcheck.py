import pytest

from src.logcheck import format_summary, scan_dir, scan_file


def test_scan_file_counts_error_and_missed(tmp_path):
    f = tmp_path / "a.log"
    f.write_text("2026-11-02 01:00:00 INFO  ok\n"
                 "2026-11-02 01:01:00 ERROR bad\n"
                 "2026-11-02 01:02:00 MISSED skipped\n"
                 "2026-11-02 01:03:00 INFO  the word ERROR in text only\n")
    r = scan_file(f)
    assert len(r["errors"]) == 1
    assert len(r["missed"]) == 1


def test_summary_has_totals(tmp_path):
    (tmp_path / "a.log").write_text("2026-11-02 01:00:00 ERROR x\n")
    (tmp_path / "b.log").write_text("2026-11-02 01:00:00 MISSED y\n")
    text = format_summary(scan_dir(tmp_path))
    assert "TOTAL: 1 ERROR, 1 MISSED in 2 files" in text


def test_empty_log_dir_raises(tmp_path):
    with pytest.raises(ValueError):
        scan_dir(tmp_path)
