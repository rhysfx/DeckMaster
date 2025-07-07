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
  `page` varchar(255) DEFAULT '1',
  `image_path` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `buttons` (`id`, `label`, `pos_x`, `pos_y`, `color_bg`, `color_fg`, `action`, `page`, `image_path`) VALUES
-- Row C: Page 1 only
(1, 'C1', -32, 319, '#2d2d30', 'white', NULL, '1', NULL),
(2, 'C2', 138, 317, '#2d2d30', 'white', NULL, '1', NULL),
(3, 'C3', 305, 316, '#2d2d30', 'white', NULL, '1', NULL),
(4, 'C4', 475, 316, '#2d2d30', 'white', NULL, '1', NULL),
(5, 'C5', 645, 316, '#2d2d30', 'white', NULL, '1', NULL),
(6, 'C6', 815, 316, '#2d2d30', 'white', NULL, '1', NULL),
(7, 'C7', 985, 316, '#2d2d30', 'white', NULL, '1', NULL),
(8, 'C8', 1153, 316, '#2d2d30', 'white', NULL, '1', NULL),
-- Row D: Page 2 only
(9, 'D1', -35, 488, '#2d2d30', 'white', NULL, '2', NULL),
(10, 'D2', 135, 488, '#2d2d30', 'white', NULL, '2', NULL),
(11, 'D3', 305, 488, '#2d2d30', 'white', NULL, '2', NULL),
(12, 'D4', 475, 488, '#2d2d30', 'white', NULL, '2', NULL),
(13, 'D5', 645, 488, '#2d2d30', 'white', NULL, '2', NULL),
(14, 'D6', 815, 488, '#2d2d30', 'white', NULL, '2', NULL),
(15, 'D7', 985, 488, '#2d2d30', 'white', NULL, '2', NULL),
(16, 'D8', 1153, 488, '#2d2d30', 'white', NULL, '2', NULL),
-- Row E: Shared across Page 1 and 2
(17, 'E1', -32, 663, '#2d2d30', 'white', NULL, '1,2', NULL),
(18, 'E2', 138, 663, '#2d2d30', 'white', NULL, '1,2', NULL),
(19, 'E3', 305, 662, '#2d2d30', 'white', NULL, '1,2', NULL),
(20, 'E4', 475, 662, '#2d2d30', 'white', NULL, '1,2', NULL),
(21, 'E5', 645, 662, '#2d2d30', 'white', NULL, '1,2', NULL),
(22, 'E6', 815, 662, '#2d2d30', 'white', NULL, '1,2', NULL);

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

CREATE TABLE `settings` (
  `key` varchar(255) NOT NULL,
  `value` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `settings` (`key`, `value`) VALUES
('BG_COLOR', '#1e1e1e'),
('BUTTON_ACTIVE_BG', '#007acc'),
('BUTTON_HEIGHT', '128'),
('BUTTON_WIDTH', '121'),
('CURSOR_PARK_X', '1900'),
('CURSOR_PARK_Y', '1060'),
('NAV_BUTTON_BG', '#2d2d30'),
('NAV_LEFT_X', '985'),
('NAV_RIGHT_X', '1153'),
('NAV_Y', '662'),
('OFFSET_BUTTON_V', '7'),
('OFFSET_X', '20'),
('UPDATE_INTERVAL', '500'),
('WEB_HEIGHT', '300'),
('WEB_MARGIN_TOP', '0');

ALTER TABLE `buttons`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `pages`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `page_number` (`page_number`);

ALTER TABLE `settings`
  ADD PRIMARY KEY (`key`);
COMMIT;

ALTER TABLE `buttons`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

ALTER TABLE `pages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
COMMIT;
