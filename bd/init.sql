-- Suppression des tables si elles existent déjà
DROP TABLE IF EXISTS Money;
DROP TABLE IF EXISTS User;

-- =========================
-- Table User
-- =========================
CREATE TABLE User (
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) PRIMARY KEY,
    mot_de_passe VARCHAR(255) NOT NULL
);

-- =========================
-- Table Money
-- =========================
CREATE TABLE Money (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50) NOT NULL
);

-- =========================
-- Insertion des cryptos
-- =========================
INSERT INTO Money (nom) VALUES
('BTC'),
('ETH'),
('SOL'),
('XRP'),
('ADA'),
('DOGE'),
('USDT'),
('SHIB'),
('LINK'),
('BNB'),
('TRX'),
('AVAX'),
('USDC');

-- =========================
-- Insertion d’un user de base
-- =========================
INSERT INTO User (nom, prenom, email, mot_de_passe) VALUES
('Dupont', 'Jean', 'jean.dupont@email.com', 'password123');
