-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : ven. 09 jan. 2026 à 15:35
-- Version du serveur : 10.4.32-MariaDB
-- Version de PHP : 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `projet4`
--

-- --------------------------------------------------------

--
-- Structure de la table `logs`
--

CREATE TABLE `logs` (
  `id` int(11) NOT NULL,
  `timestamp` datetime DEFAULT current_timestamp(),
  `user` varchar(50) DEFAULT NULL,
  `action` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `logs`
--

INSERT INTO `logs` (`id`, `timestamp`, `user`, `action`) VALUES
(1, '2026-01-09 14:41:23', 'Shems', 'AUDIT: Création de compte'),
(2, '2026-01-09 14:41:25', 'shems', 'AUDIT: Connexion réussie'),
(3, '2026-01-09 14:41:56', 'shems', 'AUDIT: Déconnexion'),
(4, '2026-01-09 14:42:18', 'Shems', 'AUDIT: Échec de connexion'),
(5, '2026-01-09 14:42:25', 'Shems', 'AUDIT: Échec de connexion'),
(6, '2026-01-09 14:42:29', 'Shems', 'AUDIT: Échec de connexion'),
(7, '2026-01-09 14:42:32', 'Shems', 'AUDIT: Échec de connexion'),
(8, '2026-01-09 14:42:33', 'Shems', 'AUDIT: Échec de connexion'),
(9, '2026-01-09 14:42:36', 'Shems', 'AUDIT: Échec de connexion'),
(10, '2026-01-09 14:42:36', 'Shems', 'AUDIT: Échec de connexion'),
(11, '2026-01-09 14:42:37', 'Shems', 'AUDIT: Échec de connexion'),
(12, '2026-01-09 14:42:37', 'Shems', 'AUDIT: Échec de connexion'),
(13, '2026-01-09 14:42:37', 'Shems', 'AUDIT: Échec de connexion'),
(14, '2026-01-09 14:42:38', 'Shems', 'AUDIT: Échec de connexion'),
(15, '2026-01-09 14:42:38', 'Shems', 'AUDIT: Échec de connexion'),
(16, '2026-01-09 14:42:38', 'Shems', 'AUDIT: Échec de connexion'),
(17, '2026-01-09 14:42:39', 'Shems', 'AUDIT: Échec de connexion'),
(18, '2026-01-09 14:42:39', 'Shems', 'AUDIT: Échec de connexion'),
(19, '2026-01-09 14:42:39', 'Shems', 'AUDIT: Échec de connexion'),
(20, '2026-01-09 14:42:40', 'Shems', 'AUDIT: Échec de connexion'),
(21, '2026-01-09 14:42:40', 'Shems', 'AUDIT: Échec de connexion'),
(22, '2026-01-09 14:42:40', 'Shems', 'AUDIT: Échec de connexion'),
(23, '2026-01-09 14:42:41', 'Shems', 'AUDIT: Échec de connexion'),
(24, '2026-01-09 14:42:41', 'Shems', 'AUDIT: Échec de connexion'),
(25, '2026-01-09 14:42:41', 'Shems', 'AUDIT: Échec de connexion'),
(26, '2026-01-09 14:42:42', 'Shems', 'AUDIT: Échec de connexion'),
(27, '2026-01-09 14:42:46', 'Shems', 'AUDIT: Échec de connexion'),
(28, '2026-01-09 14:43:06', 'shems', 'AUDIT: Connexion réussie'),
(29, '2026-01-09 14:43:17', 'shems', 'AUDIT: Déconnexion'),
(30, '2026-01-09 14:43:29', 'Shems', 'AUDIT: Échec de connexion'),
(31, '2026-01-09 14:43:33', 'Shems', 'AUDIT: Échec de connexion'),
(32, '2026-01-09 14:43:37', 'Shems', 'AUDIT: Échec de connexion'),
(33, '2026-01-09 14:43:37', 'Shems', 'AUDIT: Échec de connexion'),
(34, '2026-01-09 14:43:37', 'Shems', 'AUDIT: Échec de connexion'),
(35, '2026-01-09 14:43:38', 'Shems', 'AUDIT: Échec de connexion'),
(36, '2026-01-09 14:43:38', 'Shems', 'AUDIT: Échec de connexion'),
(37, '2026-01-09 14:43:38', 'Shems', 'AUDIT: Échec de connexion'),
(38, '2026-01-09 14:43:39', 'Shems', 'AUDIT: Échec de connexion'),
(39, '2026-01-09 14:43:39', 'Shems', 'AUDIT: Échec de connexion'),
(40, '2026-01-09 14:43:39', 'Shems', 'AUDIT: Échec de connexion'),
(41, '2026-01-09 14:43:39', 'Shems', 'AUDIT: Échec de connexion'),
(42, '2026-01-09 14:43:40', 'Shems', 'AUDIT: Échec de connexion'),
(43, '2026-01-09 14:43:40', 'Shems', 'AUDIT: Échec de connexion'),
(44, '2026-01-09 14:43:40', 'Shems', 'AUDIT: Échec de connexion'),
(45, '2026-01-09 14:43:41', 'Shems', 'AUDIT: Échec de connexion'),
(46, '2026-01-09 14:43:41', 'Shems', 'AUDIT: Échec de connexion'),
(47, '2026-01-09 14:43:41', 'Shems', 'AUDIT: Échec de connexion'),
(48, '2026-01-09 14:43:42', 'Shems', 'AUDIT: Échec de connexion'),
(49, '2026-01-09 14:43:42', 'Shems', 'AUDIT: Échec de connexion'),
(50, '2026-01-09 14:43:42', 'Shems', 'AUDIT: Échec de connexion'),
(51, '2026-01-09 14:43:42', 'Shems', 'AUDIT: Échec de connexion'),
(52, '2026-01-09 14:54:44', 'Shems', 'AUDIT: Échec de connexion'),
(53, '2026-01-09 14:54:47', 'Shems', 'AUDIT: Échec de connexion'),
(54, '2026-01-09 14:54:48', 'Shems', 'AUDIT: Compte bloqué après plusieurs échecs'),
(55, '2026-01-09 15:19:59', 'Shems', 'AUDIT: Échec de connexion'),
(56, '2026-01-09 15:20:03', 'Shems', 'AUDIT: Échec de connexion'),
(57, '2026-01-09 15:20:05', 'Shems', 'AUDIT: Compte bloqué après plusieurs échecs');

-- --------------------------------------------------------

--
-- Structure de la table `products`
--

CREATE TABLE `products` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `stock` int(11) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `products`
--

INSERT INTO `products` (`id`, `name`, `price`, `stock`) VALUES
(1, 'Produit démo', 9.99, 5);

-- --------------------------------------------------------

--
-- Structure de la table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `mail` varchar(100) NOT NULL,
  `salt` varchar(64) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('client','admin') DEFAULT 'client',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `logs`
--
ALTER TABLE `logs`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `logs`
--
ALTER TABLE `logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=58;

--
-- AUTO_INCREMENT pour la table `products`
--
ALTER TABLE `products`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
