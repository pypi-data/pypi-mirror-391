import json
from pathlib import Path
from flow_exporter import FlowExporter


def test_export_and_import_from_real_file(tmp_path):
    """Проверка экспорта/импорта проекта на реальном входном файле."""
    input_file = Path("tests/input.json")
    assert input_file.exists(), "Файл tests/input.json должен существовать!"

    print(tmp_path)
    export_dir = tmp_path / "exported"
    restore_dir = tmp_path / "restored"

    # === Экспорт ===
    exporter = FlowExporter(str(input_file), str(export_dir))
    flow_json = exporter.export_project()
    assert flow_json.exists(), "flow.json должен быть создан"

    # Проверяем, что создались подкаталоги
    for sub in ["nodes", "edges", "src"]:
        assert (export_dir / sub).exists(), f"папка {sub} не создана"

    # Проверяем, что код вынесен в отдельный файл
    src_files = list((export_dir / "src").glob("*.py"))
    assert len(src_files) >= 1

    # === Импорт ===
    restored_path = FlowExporter.import_project(str(flow_json), str(restore_dir))
    assert restored_path.exists(), "Файл restored_project.json должен быть создан"

    restored_json = json.loads(restored_path.read_text(encoding="utf-8"))
    assert len(restored_json) > 0
