"""Sistema de contas bancárias — modelagem orientada a objetos."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    """Titular de uma ou mais contas. Relação de composição: Conta *tem um* Cliente."""

    _EMAIL_REGEX = re.compile(r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$")

    def __init__(self, nome: str, email: str, cpf: str):
        self.nome = nome
        self.email = email
        self.cpf = cpf

    @property
    def nome(self) -> str:
        return self._nome

    @nome.setter
    def nome(self, valor: str):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("nome não pode ser vazio")
        self._nome = valor.strip()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str):
        if not self._EMAIL_REGEX.match(valor or ""):
            raise ValueError(f"e-mail inválido: {valor!r}")
        self._email = valor

    @property
    def cpf(self) -> str:
        return self._cpf

    @cpf.setter
    def cpf(self, valor: str):
        digitos = re.sub(r"\D", "", valor or "")
        if len(digitos) != 11:
            raise ValueError(f"CPF inválido: {valor!r}")
        self._cpf = digitos

    def __str__(self) -> str:
        return f"{self.nome} ({self.email})"

    def __repr__(self) -> str:
        return f"Cliente(nome={self.nome!r}, email={self.email!r}, cpf={self.cpf!r})"

    def __eq__(self, other):
        return isinstance(other, Cliente) and self.cpf == other.cpf


class Conta(ABC):
    """Classe abstrata: contrato comum a todo tipo de conta."""

    _proximo_numero = 1000

    def __init__(self, titular: Cliente, saldo_inicial: float = 0.0):
        self.titular = titular
        self._numero = Conta._proximo_numero
        Conta._proximo_numero += 1
        self._saldo = 0.0
        self.saldo = saldo_inicial  # passa pelo setter, valida >= 0
        self.criada_em = datetime.now()

    @property
    def numero(self) -> int:
        return self._numero

    @property
    def saldo(self) -> float:
        return self._saldo

    @saldo.setter
    def saldo(self, valor: float):
        if not isinstance(valor, (int, float)):
            raise TypeError("saldo deve ser numérico")
        if valor < 0:
            raise ValueError("saldo não pode ficar negativo")
        self._saldo = float(valor)

    def depositar(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("valor de depósito deve ser positivo")
        self.saldo = self.saldo + valor

    def sacar(self, valor: float) -> None:
        """Implementação padrão; ContaCorrente sobrescreve para permitir cheque especial."""
        if valor <= 0:
            raise ValueError("valor de saque deve ser positivo")
        if valor > self.saldo:
            raise ValueError(f"saldo insuficiente (saldo atual: R$ {self.saldo:.2f})")
        self.saldo = self.saldo - valor

    @abstractmethod
    def aplicar_rendimento(self) -> float:
        """Cada subtipo de conta rende (ou cobra) de um jeito — ponto de polimorfismo."""
        raise NotImplementedError

    def __str__(self) -> str:
        return f"{self.__class__.__name__} #{self.numero} — {self.titular.nome} — saldo: R$ {self.saldo:.2f}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(numero={self.numero}, titular={self.titular!r}, saldo={self.saldo!r})"

    def __eq__(self, other):
        return isinstance(other, Conta) and self.numero == other.numero

    def __lt__(self, other):
        if not isinstance(other, Conta):
            return NotImplemented
        return self.saldo < other.saldo


class ContaCorrente(Conta):
    """Conta sem rendimento, mas com limite de cheque especial."""

    def __init__(self, titular: Cliente, saldo_inicial: float = 0.0, limite: float = 500.0):
        super().__init__(titular, saldo_inicial)
        self.limite = limite

    @property
    def limite(self) -> float:
        return self._limite

    @limite.setter
    def limite(self, valor: float):
        if valor < 0:
            raise ValueError("limite não pode ser negativo")
        self._limite = float(valor)

    def sacar(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("valor de saque deve ser positivo")
        if valor > self.saldo + self.limite:
            raise ValueError("saque excede saldo + limite de cheque especial")
        self._saldo -= valor  # pode ficar negativo até -limite; não passa pelo setter

    def aplicar_rendimento(self) -> float:
        # conta corrente não rende; cobra manutenção se o saldo ficar negativo
        if self.saldo < 0:
            taxa = round(abs(self.saldo) * 0.01, 2)
            self._saldo -= taxa
            return -taxa
        return 0.0

    def __str__(self) -> str:
        return super().__str__() + f" — limite: R$ {self.limite:.2f}"


class ContaPoupanca(Conta):
    """Conta com rendimento mensal simples sobre o saldo."""

    def __init__(self, titular: Cliente, saldo_inicial: float = 0.0, taxa_rendimento: float = 0.005):
        super().__init__(titular, saldo_inicial)
        self.taxa_rendimento = taxa_rendimento

    @property
    def taxa_rendimento(self) -> float:
        return self._taxa_rendimento

    @taxa_rendimento.setter
    def taxa_rendimento(self, valor: float):
        if not 0 <= valor <= 1:
            raise ValueError("taxa de rendimento deve estar entre 0 e 1")
        self._taxa_rendimento = float(valor)

    def aplicar_rendimento(self) -> float:
        rendimento = round(self.saldo * self.taxa_rendimento, 2)
        self.saldo = self.saldo + rendimento
        return rendimento

    def __str__(self) -> str:
        return super().__str__() + f" — rende {self.taxa_rendimento:.2%}/mês"


class ContaInvestimento(Conta):
    """Conta com rendimento atrelado ao perfil de risco do titular."""

    _TAXAS_POR_PERFIL = {"conservador": 0.004, "moderado": 0.008, "arrojado": 0.015}

    def __init__(self, titular: Cliente, saldo_inicial: float = 0.0, perfil_risco: str = "moderado"):
        super().__init__(titular, saldo_inicial)
        self.perfil_risco = perfil_risco

    @property
    def perfil_risco(self) -> str:
        return self._perfil_risco

    @perfil_risco.setter
    def perfil_risco(self, valor: str):
        if valor not in self._TAXAS_POR_PERFIL:
            raise ValueError(f"perfil inválido: {valor!r} (use {list(self._TAXAS_POR_PERFIL)})")
        self._perfil_risco = valor

    def aplicar_rendimento(self) -> float:
        taxa = self._TAXAS_POR_PERFIL[self.perfil_risco]
        rendimento = round(self.saldo * taxa, 2)
        self.saldo = self.saldo + rendimento
        return rendimento

    def __str__(self) -> str:
        return super().__str__() + f" — perfil {self.perfil_risco}"
