-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 29, 2025 at 11:49 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `deckmaster`
--

-- --------------------------------------------------------

--
-- Table structure for table `buttons`
--

CREATE TABLE `buttons` (
  `id` int(11) NOT NULL,
  `label` varchar(50) NOT NULL,
  `pos_x` int(11) NOT NULL,
  `pos_y` int(11) NOT NULL,
  `color_bg` varchar(7) DEFAULT '#2d2d30',
  `color_fg` varchar(7) DEFAULT 'white',
  `action` varchar(255) DEFAULT NULL,
  `page` int(11) DEFAULT 1,
  `image_path` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `buttons`
--

INSERT INTO `buttons` (`id`, `label`, `pos_x`, `pos_y`, `color_bg`, `color_fg`, `action`, `page`, `image_path`) VALUES
(1, 'C1', -32, 319, '#2d2d30', 'white', NULL, 1, NULL),
(2, 'C2', 138, 317, '#2d2d30', 'white', NULL, 1, NULL),
(3, 'C3', 305, 316, '#2d2d30', 'white', NULL, 1, NULL),
(4, 'C4', 475, 316, '#2d2d30', 'white', NULL, 1, NULL),
(5, 'C5', 645, 316, '#2d2d30', 'white', NULL, 1, NULL),
(6, 'C6', 815, 316, '#2d2d30', 'white', NULL, 1, NULL),
(7, 'C7', 985, 316, '#2d2d30', 'white', NULL, 1, NULL),
(8, 'C8', 1153, 316, '#2d2d30', 'white', NULL, 1, NULL),
(9, 'D1', -35, 488, '#2d2d30', 'white', NULL, 1, NULL),
(10, 'D2', 135, 488, '#2d2d30', 'white', NULL, 1, NULL),
(11, 'D3', 305, 488, '#2d2d30', 'white', NULL, 1, NULL),
(12, 'D4', 475, 488, '#2d2d30', 'white', NULL, 1, NULL),
(13, 'D5', 645, 488, '#2d2d30', 'white', NULL, 1, NULL),
(14, 'D6', 815, 488, '#2d2d30', 'white', NULL, 1, NULL),
(15, 'D7', 985, 488, '#2d2d30', 'white', NULL, 1, NULL),
(16, 'D8', 1153, 488, '#2d2d30', 'white', NULL, 1, NULL),
(17, 'E1', -32, 663, '#2d2d30', 'white', NULL, 1, NULL),
(18, 'E2', 138, 663, '#2d2d30', 'white', NULL, 1, NULL),
(19, 'E3', 305, 662, '#2d2d30', 'white', NULL, 1, NULL),
(20, 'E4', 475, 662, '#2d2d30', 'white', NULL, 1, NULL),
(21, 'E5', 645, 662, '#2d2d30', 'white', NULL, 1, NULL),
(22, 'E6', 815, 662, '#2d2d30', 'white', NULL, 1, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `buttons`
--
ALTER TABLE `buttons`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `buttons`
--
ALTER TABLE `buttons`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
