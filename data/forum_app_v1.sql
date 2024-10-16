SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema forum
-- -----------------------------------------------------

CREATE SCHEMA IF NOT EXISTS `forum` DEFAULT CHARACTER SET latin1 ;
USE `forum` ;

-- -----------------------------------------------------
-- Table `forum`.`categories`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `forum`.`categories` (
  `category_id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `is_locked` TINYINT(2) NOT NULL DEFAULT 0,
  `is_private` TINYINT(2) NOT NULL DEFAULT 0,
  PRIMARY KEY (`category_id`),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `forum`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `forum`.`users` (
  `user_id` INT(11) NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(45) NOT NULL,
  `password` VARCHAR(200) NOT NULL,
  `email` VARCHAR(45) NOT NULL,
  `first_name` VARCHAR(45) NULL DEFAULT NULL,
  `last_name` VARCHAR(45) NULL DEFAULT NULL,
  `is_admin` TINYINT(2) NOT NULL DEFAULT 0,
  `is_deleted` TINYINT(2) NOT NULL DEFAULT 0,
  PRIMARY KEY (`user_id`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE,
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;

-- -----------------------------------------------------
-- Table `forum`.`messages`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `forum`.`messages` (
  `message_id` INT(11) NOT NULL AUTO_INCREMENT,
  `text` MEDIUMTEXT NOT NULL,
  `sender_id` INT(11) NOT NULL,
  `receiver_id` INT(11) NOT NULL,
  PRIMARY KEY (`message_id`),
  INDEX `fk_messages_users1_idx` (`sender_id` ASC) VISIBLE,
  INDEX `fk_messages_users2_idx` (`receiver_id` ASC) VISIBLE,
  CONSTRAINT `fk_messages_users1`
    FOREIGN KEY (`sender_id`)
    REFERENCES `forum`.`users` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_messages_users2`
    FOREIGN KEY (`receiver_id`)
    REFERENCES `forum`.`users` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `forum`.`topics`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `forum`.`topics` (
  `topic_id` INT(11) NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(45) NOT NULL,
  `user_id` INT(11) NOT NULL,
  `is_locked` TINYINT(2) NOT NULL DEFAULT 0,
  `best_reply_id` INT(11) NULL DEFAULT NULL,
  `category_id` INT(11) NOT NULL,
  PRIMARY KEY (`topic_id`),
  INDEX `fk_topics_users1_idx` (`user_id` ASC) VISIBLE,
  INDEX `fk_topics_replies1_idx` (`best_reply_id` ASC) VISIBLE,
  INDEX `fk_topics_categories1_idx` (`category_id` ASC) VISIBLE,
  CONSTRAINT `fk_topics_categories1`
    FOREIGN KEY (`category_id`)
    REFERENCES `forum`.`categories` (`category_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_topics_replies1`
    FOREIGN KEY (`best_reply_id`)
    REFERENCES `forum`.`replies` (`reply_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_topics_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `forum`.`users` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `forum`.`replies`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `forum`.`replies` (
  `reply_id` INT(11) NOT NULL AUTO_INCREMENT,
  `text` TEXT NOT NULL,
  `user_id` INT(11) NOT NULL,
  `topic_id` INT(11) NOT NULL,
  `edited` TINYINT(2) NOT NULL DEFAULT 0,
  PRIMARY KEY (`reply_id`),
  INDEX `fk_replies_users1_idx` (`user_id` ASC) VISIBLE,
  INDEX `fk_replies_topics1_idx` (`topic_id` ASC) VISIBLE,
  CONSTRAINT `fk_replies_topics1`
    FOREIGN KEY (`topic_id`)
    REFERENCES `forum`.`topics` (`topic_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_replies_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `forum`.`users` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `forum`.`users_categories_permissions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `forum`.`users_categories_permissions` (
  `user_id` INT(11) NOT NULL,
  `category_id` INT(11) NOT NULL,
  `write_access` TINYINT(4) NOT NULL DEFAULT 0,
  PRIMARY KEY (`user_id`, `category_id`),
  INDEX `fk_users_has_categories_categories1_idx` (`category_id` ASC) VISIBLE,
  INDEX `fk_users_has_categories_users1_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_users_has_categories_categories1`
    FOREIGN KEY (`category_id`)
    REFERENCES `forum`.`categories` (`category_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_users_has_categories_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `forum`.`users` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;

-- -----------------------------------------------------
-- Table `forum`.`votes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `forum`.`votes` (
  `user_id` INT(11) NOT NULL,
  `reply_id` INT(11) NOT NULL,
  `type` TINYINT(2) NOT NULL,
  PRIMARY KEY (`user_id`, `reply_id`),
  INDEX `fk_votes_users1_idx` (`user_id` ASC) VISIBLE,
  INDEX `fk_votes_replies1_idx` (`reply_id` ASC) VISIBLE,
  CONSTRAINT `fk_votes_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `forum`.`users` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;

USE `forum`;
DELIMITER $$
USE `forum`$$
CREATE
DEFINER=`root`@`localhost`
TRIGGER `forum`.`after_user_deleted_delete_his_messages_and_permissions`
AFTER UPDATE ON `forum`.`users`
FOR EACH ROW
BEGIN
  IF NEW.is_deleted = 1 THEN
    DELETE FROM messages
    WHERE sender_id = OLD.user_id OR receiver_id = OLD.user_id;
    DELETE FROM users_categories_permissions
    WHERE user_id = OLD.user_id;
  END IF;
END$$
DELIMITER ;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;