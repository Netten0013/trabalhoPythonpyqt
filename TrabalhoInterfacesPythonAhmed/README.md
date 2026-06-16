# Trabalho Interfaces Python

Esse projeto e um sistema simples de oficina feito em Python com PyQt5.

Ele serve para cadastrar clientes, carros, servicos e ordens de servico.

## Banco de dados

O banco agora foi feito para usar no XAMPP, pelo phpMyAdmin.

Para criar o banco:

1. Abra o XAMPP.
2. Ligue o MySQL.
3. Entre no phpMyAdmin.
4. Va na aba SQL.
5. Cole o conteudo do arquivo `database/banco.sql`.
6. Clique em executar.

O nome do banco criado vai ser:

`oficina_os`

## Pacote necessario no Python

Como o sistema usa MySQL, precisa instalar esse pacote:

```bash
pip install mysql-connector-python
```

## Rodar o sistema

```bash
python src/main.py
```

## Login para teste

usuario: admin

senha: admin

## Documento

O documento de requisitos esta na pasta `docs`.
