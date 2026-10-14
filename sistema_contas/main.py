"""Demonstração: instâncias, polimorfismo, ordenação via __lt__ e tratamento de exceções."""

from models import Cliente, ContaCorrente, ContaPoupanca, ContaInvestimento

clientes = [
    Cliente("Ana Beatriz", "ana.beatriz@email.com", "111.111.111-11"),
    Cliente("Bruno Costa", "bruno.costa@email.com", "222.222.222-22"),
    Cliente("Carla Dias", "carla.dias@email.com", "333.333.333-33"),
    Cliente("Diego Souza", "diego.souza@email.com", "444.444.444-44"),
]

contas = [
    ContaCorrente(clientes[0], saldo_inicial=1500.0, limite=800.0),
    ContaCorrente(clientes[1], saldo_inicial=200.0, limite=300.0),
    ContaCorrente(clientes[2], saldo_inicial=0.0, limite=500.0),
    ContaPoupanca(clientes[0], saldo_inicial=5000.0, taxa_rendimento=0.006),
    ContaPoupanca(clientes[1], saldo_inicial=1200.0),
    ContaPoupanca(clientes[3], saldo_inicial=300.0, taxa_rendimento=0.004),
    ContaInvestimento(clientes[2], saldo_inicial=10000.0, perfil_risco="arrojado"),
    ContaInvestimento(clientes[3], saldo_inicial=2500.0, perfil_risco="conservador"),
    ContaInvestimento(clientes[0], saldo_inicial=4000.0, perfil_risco="moderado"),
    ContaPoupanca(clientes[2], saldo_inicial=50.0),
]

print(f"{len(contas)} contas criadas para {len(clientes)} clientes.\n")

# --- Polimorfismo: mesma chamada, comportamento por subclasse ---------------
print("=== Fechamento mensal (aplicar_rendimento) ===")
for conta in contas:
    rendimento = conta.aplicar_rendimento()
    sinal = "+" if rendimento >= 0 else ""
    print(f"{conta}  →  {sinal}R$ {rendimento:.2f}")

# --- __lt__ / __eq__: ordenar contas por saldo -------------------------------
print("\n=== Contas ordenadas por saldo (menor → maior) ===")
for conta in sorted(contas):
    print(conta)

print(f"\nDuas contas de mesmo número são iguais? {contas[0] == contas[0]}")
print(f"Conta nova (número diferente) é igual à primeira? {contas[0] == contas[1]}")

# --- Tratamento de exceções ---------------------------------------------------
print("\n=== Validações e exceções ===")

tentativas = [
    ("saque maior que saldo + limite", lambda: contas[2].sacar(10_000)),
    ("depósito negativo", lambda: contas[0].depositar(-50)),
    ("e-mail inválido no cliente", lambda: Cliente("Teste", "nao-e-email", "555.555.555-55")),
    ("perfil de risco inexistente", lambda: ContaInvestimento(clientes[0], perfil_risco="agressivo-demais")),
    ("saldo negativo direto na @property", lambda: setattr(contas[3], "saldo", -100)),
]

for descricao, acao in tentativas:
    try:
        acao()
        print(f"[inesperado] '{descricao}' não levantou exceção")
    except (ValueError, TypeError) as erro:
        print(f"[ok] {descricao}: {erro}")
