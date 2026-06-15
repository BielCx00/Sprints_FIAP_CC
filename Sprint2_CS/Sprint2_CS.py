# ============================================================
# Sprint 02 CS
#
# Lógica do sistema: R = A • C • !S • (!P + E)
# Lógica do Buzzer: B = !S + !P
#
# A = autenticado       — usuário fez login
# C = carro conectado   — veículo plugado no carregador
# S = sobrecarga        — ldr_val <= 300 (consumo crítico)
# P = pico de consumo   — 300 < ldr_val < 500
# E = energia solar     — placa solar disponível
#
#
# O pico (P) sozinho não bloqueia se a energia solar (E)
# estiver disponível, pois ela compensa o consumo elevado.
# A sobrecarga (S) bloqueia sempre, independente de E.
# ============================================================


def ler_switch(nome):
    # Repete até receber exatamente 0 ou 1
    while True:
        raw = input(f"  {nome} (0 = não / 1 = sim): ")
        if raw == "0" or raw == "1":
            return int(raw)
        print("  Entrada inválida! Digite apenas 0 ou 1.")


def buzzer(estado):
    # Simula tone()/noTone() do Arduino
    # 250Hz → pico sem solar (intermitente)
    # 500Hz → sobrecarga    (intermitente)
    # silêncio → normal ou bloqueado por A/C
    if estado == "pico":
        print("   BUZZER: 250Hz")
    elif estado == "sobrecarga":
        print("   BUZZER: 500Hz")
    else:
        print("   BUZZER: silêncio")


def processar_leitura(ldr_val, A, C, E):
    # Deriva S e P a partir do ldr_val
    # S e P são mutuamente exclusivos:
    #   ldr <= 300        → S = 1 (sobrecarga)
    #   300 < ldr < 500   → P = 1 (pico)
    #   ldr >= 500        → consumo normal
    S = ldr_val <= 300
    P = ldr_val > 300 and ldr_val < 500

    print("\n  --- ESTADO DAS ENTRADAS ---")
    print(f"  A  Autenticado:      {'SIM' if A else 'NÃO'}")
    print(f"  C  Carro conectado:  {'SIM' if C else 'NÃO'}")
    print(f"  E  Energia solar:    {'SIM' if E else 'NÃO'}")
    print(f"  S  Sobrecarga:       {'SIM' if S else 'NÃO'}  (LDR <= 300)")
    print(f"  P  Pico de consumo:  {'SIM' if P else 'NÃO'}  (300 > LDR < 500)")

    print("\n  --- SAÍDAS DO CIRCUITO ---")

    # Prioridade 1: sobrecarga — S bloqueia sempre (A•C•!S falha)
    if S:
        print("  CRÍTICO: Sobrecarga detectada! Recarga bloqueada.")
        print("  → LED Vermelho (Sobrecarga):  LIGADO")
        print("  → LED Amarelo  (Placa solar): DESLIGADO")
        print("  → LED Verde    (Carregando):  DESLIGADO")
        buzzer("sobrecarga")
        return {"recarga": False, "pico": False, "sobrecarga": True}

    # Prioridade 2: A ou C ausentes — sem autenticação ou carro
    # não importa o consumo, R = 0
    if not A or not C:
        print("  RECARGA BLOQUEADA.")
        if not A:
            print("  → Motivo: usuário não autenticado")
        if not C:
            print("  → Motivo: veículo não conectado")
        print("  → LED Verde    (Carregando):  DESLIGADO")
        print("  → LED Amarelo  (Placa solar): DESLIGADO")
        print("  → LED Vermelho (Sobrecarga):  DESLIGADO")
        buzzer("silencio")
        return {"recarga": False, "pico": False, "sobrecarga": False}

    # Prioridade 3: pico sem solar — (!P + E) = 0
    # P existe mas E não compensa → R = 0
    if P and not E:
        print("  ALERTA: Pico de consumo sem energia solar!")
        print("  → LED Amarelo  (Placa solar): DESLIGADO")
        print("  → LED Verde    (Carregando):  DESLIGADO")
        print("  → LED Vermelho (Sobrecarga):  DESLIGADO")
        buzzer("pico")
        return {"recarga": False, "pico": True, "sobrecarga": False}

    # Todas as condições satisfeitas — R = 1
    # Inclui: pico com solar (P=1, E=1 → !P+E = 1) e consumo normal
    if E:
        print("  RECARGA LIBERADA! (energia solar ativa)")
    else:
        print("  RECARGA LIBERADA!")
    print("  → LED Verde    (Carregando):  LIGADO")
    print("  → LED Amarelo  (Placa solar): " + ("LIGADO" if E else "DESLIGADO"))
    print("  → LED Vermelho (Sobrecarga):  DESLIGADO")
    buzzer("silencio")
    return {"recarga": True, "pico": False, "sobrecarga": False}

# LOOP PRINCIPAL — simula o void loop() do Arduino

historico = []
leitura_num = 0

print("=" * 55)
print("   SISTEMA DE MONITORAMENTO DE DEMANDA ENERGÉTICA")
print("   GoodWe — Estação de Recarga EV")
print("=" * 55)
print("  Digite 'sair' para encerrar.")
print("  ldr <= 300 → (sobrecarga)")
print("  300 < ldr < 500 → (pico)")
print("  ldr >= 500 → consumo normal")

while True:
    leitura_num += 1
    print(f"{'='*55}")
    print(f"  LEITURA #{leitura_num}")
    print(f"{'='*55}")

    # Lê o LDR e reutiliza em todos os ifs
    raw = input("  LDR — valor de consumo (0 a 1023) ou 'sair': ")
    if raw.strip().lower() == "sair":
        break

    if raw.isdigit():
        ldr_val = int(raw)
        if ldr_val > 1023:
            print("  Valor fora do intervalo! Usando 1023.")
            ldr_val = 1023
    else:
        print("  Entrada inválida. Usando 1023.")
        ldr_val = 1023

    # Entradas digitais — loop até valor válido
    A = ler_switch("Usuário autenticado      (A)")
    C = ler_switch("Carro conectado          (C)")
    E = ler_switch("Energia solar disponível (E)")

    resultado = processar_leitura(ldr_val, A, C, E)

    historico.append({
        "leitura": leitura_num,
        "ldr": ldr_val,
        "A": A, "C": C, "E": E,
        **resultado
    })

# RESUMO FINAL

print(f"\n{'='*55}")
print("  RESUMO DA SESSÃO")
print(f"{'='*55}")
print(f"  Total de leituras:   {len(historico)}")
print(f"  Recarga liberada:    {sum(1 for h in historico if h['recarga'])}")
print(f"  Pico sem solar:      {sum(1 for h in historico if h['pico'])}")
print(f"  Sobrecarga crítica:  {sum(1 for h in historico if h['sobrecarga'])}")
print(f"  Recarga bloqueada:   {sum(1 for h in historico if not h['recarga'])}")
print(f"{'='*55}")