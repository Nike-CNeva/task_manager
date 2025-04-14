CREATE TABLE `Users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL COMMENT 'Имя',
  `firstname` VARCHAR(50) NULL COMMENT 'Фамилия',
  `email` VARCHAR(100) NULL COMMENT 'Электронная почта',
  `telegram` VARCHAR(50) NULL COMMENT 'Телеграм',
  `username` VARCHAR(50) NOT NULL COMMENT 'Никнейм',
  `password` CHAR(60) NOT NULL COMMENT 'Пароль (bcrypt)',
  `user_type` INT NOT NULL COMMENT 'Айди должности',
  `workshop` INT NULL COMMENT 'Айди цеха',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Активен',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_type`) REFERENCES `User_type`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`workshop`) REFERENCES `Workshop`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Bid` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `task_number` VARCHAR(50) NULL COMMENT 'Номер заявки',
  `customer_id` INT NOT NULL COMMENT 'Айди заказчика',
  `manager_id` INT NULL COMMENT 'Айди менеджера',
  `task_id` INT NOT NULL COMMENT 'Айди задачи',
  `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Удалено',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`customer_id`) REFERENCES `Customer`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`manager_id`) REFERENCES `Manager`(`id`) ON DELETE SET NULL,
  FOREIGN KEY (`task_id`) REFERENCES `Task`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Task` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `bid_id` INT NOT NULL COMMENT 'Айди заявки',
  `product_type_id` INT NOT NULL COMMENT 'Айди типа изделия',
  `material_id` INT NOT NULL COMMENT 'Айди материала изделия',
  `quantity` INT NOT NULL COMMENT 'Количество изделий',
  `urgency_id` INT NOT NULL COMMENT 'Айди срочности',
  `status_id` INT NOT NULL COMMENT 'Айди статуса готовности',
  `workshop_id` INT NOT NULL COMMENT 'Айди цеха',
  `responsible_id` INT NOT NULL COMMENT 'Ответственный',
  `sheets_id` INT NULL COMMENT 'Айди листов',
  `waste` INT NULL COMMENT 'Отходность',
  `weight` INT NULL COMMENT 'Вес',
  `files_id` INT NULL COMMENT 'Айди файлов',
  `comment_id` INT NULL COMMENT 'Айди комментариев',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата создания',
  `completed_at` TIMESTAMP NULL COMMENT 'Дата выполнения',
  `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Удалено',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`bid_id`) REFERENCES `Bid`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`product_type_id`) REFERENCES `Product`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`material_id`) REFERENCES `Material`(`id`) ON DELETE SET NULL,
  FOREIGN KEY (`urgency_id`) REFERENCES `Urgency`(`id`) ON DELETE SET NULL,
  FOREIGN KEY (`status_id`) REFERENCES `Status`(`id`) ON DELETE SET NULL,
  FOREIGN KEY (`workshop_id`) REFERENCES `Workshop`(`id`) ON DELETE SET NULL,
  FOREIGN KEY (`responsible_id`) REFERENCES `Users`(`id`) ON DELETE SET NULL,
  FOREIGN KEY (`sheets_id`) REFERENCES `Sheets`(`id`) ON DELETE SET NULL,
  FOREIGN KEY (`files_id`) REFERENCES `Files`(`id`) ON DELETE SET NULL,
  FOREIGN KEY (`comment_id`) REFERENCES `Comment`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `User_type` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL COMMENT 'Должность',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Workshop` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL COMMENT 'Название цеха',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Customer` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL COMMENT 'Заказчик',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Manager` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL COMMENT 'Менеджер',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Product` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `type` ENUM('Profile', 'Klamer', 'Bracket', 'ExtensionBracket', 'Cassette', 'LinearPanel') NOT NULL COMMENT 'Тип изделия'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `ProfileType` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `type` VARCHAR(50) NOT NULL COMMENT 'Тип профиля'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Profile` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `product_id` INT NOT NULL UNIQUE COMMENT 'Общий ID продукта',
  `profile_type_id` INT NOT NULL COMMENT 'Айди типа профиля',
  `length` INT NOT NULL COMMENT 'Длина профиля',
  FOREIGN KEY (`profile_type_id`) REFERENCES `ProfileType`(`id`),
  FOREIGN KEY (`product_id`) REFERENCES `Product`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Klamer` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `product_id` INT NOT NULL UNIQUE COMMENT 'Общий ID продукта',
  `type` VARCHAR(50) NOT NULL COMMENT 'Тип клямера',
  FOREIGN KEY (`product_id`) REFERENCES `Product`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Bracket` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `product_id` INT NOT NULL UNIQUE COMMENT 'Общий ID продукта',
  `width` INT NOT NULL COMMENT 'Ширина кронштейна',
  `length` INT NOT NULL COMMENT 'Длина кронштейна',
  `thickness` INT NOT NULL COMMENT 'Толщина кронштейна',
  FOREIGN KEY (`product_id`) REFERENCES `Product`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `ExtensionBracket` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `product_id` INT NOT NULL UNIQUE COMMENT 'Общий ID продукта',
  `width` INT NOT NULL COMMENT 'Ширина уд. кронштейна',
  `length` INT NOT NULL COMMENT 'Длина уд. кронштейна',
  `heel` BOOLEAN NOT NULL COMMENT 'Нужна ли пятка',
  FOREIGN KEY (`product_id`) REFERENCES `Product`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `CassetteType` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(50) NOT NULL COMMENT 'Тип кассет'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Cassette` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `product_id` INT NOT NULL UNIQUE COMMENT 'Общий ID продукта',
  `cassette_type_id` INT NOT NULL COMMENT 'Тип кассет',
  FOREIGN KEY (`cassette_type_id`) REFERENCES `CassetteType`(`id`),
  FOREIGN KEY (`product_id`) REFERENCES `Product`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `LinearPanel` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `product_id` INT NOT NULL UNIQUE COMMENT 'Общий ID продукта',
  `field` INT NOT NULL COMMENT 'Лицевая',
  `rust` INT NOT NULL COMMENT 'Руст',
  `length` INT NOT NULL COMMENT 'Длина',
  `butt_end` BOOLEAN NOT NULL COMMENT 'Закрытый торец',
  FOREIGN KEY (`product_id`) REFERENCES `Product`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Material` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `form` INT NOT NULL COMMENT 'Айди формы',
  `type` INT NOT NULL COMMENT 'Айди типа',
  `thickness` INT NOT NULL COMMENT 'Айди толщины',
  `color` INT NOT NULL COMMENT 'Айди цвета',
  `painting` TINYINT(1) NOT NULL COMMENT 'Красится',
  PRIMARY KEY (`id`)
  FOREIGN KEY (`form`) REFERENCES `MaterialForm`(`id`),
  FOREIGN KEY (`type`) REFERENCES `MaterialType`(`id`),
  FOREIGN KEY (`thickness`) REFERENCES `MaterialTickness`(`id`),
  FOREIGN KEY (`color`) REFERENCES `MaterialColor`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `MaterialForm` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `type` VARCHAR(50) NOT NULL COMMENT 'Тип материала',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `MaterialType` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `type` VARCHAR(50) NOT NULL COMMENT 'Тип металла',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `MaterialThickness` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `type` VARCHAR(50) NOT NULL COMMENT 'Толщина',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `MaterialColor` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL COMMENT 'Цвет',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Urgency` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL COMMENT 'Срочность',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Status` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL COMMENT 'Статус',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Sheets` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `width` INT NOT NULL COMMENT 'Ширина',
  `length` INT NOT NULL COMMENT 'Длина',
  `quantity` INT NOT NULL COMMENT 'Количество',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`width`) REFERENCES `SheetWidth`(`id`),
  FOREIGN KEY (`length`) REFERENCES `SheetLength`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `SheetWidth` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `width` INT NOT NULL COMMENT 'Ширина',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `SheetLength` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `length` INT NOT NULL COMMENT 'Длина',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Files` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `file_name` VARCHAR(255) NOT NULL COMMENT 'Имя файла',
  `file_path` TEXT NOT NULL COMMENT 'Путь',
  `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Удалён',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Comment` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `task` INT NOT NULL COMMENT 'Айди задачи',
  `user` INT NOT NULL COMMENT 'Айди юзера',
  `read` TINYINT(1) NOT NULL COMMENT 'Прочитано',
  `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Удалено',
  PRIMARY KEY (`id`)
  FOREIGN KEY (`task`) REFERENCES `Task`(`id`),
  FOREIGN KEY (`user`) REFERENCES `Users`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
