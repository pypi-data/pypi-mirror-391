from datetime import datetime, timedelta, timezone
import zoneinfo  # Python 3.9+

import numpy as np

from mtcli.logger import setup_logger
from mtcli_volume.models.volume_model import (
    calcular_estatisticas,
    calcular_profile,
    obter_rates,
)

log = setup_logger()


def calcular_volume_profile(
    symbol,
    period,
    bars,
    step,
    volume,
    data_inicio=None,
    data_fim=None,
    verbose=False,
    timezone_str="America/Sao_Paulo",
):
    """Controla o fluxo de cálculo do volume profile, com suporte a timezone configurável."""
    volume = volume.lower().strip()
    if volume not in ["tick", "real"]:
        log.error(f"Tipo de volume inválido: {volume}. Use 'tick' ou 'real'.")
        raise ValueError(f"Tipo de volume inválido: {volume}. Use 'tick' ou 'real'.")

    rates = obter_rates(symbol, period, bars, data_inicio, data_fim)

    if rates is None or len(rates) == 0:
        log.error("Falha ao obter dados de preços para cálculo do volume profile.")
        return {}, {}, {}

    profile = calcular_profile(rates, step, volume)
    stats = calcular_estatisticas(profile)

    # Captura de informações de contexto
    info = {}
    if isinstance(rates, np.ndarray) and len(rates) > 0:
        primeiro = rates[0]
        ultimo = rates[-1]
        if "time" in rates.dtype.names:
            try:
                # Define fuso horário desejado
                try:
                    fuso = zoneinfo.ZoneInfo(timezone_str)
                except Exception:
                    log.warning(
                        f"Fuso horário '{timezone_str}' inválido. Usando UTC−3 (Brasília)."
                    )
                    fuso = timezone(timedelta(hours=-3))

                inicio_real = (
                    datetime.utcfromtimestamp(float(primeiro["time"]))
                    .astimezone(fuso)
                    .strftime("%Y-%m-%d %H:%M:%S")
                )
                fim_real = (
                    datetime.utcfromtimestamp(float(ultimo["time"]))
                    .astimezone(fuso)
                    .strftime("%Y-%m-%d %H:%M:%S")
                )
            except Exception as e:
                log.error(f"Erro ao converter timezone: {e}")
                inicio_real = fim_real = "?"
        else:
            inicio_real = fim_real = "?"

        info = {
            "symbol": symbol,
            "period": period,
            "candles": len(rates),
            "inicio": inicio_real,
            "fim": fim_real,
            "timezone": timezone_str,
        }

    return profile, stats, info
