-- -----------------------------------------------------
-- Schema honeypot
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `noneypot` DEFAULT CHARACTER SET utf8 ;
USE `honeypot` ;

-- -----------------------------------------------------
-- User honeypot
-- -----------------------------------------------------

CREATE USER 'honeypot' IDENTIFIED BY 'D@v1B1aEdu321!@#';
GRANT ALL PRIVILEGES ON honeypot.* TO 'honeypot'; FLUSH PRIVILEGES;

-- -----------------------------------------------------
-- Table `honeypot`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(150) NOT NULL,
  `sobrenome` VARCHAR(150) NOT NULL,
  `username` VARCHAR(50) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `senha` VARCHAR(128) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE,
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE
);
