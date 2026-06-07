import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('pt_PT')
np.random.seed(42)
random.seed(42)

# ─── CONFIGURAÇÃO DO HOTEL ───────────────────────────────────────
TOTAL_QUARTOS = 120
ANOS = [2023, 2024]
CANAIS = {
    'Booking.com': {'peso': 0.38, 'comissao': 0.15},
    'Expedia':     {'peso': 0.18, 'comissao': 0.18},
    'Airbnb':      {'peso': 0.12, 'comissao': 0.03},
    'Direto':      {'peso': 0.22, 'comissao': 0.00},
    'Telefone':    {'peso': 0.10, 'comissao': 0.00},
}
TIPOS_QUARTO = {
    'Standard':    {'preco_base': 85,  'quartos': 60},
    'Superior':    {'preco_base': 120, 'quartos': 35},
    'Suite':       {'preco_base': 180, 'quartos': 25},
}
NACIONALIDADES = ['Portuguesa', 'Espanhola', 'Francesa', 'Alemã',
                  'Britânica', 'Americana', 'Brasileira', 'Italiana']

# ─── SAZONALIDADE (multiplicador de preço por mês) ────────────────
SAZONALIDADE = {
    1: 0.65, 2: 0.70, 3: 0.80, 4: 0.90,
    5: 1.00, 6: 1.15, 7: 1.35, 8: 1.40,
    9: 1.20, 10: 1.00, 11: 0.75, 12: 0.85
}

# ─── GERAR RESERVAS ───────────────────────────────────────────────
reservas = []
reserva_id = 1000

for ano in ANOS:
    for mes in range(1, 13):
        fator = SAZONALIDADE[mes]
        num_reservas = int(TOTAL_QUARTOS * fator * random.uniform(0.55, 0.75))

        for _ in range(num_reservas):
            canal = random.choices(
                list(CANAIS.keys()),
                weights=[v['peso'] for v in CANAIS.values()]
            )[0]
            tipo = random.choices(
                list(TIPOS_QUARTO.keys()),
                weights=[v['quartos'] for v in TIPOS_QUARTO.values()]
            )[0]

            preco_base  = TIPOS_QUARTO[tipo]['preco_base']
            preco_final = round(preco_base * fator * random.uniform(0.9, 1.1), 2)
            comissao_pct = CANAIS[canal]['comissao']
            noites       = random.choices([1,2,3,4,5,6,7], weights=[20,30,25,12,7,4,2])[0]
            revenue      = round(preco_final * noites, 2)
            comissao_val = round(revenue * comissao_pct, 2)

            dia     = random.randint(1, 28)
            checkin = datetime(ano, mes, dia)
            checkout = checkin + timedelta(days=noites)

            reservas.append({
                'reserva_id':       reserva_id,
                'checkin':          checkin.strftime('%Y-%m-%d'),
                'checkout':         checkout.strftime('%Y-%m-%d'),
                'noites':           noites,
                'ano':              ano,
                'mes':              mes,
                'canal':            canal,
                'tipo_quarto':      tipo,
                'preco_noite':      preco_final,
                'revenue_total':    revenue,
                'comissao_pct':     comissao_pct,
                'comissao_valor':   comissao_val,
                'nacionalidade':    random.choice(NACIONALIDADES),
                'num_hospedes':     random.choices([1,2,3,4], weights=[20,50,20,10])[0],
                'cancelada':        random.choices([0,1], weights=[88,12])[0],
            })
            reserva_id += 1

df_reservas = pd.DataFrame(reservas)

# ─── GERAR REVIEWS ────────────────────────────────────────────────
reviews = []
df_nao_canceladas = df_reservas[df_reservas['cancelada'] == 0]

for _, row in df_nao_canceladas.iterrows():
    if random.random() < 0.60:  # 60% dos hóspedes deixam review
        score_base = {
            'Direto':      random.gauss(8.8, 0.6),
            'Telefone':    random.gauss(8.6, 0.7),
            'Booking.com': random.gauss(8.2, 1.0),
            'Expedia':     random.gauss(8.0, 1.1),
            'Airbnb':      random.gauss(8.4, 0.9),
        }[row['canal']]

        score = round(min(10, max(5, score_base)), 1)

        categorias = ['Limpeza', 'Localização', 'Atendimento',
                      'Pequeno-almoço', 'Conforto', 'Custo-benefício']
        scores_cat = {c: round(min(10, max(4, random.gauss(score, 0.8))), 1)
                      for c in categorias}

        reviews.append({
            'reserva_id':      row['reserva_id'],
            'canal':           row['canal'],
            'score_geral':     score,
            'sentimento':      'Positivo' if score >= 8 else ('Neutro' if score >= 6.5 else 'Negativo'),
            'ano':             row['ano'],
            'mes':             row['mes'],
            **scores_cat
        })

df_reviews = pd.DataFrame(reviews)

# ─── EXPORTAR ─────────────────────────────────────────────────────
df_reservas.to_csv('reservas.csv', index=False)
df_reviews.to_csv('reviews.csv',   index=False)

# ─── RESUMO ───────────────────────────────────────────────────────
print("=" * 50)
print("✅ DATASET GERADO COM SUCESSO")
print("=" * 50)
print(f"Total de reservas:  {len(df_reservas)}")
print(f"Total de reviews:   {len(df_reviews)}")
print(f"\nReservas por canal:")
print(df_reservas['canal'].value_counts())
print(f"\nRevenue total gerado: €{df_reservas['revenue_total'].sum():,.2f}")
print(f"Comissões pagas OTA:  €{df_reservas['comissao_valor'].sum():,.2f}")
print("=" * 50)