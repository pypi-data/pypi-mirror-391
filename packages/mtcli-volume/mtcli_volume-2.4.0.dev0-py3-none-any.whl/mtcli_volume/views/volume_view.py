import click

from mtcli_volume.conf import DIGITOS

BARRA_CHAR = "#"


def exibir_volume_profile(profile, stats, symbol, info=None, verbose=False):
    """Exibe o volume profile no terminal de forma acessível e organizada."""
    if not profile:
        click.echo(f"Nenhum dado disponível para {symbol}")
        return

    # ──────────────────────────────────────────────
    # BLOCO VERBOSO: exibe detalhes da análise
    # ──────────────────────────────────────────────
    if verbose and info:
        click.echo("\n=== Informações da Análise ===")
        linhas = [
            ("Símbolo", info.get("symbol", "?")),
            ("Timeframe", info.get("period", "?").upper()),
            ("Candles analisados", str(info.get("candles", "?"))),
            (
                "Período analisado",
                f"{info.get('inicio', '?')} → {info.get('fim', '?')}",
            ),
            ("Fuso horário", info.get("timezone", "Desconhecido")),
        ]
        largura_esq = max(len(t[0]) for t in linhas) + 2
        for chave, valor in linhas:
            click.echo(f"{chave:<{largura_esq}}: {valor}")
        click.echo("=" * (largura_esq + 30))

    # ──────────────────────────────────────────────
    # BLOCO PRINCIPAL: Volume Profile
    # ──────────────────────────────────────────────
    dados_ordenados = sorted(profile.items(), reverse=True)
    click.echo(f"\nVolume Profile — {symbol}\n")

    max_vol = max(profile.values())
    largura_preco = max(len(f"{p:.{DIGITOS}f}") for p in profile.keys())

    # Cabeçalho
    click.echo(f"{'Preço':>{largura_preco}} | Volume 1000X | Distribuição")
    click.echo("-" * (largura_preco + 32))

    # Corpo da tabela
    for preco, vol in dados_ordenados:
        barra_len = int(vol / max_vol * 50)
        barra = BARRA_CHAR * barra_len
        click.echo(f"{preco:>{largura_preco}.{DIGITOS}f} | {vol/1000:>6.0f} | {barra}")

    # ──────────────────────────────────────────────
    # BLOCO FINAL: Estatísticas
    # ──────────────────────────────────────────────
    click.echo("\n=== Estatísticas ===")
    if stats.get("poc") is not None:
        click.echo(f"POC              {stats['poc']:.{DIGITOS}f}")
        click.echo(
            f"VA {stats['area_valor'][0]:.{DIGITOS}f} a {stats['area_valor'][1]:.{DIGITOS}f}"
        )
        click.echo(
            f"HVNs {', '.join(map(lambda x: f'{x:.{DIGITOS}f}', stats['hvns'])) or 'Nenhum'}"
        )
        click.echo(
            f"LVNs {', '.join(map(lambda x: f'{x:.{DIGITOS}f}', stats['lvns'])) or 'Nenhum'}"
        )
    else:
        click.echo("Estatísticas indisponíveis (dados insuficientes).")
