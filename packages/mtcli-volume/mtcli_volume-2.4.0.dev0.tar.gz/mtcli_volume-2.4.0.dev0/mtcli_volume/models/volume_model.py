from collections import defaultdict
from collections.abc import Mapping
from datetime import datetime

import MetaTrader5 as mt5
import numpy as np

from mtcli.logger import setup_logger
from mtcli.mt5_context import mt5_conexao
from mtcli_volume.conf import DIGITOS

log = setup_logger()


def obter_rates(
    symbol: str,
    period: str,
    bars: int,
    data_inicio: datetime = None,
    data_fim: datetime = None,
):
    """Obtém dados históricos via MetaTrader 5, podendo filtrar por intervalo de tempo."""
    with mt5_conexao():
        tf = getattr(mt5, f"TIMEFRAME_{period.upper()}", None)
        if tf is None:
            log.error(f"Timeframe inválido: {period}")
            return None

        if not mt5.symbol_select(symbol, True):
            log.error(f"Erro ao selecionar símbolo {symbol}")
            return None

        try:
            if data_inicio and data_fim:
                log.debug(
                    f"Obtendo candles de {symbol} entre {data_inicio} e {data_fim}"
                )
                rates = mt5.copy_rates_range(symbol, tf, data_inicio, data_fim)
            else:
                log.debug(f"Obtendo {bars} candles de {symbol} a partir da posição 0")
                rates = mt5.copy_rates_from_pos(symbol, tf, 0, bars)
        except Exception as e:
            log.error(f"Erro ao obter dados históricos: {e}")
            return None

        # ✅ Correção para arrays NumPy
        if rates is None or len(rates) == 0:
            log.error("Nenhum dado retornado.")
            return None

    return rates


def calcular_profile(
    rates: list[dict | tuple | object],
    step: float,
    volume: str = "tick",
) -> dict[float, float]:
    """Calcula o volume total por faixa de preço, suportando dicionários, numpy.void, objetos ou tuplas."""
    profile = defaultdict(int)

    for r in rates:
        # --- 1️⃣ Dict comum ---
        if isinstance(r, Mapping):
            preco = r["close"]
            tick_volume = r["tick_volume"]
            real_volume = r.get("real_volume", tick_volume)

        # --- 2️⃣ numpy.void (estrutura MT5) ---
        elif isinstance(r, np.void):
            preco = float(r["close"])
            tick_volume = int(r["tick_volume"])
            # real_volume pode não existir dependendo da corretora
            real_volume = (
                int(r["real_volume"]) if "real_volume" in r.dtype.names else tick_volume
            )

        # --- 3️⃣ Objeto com atributos (ex: namedtuple) ---
        elif hasattr(r, "close"):
            preco = r.close
            tick_volume = r.tick_volume
            real_volume = getattr(r, "real_volume", tick_volume)

        # --- 4️⃣ Tupla/lista ---
        elif isinstance(r, (tuple, list)) and len(r) >= 6:
            preco = r[4]
            tick_volume = r[5]
            real_volume = r[6] if len(r) > 6 else tick_volume

        else:
            raise TypeError(f"Formato de rate desconhecido: {type(r)}")

        faixa = round(round(preco / step) * step, DIGITOS)
        profile[faixa] += tick_volume if volume == "tick" else real_volume

    return dict(profile)


def calcular_estatisticas(profile):
    """Calcula POC, área de valor (70%), HVNs e LVNs."""
    if not profile:
        return {"poc": None, "area_valor": (None, None), "hvns": [], "lvns": []}

    # Ordena as faixas de preço por volume (desc)
    volumes_ordenados = sorted(profile.items(), key=lambda x: x[1], reverse=True)
    poc = volumes_ordenados[0][0]

    # Cálculo da área de valor (70%)
    total_volume = sum(profile.values())
    acumulado = 0
    faixas_area_valor = []
    for faixa, vol in volumes_ordenados:
        acumulado += vol
        faixas_area_valor.append(faixa)
        if acumulado >= total_volume * 0.7:
            break
    area_valor = (min(faixas_area_valor), max(faixas_area_valor))

    # HVNs e LVNs
    media = total_volume / len(profile)
    hvns = sorted([faixa for faixa, vol in profile.items() if vol >= media * 1.5])
    lvns = sorted([faixa for faixa, vol in profile.items() if vol <= media * 0.5])

    return {
        "poc": poc,
        "area_valor": area_valor,
        "hvns": hvns,
        "lvns": lvns,
    }
