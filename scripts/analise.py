import pandas as pd
import numpy as np

# ─── CARREGAR DADOS ───────────────────────────────────────────────
df_res = pd.read_csv('reservas.csv')
df_rev = pd.read_csv('reviews.csv')

# ─── 1. QUALIDADE DOS DADOS ───────────────────────────────────────
print("=" * 50)
print("📋 QUALIDADE DOS DADOS — RESERVAS")
print("=" * 50)
print(f"Linhas:   {df_res.shape[0]}")
print(f"Colunas:  {df_res.shape[1]}")
print(f"\nValores nulos:")
print(df_res.isnull().sum())
print(f"\nTipos de dados:")
print(df_res.dtypes)

print("\n" + "=" * 50)
print("📋 QUALIDADE DOS DADOS — REVIEWS")
print("=" * 50)
print(f"Linhas:   {df_rev.shape[0]}")
print(f"Colunas:  {df_rev.shape[1]}")
print(f"\nValores nulos:")
print(df_rev.isnull().sum())

# ─── 2. CORRIGIR TIPOS ────────────────────────────────────────────
df_res['checkin']  = pd.to_datetime(df_res['checkin'])
df_res['checkout'] = pd.to_datetime(df_res['checkout'])

# ─── 3. COLUNAS CALCULADAS ────────────────────────────────────────

# Separar reservas activas (não canceladas)
df_ativas = df_res[df_res['cancelada'] == 0].copy()

# RevPAR por mês (Revenue / Total quartos disponíveis no mês)
TOTAL_QUARTOS = 120

df_revpar = (
    df_ativas.groupby(['ano', 'mes'])['revenue_total']
    .sum()
    .reset_index()
)
df_revpar['dias_no_mes']       = df_revpar['mes'].map(
    {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
)
df_revpar['quartos_disponiveis'] = TOTAL_QUARTOS * df_revpar['dias_no_mes']
df_revpar['RevPAR']              = (
    df_revpar['revenue_total'] / df_revpar['quartos_disponiveis']
).round(2)

# ADR por mês (Revenue / Noites vendidas)
df_noites = (
    df_ativas.groupby(['ano', 'mes'])['noites']
    .sum()
    .reset_index()
    .rename(columns={'noites': 'noites_vendidas'})
)
df_revpar = df_revpar.merge(df_noites, on=['ano', 'mes'])
df_revpar['ADR'] = (
    df_revpar['revenue_total'] / df_revpar['noites_vendidas']
).round(2)

# Taxa de ocupação por mês
df_revpar['taxa_ocupacao'] = (
    df_revpar['noites_vendidas'] / df_revpar['quartos_disponiveis'] * 100
).round(1)

# ─── 4. ANÁLISE POR CANAL ─────────────────────────────────────────
df_canal = (
    df_ativas.groupby('canal')
    .agg(
        reservas        = ('reserva_id', 'count'),
        revenue         = ('revenue_total', 'sum'),
        comissoes       = ('comissao_valor', 'sum'),
        noites_médias   = ('noites', 'mean'),
    )
    .reset_index()
)
df_canal['revenue_liquido']  = (df_canal['revenue'] - df_canal['comissoes']).round(2)
df_canal['pct_reservas']     = (df_canal['reservas'] / df_canal['reservas'].sum() * 100).round(1)
df_canal['pct_revenue']      = (df_canal['revenue']  / df_canal['revenue'].sum()  * 100).round(1)
df_canal['comissao_media']   = (df_canal['comissoes'] / df_canal['reservas']).round(2)

# ─── 5. ANÁLISE DE REVIEWS ────────────────────────────────────────
df_rev_resumo = (
    df_rev.groupby('canal')
    .agg(
        total_reviews   = ('reserva_id', 'count'),
        score_medio     = ('score_geral', 'mean'),
        pct_positivo    = ('sentimento', lambda x: (x == 'Positivo').mean() * 100),
        pct_negativo    = ('sentimento', lambda x: (x == 'Negativo').mean() * 100),
    )
    .reset_index()
)
df_rev_resumo['score_medio']  = df_rev_resumo['score_medio'].round(2)
df_rev_resumo['pct_positivo'] = df_rev_resumo['pct_positivo'].round(1)
df_rev_resumo['pct_negativo'] = df_rev_resumo['pct_negativo'].round(1)

# ─── OUTPUTS ──────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("📊 KPIS MENSAIS (RevPAR / ADR / Ocupação)")
print("=" * 50)
print(df_revpar[['ano','mes','RevPAR','ADR','taxa_ocupacao','revenue_total']].to_string(index=False))

print("\n" + "=" * 50)
print("💰 ANÁLISE POR CANAL")
print("=" * 50)
print(df_canal[['canal','reservas','pct_reservas','revenue','comissoes',
                'revenue_liquido','pct_revenue']].to_string(index=False))

print("\n" + "=" * 50)
print("⭐ REVIEWS POR CANAL")
print("=" * 50)
print(df_rev_resumo.to_string(index=False))

# ─── EXPORTAR PARA POWER BI ───────────────────────────────────────
df_ativas.to_csv('fact_reservas.csv',       index=False)
df_revpar.to_csv('kpis_mensais.csv',        index=False)
df_canal.to_csv('analise_canal.csv',        index=False)
df_rev_resumo.to_csv('analise_reviews.csv', index=False)
df_rev.to_csv('fact_reviews.csv',           index=False)

print("\n✅ 5 ficheiros exportados para Power BI")