"""Funções de data/hora. Tudo é guardado em UTC, sem fuso, e enviado ao front com 'Z'."""
from datetime import datetime, timezone


def agora_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def para_iso_utc(valor: datetime) -> str:
    """Datas sem fuso são tratadas como UTC; a saída termina em 'Z' para o navegador converter certo."""
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
