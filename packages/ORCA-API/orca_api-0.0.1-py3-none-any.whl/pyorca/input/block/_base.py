"""Base class for ORCA input blocks."""


class InputBlock:

    def __init__(self, name: str, settings: dict, indent: int = 3):
        self.name = name
        self.settings = settings
        self.indent = indent
        return

    def __str__(self) -> str:
        if not self.settings:
            raise ValueError(f"Input block '{self.name}' has no settings.")
        settings_str = self._to_string(self.settings)
        return f"%{self.name}\n{settings_str}\nend"

    def _to_string(self, settings, level: int = 1) -> str:
        indent = " " * (self.indent * level)
        if isinstance(settings, tuple):
            return f"{indent}{','.join(str(v) for v in settings)}"
        elif isinstance(settings, list):
            lines = []
            for line in settings:
                lines.append(f"{indent}{line}")
            indent_less = " " * (self.indent * (level - 1))
            lines.append(f"{indent_less}end")
            return "\n".join(lines)
        elif not isinstance(settings, dict):
            value = str(settings)
            return "\n".join(f"{indent}{line}" for line in value.strip().splitlines())
        lines = []
        for key, value in settings.items():
            lines.append(f"{indent}{key}")
            lines.append(self._to_string(value, level + 1))
            if isinstance(value, dict):
                lines.append(f"{indent}end")
        return "\n".join(lines)