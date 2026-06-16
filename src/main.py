import sys
from pathlib import Path

try:
    import mysql.connector
    from mysql.connector import Error, IntegrityError
except ModuleNotFoundError:
    print("Instale o conector do MySQL: pip install mysql-connector-python")
    sys.exit(1)
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QHeaderView


BASE_DIR = Path(__file__).resolve().parent
UI_FILE = BASE_DIR / "sistema_ordem_servico.ui"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "oficina_os",
}


class Linha(dict):
    def __iter__(self):
        return iter(self.values())


class Banco:
    def __init__(self):
        self.conn = mysql.connector.connect(**DB_CONFIG)

    def executar(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur

    def listar(self, sql, params=()):
        cur = self.conn.cursor(dictionary=True)
        cur.execute(sql, params)
        return [Linha(linha) for linha in cur.fetchall()]

    def um(self, sql, params=()):
        cur = self.conn.cursor(dictionary=True)
        cur.execute(sql, params)
        linha = cur.fetchone()
        return Linha(linha) if linha else None


class SistemaOS:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.tela = uic.loadUi(str(UI_FILE))
        try:
            self.db = Banco()
        except Error as erro:
            QMessageBox.critical(self.tela, "Erro no banco", str(erro))
            sys.exit(1)

        self.configurar_tabelas()
        self.conectar_eventos()
        self.carregar_tudo()

        self.tela.stackedWidget.setCurrentIndex(0)
        self.tela.dateOS.setDate(QDate.currentDate())

    def configurar_tabelas(self):
        tabelas = [
            self.tela.tblClientes,
            self.tela.tblCarros,
            self.tela.tblServicos,
            self.tela.tblOrdensServico,
            self.tela.tblListarOrdens,
        ]
        for tabela in tabelas:
            tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            tabela.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            tabela.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def conectar_eventos(self):
        # Login e navegaÃ§Ã£o
        self.tela.btnEntrar.clicked.connect(self.login)
        self.tela.btnSair.clicked.connect(lambda: self.tela.stackedWidget.setCurrentIndex(0))
        self.tela.btnCardCliente.clicked.connect(lambda: self.tela.tabWidget.setCurrentIndex(1))
        self.tela.btnCardCarro.clicked.connect(lambda: self.tela.tabWidget.setCurrentIndex(2))
        self.tela.btnCardServico.clicked.connect(lambda: self.tela.tabWidget.setCurrentIndex(3))
        self.tela.btnCardOS.clicked.connect(lambda: self.tela.tabWidget.setCurrentIndex(4))
        self.tela.btnCardListarOS.clicked.connect(lambda: self.tela.tabWidget.setCurrentIndex(5))

        # Cliente
        self.tela.btnNovoCliente.clicked.connect(self.limpar_cliente)
        self.tela.btnLimparCliente.clicked.connect(self.limpar_cliente)
        self.tela.btnSalvarCliente.clicked.connect(self.salvar_cliente)
        self.tela.btnEditarCliente.clicked.connect(self.editar_cliente)
        self.tela.btnExcluirCliente.clicked.connect(self.excluir_cliente)
        self.tela.tblClientes.cellClicked.connect(self.selecionar_cliente)

        # Carro
        self.tela.btnNovoCarro.clicked.connect(self.limpar_carro)
        self.tela.btnLimparCarro.clicked.connect(self.limpar_carro)
        self.tela.btnSalvarCarro.clicked.connect(self.salvar_carro)
        self.tela.btnEditarCarro.clicked.connect(self.editar_carro)
        self.tela.btnExcluirCarro.clicked.connect(self.excluir_carro)
        self.tela.tblCarros.cellClicked.connect(self.selecionar_carro)

        # ServiÃ§o
        self.tela.btnNovoServico.clicked.connect(self.limpar_servico)
        self.tela.btnLimparServico.clicked.connect(self.limpar_servico)
        self.tela.btnSalvarServico.clicked.connect(self.salvar_servico)
        self.tela.btnEditarServico.clicked.connect(self.editar_servico)
        self.tela.btnExcluirServico.clicked.connect(self.excluir_servico)
        self.tela.tblServicos.cellClicked.connect(self.selecionar_servico)

        # Ordem de ServiÃ§o
        self.tela.btnNovaOS.clicked.connect(self.limpar_os)
        self.tela.btnLimparOS.clicked.connect(self.limpar_os)
        self.tela.btnSalvarOS.clicked.connect(self.salvar_os)
        self.tela.btnEditarOS.clicked.connect(self.editar_os)
        self.tela.btnExcluirOS.clicked.connect(self.excluir_os)
        self.tela.tblOrdensServico.cellClicked.connect(self.selecionar_os)
        self.tela.cmbOSCliente.currentIndexChanged.connect(self.carregar_carros_os)
        self.tela.cmbOSServico.currentIndexChanged.connect(self.preencher_valor_servico)

        # Listagem
        self.tela.btnPesquisarOS.clicked.connect(self.carregar_listagem_os)
        self.tela.btnAtualizarOS.clicked.connect(self.carregar_listagem_os)

    def aviso(self, titulo, texto):
        QMessageBox.information(self.tela, titulo, texto)

    def erro(self, texto):
        QMessageBox.warning(self.tela, "Aviso", texto)

    def confirmar(self, texto):
        return QMessageBox.question(
            self.tela,
            "Confirmar",
            texto,
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes

    def item(self, tabela, row, col):
        it = tabela.item(row, col)
        return it.text() if it else ""

    def preencher_tabela(self, tabela, linhas):
        tabela.setRowCount(0)
        for row_num, linha in enumerate(linhas):
            tabela.insertRow(row_num)
            for col_num, valor in enumerate(linha):
                tabela.setItem(row_num, col_num, QTableWidgetItem(str(valor if valor is not None else "")))

    def selecionar_combo_por_id(self, combo, valor_id):
        for i in range(combo.count()):
            if combo.itemData(i) == valor_id:
                combo.setCurrentIndex(i)
                return

    # LOGIN
    def login(self):
        usuario = self.tela.txtUsuario.text().strip()
        senha = self.tela.txtSenha.text().strip()
        user = self.db.um("SELECT * FROM usuarios WHERE usuario=%s AND senha=%s", (usuario, senha))
        if user:
            self.tela.stackedWidget.setCurrentIndex(1)
            self.tela.tabWidget.setCurrentIndex(0)
            self.tela.txtSenha.clear()
        else:
            self.erro("UsuÃ¡rio ou senha errado.")

    # CARREGAMENTO GERAL
    def carregar_tudo(self):
        self.carregar_clientes()
        self.carregar_combos()
        self.carregar_carros()
        self.carregar_servicos()
        self.carregar_ordens()
        self.carregar_listagem_os()

    def carregar_combos(self):
        clientes = self.db.listar("SELECT id, nome FROM clientes ORDER BY nome")
        self.tela.cmbCarroCliente.clear()
        self.tela.cmbOSCliente.clear()
        for c in clientes:
            self.tela.cmbCarroCliente.addItem(c["nome"], c["id"])
            self.tela.cmbOSCliente.addItem(c["nome"], c["id"])

        servicos = self.db.listar("SELECT id, nome, valor FROM servicos ORDER BY nome")
        self.tela.cmbOSServico.clear()
        for s in servicos:
            self.tela.cmbOSServico.addItem(s["nome"], s["id"])

        self.carregar_carros_os()

    # CLIENTE
    def limpar_cliente(self):
        self.tela.txtClienteId.clear()
        self.tela.txtClienteNome.clear()
        self.tela.txtClienteCpf.clear()
        self.tela.txtClienteTelefone.clear()
        self.tela.txtClienteEmail.clear()
        self.tela.txtClienteEndereco.clear()

    def salvar_cliente(self):
        nome = self.tela.txtClienteNome.text().strip()
        if not nome:
            self.erro("Digite o nome do cliente.")
            return
        self.db.executar(
            "INSERT INTO clientes (nome, cpf, telefone, email, endereco) VALUES (%s, %s, %s, %s, %s)",
            (
                nome,
                self.tela.txtClienteCpf.text().strip(),
                self.tela.txtClienteTelefone.text().strip(),
                self.tela.txtClienteEmail.text().strip(),
                self.tela.txtClienteEndereco.text().strip(),
            )
        )
        self.limpar_cliente()
        self.carregar_tudo()
        self.aviso("Aviso", "Cliente salvo.")

    def editar_cliente(self):
        cliente_id = self.tela.txtClienteId.text().strip()
        if not cliente_id:
            self.erro("Selecione um cliente na tabela para editar.")
            return
        self.db.executar(
            "UPDATE clientes SET nome=%s, cpf=%s, telefone=%s, email=%s, endereco=%s WHERE id=%s",
            (
                self.tela.txtClienteNome.text().strip(),
                self.tela.txtClienteCpf.text().strip(),
                self.tela.txtClienteTelefone.text().strip(),
                self.tela.txtClienteEmail.text().strip(),
                self.tela.txtClienteEndereco.text().strip(),
                cliente_id,
            )
        )
        self.carregar_tudo()
        self.aviso("Aviso", "Cliente alterado.")

    def excluir_cliente(self):
        cliente_id = self.tela.txtClienteId.text().strip()
        if not cliente_id:
            self.erro("Selecione um cliente na tabela para excluir.")
            return
        if self.confirmar("Excluir este cliente? Carros e OS vinculados podem impedir a exclusÃ£o."):
            try:
                self.db.executar("DELETE FROM clientes WHERE id=%s", (cliente_id,))
                self.limpar_cliente()
                self.carregar_tudo()
            except IntegrityError:
                self.erro("NÃ£o foi possÃ­vel excluir. Existe carro ou OS vinculada a este cliente.")

    def carregar_clientes(self):
        linhas = self.db.listar("SELECT id, nome, cpf, telefone, email FROM clientes ORDER BY id DESC")
        self.preencher_tabela(self.tela.tblClientes, [tuple(l) for l in linhas])

    def selecionar_cliente(self, row, col):
        cliente_id = self.item(self.tela.tblClientes, row, 0)
        c = self.db.um("SELECT * FROM clientes WHERE id=%s", (cliente_id,))
        if c:
            self.tela.txtClienteId.setText(str(c["id"]))
            self.tela.txtClienteNome.setText(c["nome"] or "")
            self.tela.txtClienteCpf.setText(c["cpf"] or "")
            self.tela.txtClienteTelefone.setText(c["telefone"] or "")
            self.tela.txtClienteEmail.setText(c["email"] or "")
            self.tela.txtClienteEndereco.setText(c["endereco"] or "")

    # CARRO
    def limpar_carro(self):
        self.tela.txtCarroId.clear()
        self.tela.txtCarroMarca.clear()
        self.tela.txtCarroModelo.clear()
        self.tela.txtCarroPlaca.clear()
        self.tela.spnCarroAno.setValue(2026)

    def salvar_carro(self):
        cliente_id = self.tela.cmbCarroCliente.currentData()
        marca = self.tela.txtCarroMarca.text().strip()
        modelo = self.tela.txtCarroModelo.text().strip()
        if not cliente_id:
            self.erro("Cadastre um cliente antes de cadastrar carro.")
            return
        if not marca or not modelo:
            self.erro("Digite marca e modelo do carro.")
            return
        self.db.executar(
            "INSERT INTO carros (cliente_id, marca, modelo, placa, ano) VALUES (%s, %s, %s, %s, %s)",
            (cliente_id, marca, modelo, self.tela.txtCarroPlaca.text().strip(), self.tela.spnCarroAno.value())
        )
        self.limpar_carro()
        self.carregar_tudo()
        self.aviso("Aviso", "Carro salvo.")

    def editar_carro(self):
        carro_id = self.tela.txtCarroId.text().strip()
        if not carro_id:
            self.erro("Selecione um carro na tabela para editar.")
            return
        self.db.executar(
            "UPDATE carros SET cliente_id=%s, marca=%s, modelo=%s, placa=%s, ano=%s WHERE id=%s",
            (
                self.tela.cmbCarroCliente.currentData(),
                self.tela.txtCarroMarca.text().strip(),
                self.tela.txtCarroModelo.text().strip(),
                self.tela.txtCarroPlaca.text().strip(),
                self.tela.spnCarroAno.value(),
                carro_id,
            )
        )
        self.carregar_tudo()
        self.aviso("Aviso", "Carro alterado.")

    def excluir_carro(self):
        carro_id = self.tela.txtCarroId.text().strip()
        if not carro_id:
            self.erro("Selecione um carro na tabela para excluir.")
            return
        if self.confirmar("Excluir este carro?"):
            try:
                self.db.executar("DELETE FROM carros WHERE id=%s", (carro_id,))
                self.limpar_carro()
                self.carregar_tudo()
            except IntegrityError:
                self.erro("NÃ£o foi possÃ­vel excluir. Existe OS vinculada a este carro.")

    def carregar_carros(self):
        linhas = self.db.listar("""
            SELECT carros.id, clientes.nome, carros.marca, carros.modelo, carros.placa, carros.ano
            FROM carros
            JOIN clientes ON clientes.id = carros.cliente_id
            ORDER BY carros.id DESC
        """)
        self.preencher_tabela(self.tela.tblCarros, [tuple(l) for l in linhas])

    def selecionar_carro(self, row, col):
        carro_id = self.item(self.tela.tblCarros, row, 0)
        c = self.db.um("SELECT * FROM carros WHERE id=%s", (carro_id,))
        if c:
            self.tela.txtCarroId.setText(str(c["id"]))
            self.selecionar_combo_por_id(self.tela.cmbCarroCliente, c["cliente_id"])
            self.tela.txtCarroMarca.setText(c["marca"] or "")
            self.tela.txtCarroModelo.setText(c["modelo"] or "")
            self.tela.txtCarroPlaca.setText(c["placa"] or "")
            self.tela.spnCarroAno.setValue(c["ano"] or 2026)

    # SERVIÃ‡O
    def limpar_servico(self):
        self.tela.txtServicoId.clear()
        self.tela.txtServicoNome.clear()
        self.tela.txtServicoDescricao.clear()
        self.tela.spnServicoValor.setValue(0)

    def salvar_servico(self):
        nome = self.tela.txtServicoNome.text().strip()
        if not nome:
            self.erro("Digite o nome do serviÃ§o.")
            return
        self.db.executar(
            "INSERT INTO servicos (nome, descricao, valor) VALUES (%s, %s, %s)",
            (nome, self.tela.txtServicoDescricao.toPlainText().strip(), self.tela.spnServicoValor.value())
        )
        self.limpar_servico()
        self.carregar_tudo()
        self.aviso("Aviso", "ServiÃ§o salvo.")

    def editar_servico(self):
        servico_id = self.tela.txtServicoId.text().strip()
        if not servico_id:
            self.erro("Selecione um serviÃ§o na tabela para editar.")
            return
        self.db.executar(
            "UPDATE servicos SET nome=%s, descricao=%s, valor=%s WHERE id=%s",
            (
                self.tela.txtServicoNome.text().strip(),
                self.tela.txtServicoDescricao.toPlainText().strip(),
                self.tela.spnServicoValor.value(),
                servico_id,
            )
        )
        self.carregar_tudo()
        self.aviso("Aviso", "ServiÃ§o alterado.")

    def excluir_servico(self):
        servico_id = self.tela.txtServicoId.text().strip()
        if not servico_id:
            self.erro("Selecione um serviÃ§o na tabela para excluir.")
            return
        if self.confirmar("Excluir este serviÃ§o?"):
            try:
                self.db.executar("DELETE FROM servicos WHERE id=%s", (servico_id,))
                self.limpar_servico()
                self.carregar_tudo()
            except IntegrityError:
                self.erro("NÃ£o foi possÃ­vel excluir. Existe OS vinculada a este serviÃ§o.")

    def carregar_servicos(self):
        linhas = self.db.listar("SELECT id, nome, descricao, FORMAT(valor, 2) FROM servicos ORDER BY id DESC")
        self.preencher_tabela(self.tela.tblServicos, [tuple(l) for l in linhas])

    def selecionar_servico(self, row, col):
        servico_id = self.item(self.tela.tblServicos, row, 0)
        s = self.db.um("SELECT * FROM servicos WHERE id=%s", (servico_id,))
        if s:
            self.tela.txtServicoId.setText(str(s["id"]))
            self.tela.txtServicoNome.setText(s["nome"] or "")
            self.tela.txtServicoDescricao.setPlainText(s["descricao"] or "")
            self.tela.spnServicoValor.setValue(float(s["valor"] or 0))

    # ORDEM DE SERVIÃ‡O
    def carregar_carros_os(self):
        cliente_id = self.tela.cmbOSCliente.currentData()
        self.tela.cmbOSCarro.clear()
        if not cliente_id:
            return
        carros = self.db.listar(
            "SELECT id, marca, modelo, placa FROM carros WHERE cliente_id=%s ORDER BY marca, modelo",
            (cliente_id,)
        )
        for c in carros:
            texto = f"{c['marca']} {c['modelo']} - {c['placa']}"
            self.tela.cmbOSCarro.addItem(texto, c["id"])

    def preencher_valor_servico(self):
        servico_id = self.tela.cmbOSServico.currentData()
        if servico_id:
            s = self.db.um("SELECT valor FROM servicos WHERE id=%s", (servico_id,))
            if s:
                self.tela.spnOSValor.setValue(float(s["valor"] or 0))

    def limpar_os(self):
        self.tela.txtOSId.clear()
        self.tela.dateOS.setDate(QDate.currentDate())
        self.tela.cmbOSStatus.setCurrentIndex(0)
        self.tela.spnOSValor.setValue(0)
        self.tela.txtOSObs.clear()
        self.preencher_valor_servico()

    def salvar_os(self):
        cliente_id = self.tela.cmbOSCliente.currentData()
        carro_id = self.tela.cmbOSCarro.currentData()
        servico_id = self.tela.cmbOSServico.currentData()
        if not cliente_id or not carro_id or not servico_id:
            self.erro("Cadastre cliente, carro e serviÃ§o antes de criar uma OS.")
            return
        self.db.executar(
            """
            INSERT INTO ordens_servico
            (cliente_id, carro_id, servico_id, data, status, valor, observacoes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                cliente_id,
                carro_id,
                servico_id,
                self.tela.dateOS.date().toString("yyyy-MM-dd"),
                self.tela.cmbOSStatus.currentText(),
                self.tela.spnOSValor.value(),
                self.tela.txtOSObs.toPlainText().strip(),
            )
        )
        self.limpar_os()
        self.carregar_tudo()
        self.aviso("Aviso", "Ordem salva.")

    def editar_os(self):
        os_id = self.tela.txtOSId.text().strip()
        if not os_id:
            self.erro("Selecione uma OS na tabela para editar.")
            return
        self.db.executar(
            """
            UPDATE ordens_servico
            SET cliente_id=%s, carro_id=%s, servico_id=%s, data=%s, status=%s, valor=%s, observacoes=%s
            WHERE id=%s
            """,
            (
                self.tela.cmbOSCliente.currentData(),
                self.tela.cmbOSCarro.currentData(),
                self.tela.cmbOSServico.currentData(),
                self.tela.dateOS.date().toString("yyyy-MM-dd"),
                self.tela.cmbOSStatus.currentText(),
                self.tela.spnOSValor.value(),
                self.tela.txtOSObs.toPlainText().strip(),
                os_id,
            )
        )
        self.carregar_tudo()
        self.aviso("Aviso", "OS alterada.")

    def excluir_os(self):
        os_id = self.tela.txtOSId.text().strip()
        if not os_id:
            self.erro("Selecione uma OS na tabela para excluir.")
            return
        if self.confirmar("Excluir esta ordem de serviÃ§o?"):
            self.db.executar("DELETE FROM ordens_servico WHERE id=%s", (os_id,))
            self.limpar_os()
            self.carregar_tudo()

    def carregar_ordens(self):
        linhas = self.db.listar("""
            SELECT os.id, cl.nome, CONCAT(ca.marca, ' ', ca.modelo), se.nome, os.data, os.status, FORMAT(os.valor, 2)
            FROM ordens_servico os
            JOIN clientes cl ON cl.id = os.cliente_id
            JOIN carros ca ON ca.id = os.carro_id
            JOIN servicos se ON se.id = os.servico_id
            ORDER BY os.id DESC
        """)
        self.preencher_tabela(self.tela.tblOrdensServico, [tuple(l) for l in linhas])

    def selecionar_os(self, row, col):
        os_id = self.item(self.tela.tblOrdensServico, row, 0)
        os = self.db.um("SELECT * FROM ordens_servico WHERE id=%s", (os_id,))
        if os:
            self.tela.txtOSId.setText(str(os["id"]))
            self.selecionar_combo_por_id(self.tela.cmbOSCliente, os["cliente_id"])
            self.carregar_carros_os()
            self.selecionar_combo_por_id(self.tela.cmbOSCarro, os["carro_id"])
            self.selecionar_combo_por_id(self.tela.cmbOSServico, os["servico_id"])
            data_os = os["data"]
            if hasattr(data_os, "strftime"):
                data_os = data_os.strftime("%Y-%m-%d")
            self.tela.dateOS.setDate(QDate.fromString(str(data_os), "yyyy-MM-dd"))
            self.tela.cmbOSStatus.setCurrentText(os["status"])
            self.tela.spnOSValor.setValue(float(os["valor"] or 0))
            self.tela.txtOSObs.setPlainText(os["observacoes"] or "")

    def carregar_listagem_os(self):
        busca = self.tela.txtPesquisarOS.text().strip()
        status = self.tela.cmbFiltroStatus.currentText()
        params = []
        where = []

        if busca:
            where.append("""
                (CAST(os.id AS CHAR) LIKE %s OR cl.nome LIKE %s OR ca.placa LIKE %s OR se.nome LIKE %s)
            """)
            termo = f"%{busca}%"
            params.extend([termo, termo, termo, termo])

        if status != "Todos os status":
            where.append("os.status = %s")
            params.append(status)

        sql = """
            SELECT os.id, cl.nome, cl.telefone,
                   CONCAT(ca.marca, ' ', ca.modelo), ca.placa,
                   se.nome, os.data, os.status, FORMAT(os.valor, 2)
            FROM ordens_servico os
            JOIN clientes cl ON cl.id = os.cliente_id
            JOIN carros ca ON ca.id = os.carro_id
            JOIN servicos se ON se.id = os.servico_id
        """
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY os.id DESC"

        linhas = self.db.listar(sql, params)
        self.preencher_tabela(self.tela.tblListarOrdens, [tuple(l) for l in linhas])

    def executar(self):
        self.tela.show()
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    SistemaOS().executar()


