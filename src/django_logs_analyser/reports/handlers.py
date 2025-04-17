from . import register_report
from .base import Report


@register_report
class HandlersReport(Report[dict[str, dict[str, int]]]):
    """Отчет о состоянии ручек API по уровням логирования.
    """

    name = "handlers"
    LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def process_file(self, path: str) -> dict[str, dict[str, int]]:
        counts: dict[str, dict[str, int]] = {}
        with open(path, encoding="utf-8") as f:
            for line in f:
                if "django.requests" not in line:
                    continue
                parts = line.split()
                if len(parts) < 6:
                    continue
                level = parts[2]
                handler = parts[5]
                if level not in self.LEVELS:
                    continue

                # Инициализируем словарь по новой ручке, если нужно
                if handler not in counts:
                    counts[handler] = dict.fromkeys(self.LEVELS, 0)
                counts[handler][level] += 1

        return counts

    def combine(
            self, results: list[dict[str, dict[str, int]]],
    ) -> dict[str, dict[str, int]]:
        combined: dict[str, dict[str, int]] = {}
        for partial in results:
            for handler, lvl_counts in partial.items():
                if handler not in combined:
                    combined[handler] = dict.fromkeys(self.LEVELS, 0)
                for lvl, cnt in lvl_counts.items():
                    combined[handler][lvl] += cnt
        return combined

    def render(self, data: dict[str, dict[str, int]]) -> str:
        total_requests = sum(
            cnt for lvl_counts in data.values() for cnt in lvl_counts.values()
        )
        lines: list[str] = [f"Total requests: {total_requests}", ""]

        # Заголовок
        lines.append("\t".join(["HANDLER"] + self.LEVELS))

        # По каждой ручке (в алфавитном порядке)
        for handler in sorted(data.keys()):
            row = [handler] + [str(data[handler].get(lvl, 0)) for lvl in self.LEVELS]
            lines.append("\t".join(row))

        # Итоги по уровням
        totals = [str(sum(data[h].get(lvl, 0) for h in data)) for lvl in self.LEVELS]
        lines.append("\t".join([""] + totals))

        return "\n".join(lines)
