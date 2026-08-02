import pandas as pd, sys
sys.path.insert(0, '.')
from logic import procesar_conciliacion

banco_raw = pd.read_excel('nuevo extracto.xlsx', header=None)
df_b = banco_raw.iloc[4:].copy()
df_b.columns = df_b.iloc[0]
df_b = df_b[1:].dropna(how='all')
df_b.columns = [str(c) if pd.notna(c) else f'Unnamed_{i}' for i,c in enumerate(df_b.columns)]

conta_raw = pd.read_excel('nuevo registro.xlsx', header=None)
df_c = conta_raw.iloc[9:].copy()
df_c.columns = df_c.iloc[0]
df_c = df_c[1:].dropna(how='all')
df_c.columns = [str(c) if pd.notna(c) else f'Unnamed_{i}' for i,c in enumerate(df_c.columns)]

col_f_c = '   Fecha  '
if df_c[col_f_c].dtype == object:
    df_c[col_f_c] = pd.to_datetime(df_c[col_f_c].astype(str).str.strip(), dayfirst=True, errors='coerce')

df_b['_Monto_Temp'] = (
    pd.to_numeric(df_b['Debito en $'].astype(str).str.replace(',', '.'), errors='coerce').abs().fillna(0) -
    pd.to_numeric(df_b['Credito en $'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
)
df_c['_Monto_Temp'] = (
    pd.to_numeric(df_c['     Creditos     '].astype(str).str.replace(',', '.'), errors='coerce').fillna(0) -
    pd.to_numeric(df_c['      Debitos     '].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
)

altas, bajas, solo_b, solo_c, banco_res, conta_res = procesar_conciliacion(
    df_b, df_c,
    'Fecha contable', '_Monto_Temp', 'Concepto',
    '   Fecha  ', '_Monto_Temp', '         Concepto pase        ',
    tolerancia_dias=4
)

print(f'Altas (Verde): {len(altas)}')
print(f'Bajas (Azul):  {len(bajas)}')
print(f'Solo banco (Rojo): {len(solo_b)}')
print(f'Solo contable (Rojo): {len(solo_c)}')

print('\n=== ALTAS ===')
for _, row in altas.iterrows():
    concepto = str(row.get('Concepto_banco', ''))
    monto = row.get('_Monto_Temp_banco', '')
    sim = row.get('Similitud_Detalle_%', 0)
    print(f"  {concepto:<40} monto={monto:>14}  sim={sim:.1f}%")

print('\n=== BAJAS ===')
for _, row in bajas.iterrows():
    concepto = str(row.get('Concepto_banco', ''))
    monto = row.get('_Monto_Temp_banco', '')
    sim = row.get('Similitud_Detalle_%', 0)
    print(f"  {concepto:<40} monto={monto:>14}  sim={sim:.1f}%")

print('\n=== SOLO BANCO (sin cruzar) ===')
print(solo_b[['Fecha contable', 'Concepto', '_Monto_Temp']].to_string())

print('\n=== SOLO CONTABLE (sin cruzar) ===')
col_fecha_c = '   Fecha  '
col_conc_c = '         Concepto pase        '
print(solo_c[[col_fecha_c, col_conc_c, '_Monto_Temp']].to_string())
