"""Разбор S-выражений протокола сервера (see, hear, init и т.д.)."""
import re


class ProtocolDecoder:
    """Парсер строковых сообщений в виде списков/атомов."""

    @staticmethod
    def tokenize_msg(raw: str) -> list:
        """Разбить строку на лексемы: скобки, числа, строки в кавычках, слова."""
        raw = raw.rstrip("\x00")
        regex = r'\(|\)|[-+]?\d+\.?\d*(?:e[-+]?\d+)?|"[^"]*"|[\w]+'
        return re.findall(regex, raw, re.IGNORECASE)

    @staticmethod
    def parse_tokens(tokens: list, idx: int = 0):
        """Рекурсивный разбор списка лексем. Возвращает (результат, новый_idx)."""
        result = []
        while idx < len(tokens):
            tok = tokens[idx]
            if tok == "(":
                sub, idx = ProtocolDecoder.parse_tokens(tokens, idx + 1)
                result.append(sub)
            elif tok == ")":
                return result, idx + 1
            else:
                s = tok.strip('"')
                try:
                    val = float(s) if "." in s or "e" in s.lower() else int(s)
                except ValueError:
                    val = s
                result.append(val)
                idx += 1
        return result, idx

    @staticmethod
    def from_string(raw: str) -> list | None:
        """Распарсить одно сообщение; вернуть корневой список или None."""
        tokens = ProtocolDecoder.tokenize_msg(raw)
        if not tokens:
            return None
        parsed, _ = ProtocolDecoder.parse_tokens(tokens)
        return parsed[0] if parsed else None
