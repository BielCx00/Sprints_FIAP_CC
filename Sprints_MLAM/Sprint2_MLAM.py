"""
Global Solution - Análise de Energia Sustentável Global
Sprint 2 — Análises Gráficas, Univariadas e Relatório Técnico
Base de dados: Global Data on Sustainable Energy (Kaggle / Our World in Data)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# ==============================================================
# PASSO 1 — CARGA E SANEAMENTO
# ==============================================================

Dados = pd.read_csv('global-data-on-sustainable-energy (1).csv')

Dados = Dados.drop_duplicates()
Dados = Dados.dropna(subset=[
    'gdp_per_capita',
    'Electricity from nuclear (TWh)',
    'Value_co2_emissions_kt_by_country',
    'Renewable energy share in the total final energy consumption (%)',
    'Low-carbon electricity (% electricity)',
    'Year'
])

# Variáveis derivadas para os gráficos
Dados['Faixa_PIB'] = np.where(
    Dados['gdp_per_capita'] > 30000, 'PIB Alto',
    np.where(Dados['gdp_per_capita'] > 10000, 'PIB Médio', 'PIB Baixo')
)

Dados['Nivel_Carbono_Zero'] = np.where(
    Dados['Low-carbon electricity (% electricity)'] > 50, 'Maioria Limpa',
    np.where(Dados['Low-carbon electricity (% electricity)'] > 20, 'Transição', 'Maioria Fóssil')
)

print("=" * 60)
print("BASE DE DADOS — SPRINT 2")
print(f"Total de registros após saneamento: {len(Dados)}")
print("=" * 60 + "\n")

# ==============================================================
# PASSO 2 — TABELAS DE DISTRIBUIÇÃO DE FREQUÊNCIAS
# (variáveis diferentes das usadas na Sprint 1)
# ==============================================================

print("=" * 60)
print("02) a) TABELA DE DISTRIBUIÇÃO DE FREQUÊNCIAS")
print("       VARIÁVEL DISCRETA: Electricity from nuclear (TWh)")
print("=" * 60)

# Agrupando em faixas discretas para tornar a tabela legível
Dados['Nuclear_Faixa'] = pd.cut(
    Dados['Electricity from nuclear (TWh)'],
    bins=[-1, 0, 50, 200, 500, 9999],
    labels=['Zero', '1–50 TWh', '51–200 TWh', '201–500 TWh', '>500 TWh']
)

fi_d  = pd.Series(Counter(Dados['Nuclear_Faixa'])).reindex(['Zero','1–50 TWh','51–200 TWh','201–500 TWh','>500 TWh'])
fia_d = fi_d.cumsum()
fr_d  = (fi_d / fi_d.sum()) * 100
fra_d = fr_d.cumsum()

tabela_discreta = pd.DataFrame({
    'fi':      fi_d,
    'fia':     fia_d,
    'fr (%)':  fr_d.round(2),
    'fra (%)': fra_d.round(2)
})
print(tabela_discreta)

# Insight 1: A esmagadora maioria dos países (faixa "Zero") não possui geração nuclear,
# revelando que essa fonte energética é exclusividade de nações com alta capacidade
# tecnológica e investimento — padrão que reforça a desigualdade energética global.

# Insight 2: Países com geração acima de 500 TWh representam menos de 1% dos registros,
# confirmando que a energia nuclear está concentrada em poucos grandes produtores
# (EUA, França, China), o que torna a diversificação da matriz global ainda mais urgente.

print("\n" + "-" * 60 + "\n")

print("=" * 60)
print("02) b) TABELA DE DISTRIBUIÇÃO DE FREQUÊNCIAS")
print("       VARIÁVEL CONTÍNUA: gdp_per_capita (PIB per Capita em US$)")
print("=" * 60)

bins_cont = 5
classes_c = pd.cut(Dados['gdp_per_capita'], bins=bins_cont, right=False)

fi_c  = classes_c.value_counts().sort_index()
fia_c = fi_c.cumsum()
fr_c  = (fi_c / fi_c.sum()) * 100
fra_c = fr_c.cumsum()

tabela_continua = pd.DataFrame({
    'fi':      fi_c,
    'fia':     fia_c,
    'fr (%)':  fr_c.round(2),
    'fra (%)': fra_c.round(2)
})
print(tabela_continua)

# Insight 1: Mais de 75% dos registros concentram-se na faixa de menor PIB per capita,
# evidenciando que a maior parte dos países analisados é economicamente vulnerável
# — o que limita diretamente a capacidade de investimento em infraestrutura renovável.

# Insight 2: A frequência relativa acumulada (fra) mostra que apenas ~5% dos registros
# pertencem às faixas de renda mais alta, confirmando forte assimetria positiva na
# distribuição de renda global e indicando que políticas redistributivas são essenciais
# para viabilizar a transição energética nos países mais pobres.

print("\n" + "-" * 60 + "\n")

# ==============================================================
# PASSO 3 — ANÁLISES GRÁFICAS
# (variáveis diferentes das usadas na Sprint 1)
# ==============================================================

# --- Gráfico 1: Setores — Proporção de países por Nível de Eletricidade Limpa ---
freq_carbono = Dados['Nivel_Carbono_Zero'].value_counts()
cores_pizza  = ['#27ae60', '#f39c12', '#c0392b']
labels_pizza = freq_carbono.index.tolist()

fig, ax = plt.subplots(figsize=(9, 6))
wedges, texts, autotexts = ax.pie(
    freq_carbono.values,
    labels=None,
    autopct='%1.2f%%',
    colors=cores_pizza,
    startangle=90,
    pctdistance=0.75,
    textprops={'fontsize': 12}
)
for at in autotexts:
    at.set_fontweight('bold')
    at.set_color('white')

ax.set_title(
    'Distribuição de Registros por Nível de Eletricidade de Baixo Carbono',
    fontsize=13, fontweight='bold', pad=18
)
ax.legend(
    wedges, labels_pizza,
    title='Categoria (Maioria Limpa >50% | Transição 20-50% | Maioria Fóssil <20%)',
    loc='center left',
    bbox_to_anchor=(1.0, 0.5),
    fontsize=10,
    title_fontsize=9
)
plt.tight_layout()
plt.savefig('grafico_1_setores_carbono.png', dpi=150, bbox_inches='tight')
plt.show()

# --- Gráfico 2: Barras — Emissões médias de CO₂ por Faixa de PIB ---
media_co2 = Dados.groupby('Faixa_PIB')['Value_co2_emissions_kt_by_country'].mean()
ordem = ['PIB Baixo', 'PIB Médio', 'PIB Alto']
media_co2 = media_co2.reindex(ordem)

plt.figure(figsize=(8, 5))
bars = plt.bar(
    media_co2.index,
    media_co2.values,
    color=['#3498db', '#e67e22', '#e74c3c'],
    edgecolor='black',
    width=0.5
)
plt.title('Emissões Médias de CO₂ por Faixa de PIB per Capita', fontsize=14, fontweight='bold')
plt.xlabel('Faixa de PIB per Capita (US$)', fontsize=12)
plt.ylabel('Emissões Médias de CO₂ (kt)', fontsize=12)
plt.legend(bars, media_co2.index, title='Faixa de PIB', fontsize=11)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('grafico_2_barras_co2_pib.png', dpi=150)
plt.show()

# --- Gráfico 3: Histograma — Distribuição da Participação de Renováveis na Energia ---
plt.figure(figsize=(9, 5))
plt.hist(
    Dados['Renewable energy share in the total final energy consumption (%)'],
    bins=15,
    color='#2ecc71',
    edgecolor='black',
    alpha=0.85
)
plt.title('Distribuição da Participação de Renováveis na Matriz Energética', fontsize=14, fontweight='bold')
plt.xlabel('Participação de Renováveis no Consumo Final de Energia (%)', fontsize=12)
plt.ylabel('Frequência Absoluta (fi)', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('grafico_3_histograma_renovaveis.png', dpi=150)
plt.show()

# --- Gráfico 4: Boxplot — PIB per Capita por Nível de Eletricidade Limpa ---
grupos_box = [
    Dados.loc[Dados['Nivel_Carbono_Zero'] == n, 'gdp_per_capita'].values
    for n in ['Maioria Limpa', 'Transição', 'Maioria Fóssil']
]

fig, ax = plt.subplots(figsize=(9, 6))
bp = ax.boxplot(
    grupos_box,
    patch_artist=True,
    tick_labels=['Maioria Limpa', 'Transição', 'Maioria Fóssil']
)
cores_box = ['#27ae60', '#f39c12', '#c0392b']
for patch, cor in zip(bp['boxes'], cores_box):
    patch.set_facecolor(cor)

ax.set_title('Boxplot — PIB per Capita por Nível de Eletricidade Limpa', fontsize=14, fontweight='bold')
ax.set_xlabel('Nível de Eletricidade de Baixo Carbono', fontsize=12)
ax.set_ylabel('PIB per Capita (US$)', fontsize=12)
ax.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('grafico_4_boxplot_pib_carbono.png', dpi=150)
plt.show()

# ==============================================================
# PASSO 4 — ANÁLISE UNIVARIADA
# (variáveis diferentes das usadas na Sprint 1)
# ==============================================================

# ANÁLISE 1 — VARIÁVEL CONTÍNUA: gdp_per_capita

print("=" * 60)
print("04) ANÁLISE UNIVARIADA 1 — VARIÁVEL CONTÍNUA")
print("    gdp_per_capita (PIB per Capita em US$)")
print("=" * 60)

col1 = Dados['gdp_per_capita']

print("\n--- Medidas de Tendência Central ---")
print(f"Média:   {col1.mean():.2f} US$")
print(f"Mediana: {col1.median():.2f} US$")
moda1 = col1.mode()
print(f"Moda:    {moda1[0]:.2f} US$" if not moda1.empty else "Moda:    Sem moda")

print("\n--- Medidas de Dispersão ---")
print(f"Máximo:                      {col1.max():.2f} US$")
print(f"Mínimo:                      {col1.min():.2f} US$")
print(f"Amplitude:                   {col1.max() - col1.min():.2f} US$")
print(f"Variância:                   {col1.var():.2f}")
print(f"Desvio Padrão:               {col1.std():.2f}")
print(f"Coeficiente de Variação (%): {(col1.std() / col1.mean()) * 100:.2f}%")

print("\n--- Medidas Separatrizes (Quartis) ---")
q1 = col1.quantile([0.25, 0.50, 0.75])
print(f"Q1 (25%): {q1[0.25]:.2f} US$")
print(f"Q2 (50%): {q1[0.50]:.2f} US$")
print(f"Q3 (75%): {q1[0.75]:.2f} US$")
print(f"IIQ:      {q1[0.75] - q1[0.25]:.2f} US$")
print("\n" + "-" * 60 + "\n")

# ANÁLISE 2 — VARIÁVEL CONTÍNUA: Value_co2_emissions_kt_by_country

print("=" * 60)
print("04) ANÁLISE UNIVARIADA 2 — VARIÁVEL CONTÍNUA")
print("    Value_co2_emissions_kt_by_country (Emissões de CO₂ em kt)")
print("=" * 60)

col2 = Dados['Value_co2_emissions_kt_by_country']

print("\n--- Medidas de Tendência Central ---")
print(f"Média:   {col2.mean():.2f} kt")
print(f"Mediana: {col2.median():.2f} kt")
moda2 = col2.mode()
print(f"Moda:    {moda2[0]:.2f} kt" if not moda2.empty else "Moda:    Sem moda")

print("\n--- Medidas de Dispersão ---")
print(f"Máximo:                      {col2.max():.2f} kt")
print(f"Mínimo:                      {col2.min():.2f} kt")
print(f"Amplitude:                   {col2.max() - col2.min():.2f} kt")
print(f"Variância:                   {col2.var():.2f}")
print(f"Desvio Padrão:               {col2.std():.2f}")
print(f"Coeficiente de Variação (%): {(col2.std() / col2.mean()) * 100:.2f}%")

print("\n--- Medidas Separatrizes (Quartis) ---")
q2 = col2.quantile([0.25, 0.50, 0.75])
print(f"Q1 (25%): {q2[0.25]:.2f} kt")
print(f"Q2 (50%): {q2[0.50]:.2f} kt")
print(f"Q3 (75%): {q2[0.75]:.2f} kt")
print(f"IIQ:      {q2[0.75] - q2[0.25]:.2f} kt")
print("\n" + "=" * 60 + "\n")

print("✅ Sprint 2 concluída. Gráficos salvos como .png na pasta atual.")