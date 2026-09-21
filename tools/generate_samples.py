"""Create schedule examples and their expected console output; stdlib only."""
from pathlib import Path
from datetime import date, timedelta
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"


def row(day, kind, topic, room, teachers):
    return [str(day), kind, topic, room, teachers]


FIRST = [
    row("2026-10-05", "ЛЕКЦИЯ", "Классы и делегирование", "ауд. 312", "Портнов"),
    row("2026-10-08", "ПРАКТИКУМ", "Моделируем домен", "ауд. 312", "Анохин"),
    row("2026-10-15", "СДАЧА", "Устная сдача №1", "ауд. 401", "Портнов,Степанова"),
    row("2026-10-19", "ОТМЕНА", "Лекция перенесена на 20.10", "—", "—"),
]


def render(fields, teachers=False):
    d, kind, topic, room, names = fields
    values = [d, kind, topic, room]
    if teachers:
        values.append(names.replace(",", ", "))
    return " | ".join(values) + "\n"


def write(name, value):
    data = value.encode("utf-8") if isinstance(value, str) else value
    (SAMPLES / name).write_bytes(data)


def digest(data):
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def generate(huge=False):
    SAMPLES.mkdir(exist_ok=True)
    clean = FIRST.copy()
    for i in range(196):
        day = date(2026, 9, 28) + timedelta(days=(i * 17) % 228)
        kind = ["ЛЕКЦИЯ", "ПРАКТИКУМ", "СДАЧА", "ОТМЕНА"][i % 4]
        clean.append(row(day, kind, f"Тема {i + 5:03}", "—" if kind == "ОТМЕНА" else "ауд. 312",
                         "—" if kind == "ОТМЕНА" else "Портнов,Степанова" if kind == "СДАЧА" else "Анохин"))
    clean[-1] = row("2027-05-13", "ЛЕКЦИЯ", "Итоговое занятие", "ауд. 312", "Портнов")
    dirty = FIRST.copy() + [row("2026-11-01", "ЛЕКЦИЯ", f"Тема {i:03}", "ауд. 312", "Анохин") for i in range(5, 501)]
    corruptions = [
        ("2026-13-45|ЛЕКЦИЯ|Тема|ауд. 1|Иванов", "несуществующая дата «2026-13-45»"),
        ("|ЛЕКЦИЯ|Тема|ауд. 1|Иванов", "пустое обязательное поле «дата»"),
        ("2026-10-05|СЕМИНАР|Тема|ауд. 1|Иванов", "неизвестный тип занятия «СЕМИНАР»"),
        ("2026-10-05;ЛЕКЦИЯ;Тема;ауд. 1;Иванов", "неверный разделитель полей"),
        ("2026-10-05|СДАЧА|Тема|ауд. 1|Иванов", "у типа «СДАЧА» должно быть не менее двух преподавателей, получено 1"),
        ("2026-10-05|ЛЕКЦИЯ|Тема|ауд. 1|Иванов|лишнее", "полей 6, ожидалось 5"),
    ]
    failures = {}
    for index, number in enumerate([14, 27, 31] + list(range(32, 193))):
        raw, message = corruptions[index % len(corruptions)]
        dirty[number - 1] = raw
        failures[number] = f"строка {number}: {message}\n"
    assert len(clean) == 200 and len(dirty) == 500 and len(failures) == 164
    manifest = {"generator": "v2", "commands": {}, "files": {}}
    for name, records, rejected in [("clean.txt", clean, {}), ("dirty.txt", dirty, failures), ("empty.txt", [], {})]:
        write(name, "".join(("|".join(r) if isinstance(r, list) else r) + "\n" for r in records))
        valid = [r for r in records if isinstance(r, list)]
        outputs = {
            "period": "".join(render(r) for r in valid) + f"Всего: {len(valid)}\n",
            "type": "".join(render(r, True) for r in valid if r[1] == "СДАЧА") + f"Всего: {sum(r[1] == 'СДАЧА' for r in valid)}\n",
            "errors": "".join(rejected.values()) + f"Всего отклонено: {len(rejected)} из {len(records)}\n",
        }
        for command, output in outputs.items():
            expected = f"{name.removesuffix('.txt')}.{command}.expected"
            write(expected, output)
            manifest["commands"][f"{name}/{command}"] = {"code": int(bool(rejected)), "expected": expected, **digest(output.encode())}
    write("clean.expected", (SAMPLES / "clean.period.expected").read_bytes())
    write("dirty.october.expected", "".join(render(r) for r in FIRST) + "Всего: 4\n")
    huge_row = row("2026-10-05", "ЛЕКЦИЯ", "Потоковый разбор", "ауд. 312", "Портнов")
    block = ("|".join(huge_row) + "\n").encode()
    count = 2_000_000
    if huge:
        with (SAMPLES / "huge.txt").open("wb") as target:
            for _ in range(count // 10_000): target.write(block * 10_000)
    for command in ("period", "type", "errors"):
        h = hashlib.sha256()
        total = 0
        if command == "period":
            chunk = render(huge_row).encode() * 10_000
            for _ in range(count // 10_000): h.update(chunk); total += len(chunk)
        last = "Всего: 2000000\n" if command == "period" else "Всего: 0\n" if command == "type" else "Всего отклонено: 0 из 2000000\n"
        h.update(last.encode()); total += len(last.encode())
        manifest["commands"][f"huge.txt/{command}"] = {"code": 0, "bytes": total, "sha256": h.hexdigest()}
    for path in sorted(SAMPLES.iterdir()):
        if path.is_file() and path.name != "manifest.json":
            h = hashlib.sha256()
            with path.open("rb") as source:
                while chunk := source.read(1024 * 1024): h.update(chunk)
            manifest["files"][path.name] = {"bytes": path.stat().st_size, "sha256": h.hexdigest()}
    (SAMPLES / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"clean": 200, "dirty": 500, "rejected": 164, "huge_lines": count if huge else "not generated", "huge_bytes": len(block) * count}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--huge", action="store_true")
    generate(parser.parse_args().huge)
