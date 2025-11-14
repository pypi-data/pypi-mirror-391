from datetime import datetime

import click

from mtcli_volume.conf import (
    FROM,
    PERIOD,
    PERIODOS,
    RANGE,
    SYMBOL,
    TIMEZONE,
    TO,
    VOLUME,
)
from mtcli_volume.controllers.volume_controller import calcular_volume_profile
from mtcli_volume.views.volume_view import exibir_volume_profile


@click.command(
    help="Exibe o Volume Profile, agrupando volumes por faixa de preço no histórico recente."
)
@click.version_option(package_name="mtcli-volume")
@click.option(
    "--symbol", "-s", default=SYMBOL, show_default=True, help="Símbolo do ativo."
)
@click.option(
    "--period",
    "-p",
    default=PERIOD,
    show_default=True,
    help="Período do volume.",
)
@click.option(
    "--periodos",
    "-po",
    "bars",
    default=PERIODOS,
    show_default=True,
    help="Quantidade de períodos.",
)
@click.option(
    "--range",
    "-r",
    "step",
    type=float,
    default=RANGE,
    show_default=True,
    help="Tamanho do agrupamento de preços.",
)
@click.option(
    "--volume",
    "-v",
    default=VOLUME,
    show_default=True,
    help="Tipo de volume (tick ou real).",
)
@click.option(
    "--from",
    "data_inicio",
    type=str,
    default=FROM,
    show_default=True,
    help="Data/hora inicial (YYYY-MM-DD HH:MM).",
)
@click.option(
    "--to",
    "data_fim",
    type=str,
    default=TO,
    show_default=True,
    help="Data/hora final (YYYY-MM-DD HH:MM).",
)
@click.option(
    "--verbose",
    "-vv",
    is_flag=True,
    help="Mostra informações detalhadas sobre a análise.",
)
@click.option(
    "--timezone",
    "-tz",
    type=str,
    default=TIMEZONE,
    show_default=True,
    help="Fuso horário para exibição das datas (ex: 'UTC', 'America/Sao_Paulo').",
)
def volume(
    symbol, period, bars, step, volume, data_inicio, data_fim, verbose, timezone
):
    """Exibe o Volume Profile agrupando volumes por faixa de preço."""
    inicio = datetime.strptime(data_inicio, "%Y-%m-%d %H:%M") if data_inicio else None
    fim = datetime.strptime(data_fim, "%Y-%m-%d %H:%M") if data_fim else None

    profile, stats, info = calcular_volume_profile(
        symbol, period, bars, step, volume, inicio, fim, verbose, timezone
    )
    exibir_volume_profile(profile, stats, symbol, info, verbose)
