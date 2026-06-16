CREATE DATABASE IF NOT EXISTS oficina_os
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE oficina_os;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    senha VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(20),
    telefone VARCHAR(30),
    email VARCHAR(100),
    endereco VARCHAR(200)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS carros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    marca VARCHAR(60) NOT NULL,
    modelo VARCHAR(60) NOT NULL,
    placa VARCHAR(20),
    ano INT,
    CONSTRAINT fk_carros_clientes
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS servicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    valor DECIMAL(10,2) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ordens_servico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    carro_id INT NOT NULL,
    servico_id INT NOT NULL,
    data DATE NOT NULL,
    status VARCHAR(40) NOT NULL,
    valor DECIMAL(10,2) DEFAULT 0,
    observacoes TEXT,
    CONSTRAINT fk_os_clientes
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_os_carros
        FOREIGN KEY (carro_id) REFERENCES carros(id),
    CONSTRAINT fk_os_servicos
        FOREIGN KEY (servico_id) REFERENCES servicos(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO usuarios (usuario, senha)
VALUES ('admin', 'admin');
