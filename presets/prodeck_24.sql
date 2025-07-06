-- ProDeck 24 initial base setup

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

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

INSERT INTO `buttons` (`id`, `label`, `pos_x`, `pos_y`, `color_bg`, `color_fg`, `action`, `page`, `image_path`) VALUES
-- Page 1
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
-- Page 2 (the duplicate buttons may seem redundant, but they're necessary when simulating a two-page display with web page - without the second set, it may crashout ever so slightly as the yutes say)
(23, 'C1', -32, 319, '#2d2d30', 'white', NULL, 2, NULL),
(24, 'C2', 138, 317, '#2d2d30', 'white', NULL, 2, NULL),
(25, 'C3', 305, 316, '#2d2d30', 'white', NULL, 2, NULL),
(26, 'C4', 475, 316, '#2d2d30', 'white', NULL, 2, NULL),
(27, 'C5', 645, 316, '#2d2d30', 'white', NULL, 2, NULL),
(28, 'C6', 815, 316, '#2d2d30', 'white', NULL, 2, NULL),
(29, 'C7', 985, 316, '#2d2d30', 'white', NULL, 2, NULL),
(30, 'C8', 1153, 316, '#2d2d30', 'white', NULL, 2, NULL),
(31, 'D1', -35, 488, '#2d2d30', 'white', NULL, 2, NULL),
(32, 'D2', 135, 488, '#2d2d30', 'white', NULL, 2, NULL),
(33, 'D3', 305, 488, '#2d2d30', 'white', NULL, 2, NULL),
(34, 'D4', 475, 488, '#2d2d30', 'white', NULL, 2, NULL),
(35, 'D5', 645, 488, '#2d2d30', 'white', NULL, 2, NULL),
(36, 'D6', 815, 488, '#2d2d30', 'white', NULL, 2, NULL),
(37, 'D7', 985, 488, '#2d2d30', 'white', NULL, 2, NULL),
(38, 'D8', 1153, 488, '#2d2d30', 'white', NULL, 2, NULL),
(39, 'E1', -32, 663, '#2d2d30', 'white', NULL, 2, NULL),
(40, 'E2', 138, 663, '#2d2d30', 'white', NULL, 2, NULL),
(41, 'E3', 305, 662, '#2d2d30', 'white', NULL, 2, NULL),
(42, 'E4', 475, 662, '#2d2d30', 'white', NULL, 2, NULL),
(43, 'E5', 645, 662, '#2d2d30', 'white', NULL, 2, NULL),
(44, 'E6', 815, 662, '#2d2d30', 'white', NULL, 2, NULL);

CREATE TABLE `pages` (
  `id` int(11) NOT NULL,
  `page_number` int(11) NOT NULL,
  `webpage_url` varchar(500) DEFAULT NULL,
  `show_webpage` tinyint(1) DEFAULT 0,
  `background_color` varchar(7) DEFAULT '#1e1e1e'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `pages` (`id`, `page_number`, `webpage_url`, `show_webpage`, `background_color`) VALUES
(1, 1, NULL, 0, '#1e1e1e'),
(2, 2, 'https://google.co.uk/', 1, '#1e1e1e');

ALTER TABLE `buttons`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `pages`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `page_number` (`page_number`);

ALTER TABLE `buttons`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

ALTER TABLE `pages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
COMMIT;
