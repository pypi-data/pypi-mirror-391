#!/usr/bin/env python3
"""
main.py — модуль для экспорта/импорта графовых проектов в файловую структуру.
"""

import json
import argparse
from pathlib import Path


def sanitize_name(name: str) -> str:
    """Очищает имя от недопустимых символов."""
    return "".join(char if char.isalnum() or char in "-_" else "_" for char in name.strip())


class FlowExporter:
    """Класс для экспорта и импорта графов."""

    NORM_NODE = "0"
    NORM_POINT = [100000, 100000]

    def __init__(self, input_path: str = None, output_dir: str = None):
        self.input_path = Path(input_path) if input_path else None
        self.output_dir = Path(output_dir) if output_dir else None

    @staticmethod
    def create_reference_node(node_id: str, position: list[float]):
        """Создает ноду-заметку для нормализации."""
        x, y = position
        return {
            "id": node_id,
            "data": {
                "_ref_id": node_id,
                "type": "note",
                "node": {"template": {"backgroundColor": "transparent"}},
            },
            "position": {"x": x, "y": y},
            "type": "noteNode",
        }

    @staticmethod
    def normalize_positions(nodes, reference_id, position):
        """Нормализует позиции узлов относительно опорной ноды."""
        if not nodes:
            return nodes

        ref_node = next(
            (n for n in nodes if n.get("data", {}).get("_ref_id") == reference_id), None
        )
        if not ref_node:
            return nodes

        ref_x, ref_y = ref_node["position"].get("x", 0), ref_node["position"].get("y", 0)
        x, y = position
        delta_x, delta_y = ref_x - x, ref_y - y

        for node in nodes:
            pos = node.get("position", {})
            if pos:
                pos["x"] = pos.get("x", 0) - delta_x
                pos["y"] = pos.get("y", 0) - delta_y
        return nodes

    @staticmethod
    def create_id_mappings(nodes, reference_node):
        """Создает маппинги между ID узлов."""
        id_to_ref, ref_to_id = {}, {}
        has_reference = False

        for node in nodes:
            node_id = node["id"]
            data = node.setdefault("data", {})
            ref_id = data.get("_ref_id", node_id)
            data["_ref_id"] = ref_id
            id_to_ref[node_id] = ref_id
            ref_to_id[ref_id] = node_id
            if ref_id == reference_node:
                has_reference = True

        return id_to_ref, ref_to_id, has_reference

    @staticmethod
    def extract_code_to_files(nodes, src_dir: Path, skip_id: str):
        """Извлекает код из узлов в отдельные файлы."""
        src_dir.mkdir(parents=True, exist_ok=True)
        for node in nodes:
            data = node.get("data", {})
            if data.get("_ref_id") == skip_id:
                continue
            try:
                code = data["node"]["template"]["code"]["value"].strip()
                if code:
                    filename = f"{sanitize_name(data['_ref_id'])}.py"
                    (src_dir / filename).write_text(code, encoding="utf-8")
                    data["node"]["template"]["code"]["value"] = f"@file:src/{filename}"
            except (KeyError, AttributeError):
                continue

    @staticmethod
    def process_edges(edges, id_map, edges_dir: Path):
        """Обрабатывает и сохраняет связи между узлами."""
        edges_dir.mkdir(parents=True, exist_ok=True)
        for edge in edges:
            edge = edge.copy()
            edge["source"] = id_map.get(edge["source"], edge["source"])
            edge["target"] = id_map.get(edge["target"], edge["target"])

            if "data" in edge:
                data = edge["data"]
                for field in ["sourceHandle", "targetHandle"]:
                    if field in data and "id" in data[field]:
                        data[field]["id"] = id_map.get(data[field]["id"], data[field]["id"])

            for field in ["id", "sourceHandle", "targetHandle"]:
                edge.pop(field, None)
            edge.get("data", {}).pop("id", None)

            src, tgt = sanitize_name(edge["source"]), sanitize_name(edge["target"])
            (edges_dir / f"{src}__{tgt}.json").write_text(
                json.dumps(edge, indent=2, ensure_ascii=False), encoding="utf-8"
            )

    def export_project(self) -> Path:
        """Экспортирует проект в файловую структуру."""
        project = json.loads(self.input_path.read_text(encoding="utf-8"))
        data = project.get("data", {})
        nodes, edges = data.get("nodes", []), data.get("edges", [])

        nodes_dir, edges_dir, src_dir = [
            self.output_dir / name for name in ["nodes", "edges", "src"]
        ]

        id_map, _, has_ref = self.create_id_mappings(nodes, self.NORM_NODE)
        if not has_ref:
            nodes.insert(0, self.create_reference_node(self.NORM_NODE, self.NORM_POINT))

        self.normalize_positions(nodes, self.NORM_NODE, self.NORM_POINT)

        nodes_dir.mkdir(parents=True, exist_ok=True)
        for node in nodes:
            ref_id = id_map.get(node["id"], node["id"])
            if ref_id == self.NORM_NODE:
                continue
            node_data = node.copy()
            node_data.pop("id", None)
            node_data["data"].pop("id", None)
            (nodes_dir / f"{sanitize_name(ref_id)}.json").write_text(
                json.dumps(node_data, indent=2, ensure_ascii=False), encoding="utf-8"
            )

        self.extract_code_to_files(nodes, src_dir, self.NORM_NODE)
        self.process_edges(edges, id_map, edges_dir)

        meta = {k: project.get(k) for k in ["endpoint_name", "is_component", "last_tested_version", "tags"]}
        (self.output_dir / "flow.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

        return self.output_dir / "flow.json"

    @staticmethod
    def import_project(flow_path: str, restore_dir: str) -> Path:
        """Импортирует проект обратно в JSON."""
        exporter = FlowExporter()
        NORM_NODE = exporter.NORM_NODE
        NORM_POINT = exporter.NORM_POINT

        project_root = Path(flow_path).parent
        restore_dir = Path(restore_dir)
        restore_dir.mkdir(parents=True, exist_ok=True)

        flow_data = json.loads(Path(flow_path).read_text(encoding="utf-8"))
        nodes = [exporter.create_reference_node(NORM_NODE, NORM_POINT)]

        # Восстановление нод
        nodes_dir = project_root / "nodes"
        if nodes_dir.exists():
            for node_file in nodes_dir.glob("*.json"):
                node = json.loads(node_file.read_text(encoding="utf-8"))
                data = node["data"]
                try:
                    code_ref = data["node"]["template"]["code"]["value"]
                    if isinstance(code_ref, str) and code_ref.startswith("@file:"):
                        code_path = project_root / code_ref[6:]
                        if code_path.exists():
                            data["node"]["template"]["code"]["value"] = code_path.read_text(encoding="utf-8")
                except (KeyError, AttributeError):
                    pass
                node["id"] = data["_ref_id"]
                nodes.append(node)

        edges = []
        edges_dir = project_root / "edges"
        if edges_dir.exists():
            edges = [json.loads(f.read_text(encoding="utf-8")) for f in edges_dir.glob("*.json")]

        project = {
            "data": {"nodes": nodes, "edges": edges},
            **{k: flow_data.get(k) for k in ["endpoint_name", "is_component", "last_tested_version", "tags"]},
        }

        output_path = restore_dir / "restored_project.json"
        output_path.write_text(json.dumps(project, indent=2, ensure_ascii=False), encoding="utf-8")
        return output_path


def main():
    parser = argparse.ArgumentParser(description="Экспорт и импорт JSON-проектов графов.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_p = subparsers.add_parser("export", help="Экспортирует проект в файловую структуру.")
    export_p.add_argument("input", help="Путь к входному JSON-файлу.")
    export_p.add_argument("output", help="Папка для вывода результата.")

    import_p = subparsers.add_parser("import", help="Импортирует проект обратно в JSON.")
    import_p.add_argument("flow", help="Путь к flow.json.")
    import_p.add_argument("restore", help="Папка для восстановленного JSON.")

    args = parser.parse_args()

    if args.command == "export":
        flow = FlowExporter(args.input, args.output)
        result = flow.export_project()
        print(f"Проект экспортирован: {result}")
    elif args.command == "import":
        result = FlowExporter.import_project(args.flow, args.restore)
        print(f"Проект импортирован: {result}")
