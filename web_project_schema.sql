-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema web_project
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema web_project
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `web_project` DEFAULT CHARACTER SET latin1 ;
USE `web_project` ;

-- -----------------------------------------------------
-- Table `web_project`.`categories`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `web_project`.`categories` (
  `idcategories` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `description` VARCHAR(45) NOT NULL,
  `is_private` TINYINT(4) NOT NULL DEFAULT 0,
  `date_updated` DATE NOT NULL,
  `date_created` DATE NOT NULL,
  PRIMARY KEY (`idcategories`),
  UNIQUE INDEX `idcategories_UNIQUE` (`idcategories` ASC) VISIBLE,
  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `web_project`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `web_project`.`users` (
  `idusers` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `email` VARCHAR(45) NOT NULL,
  `password_hash` VARCHAR(45) NOT NULL,
  `role` VARCHAR(45) NOT NULL,
  `date_created` DATE NOT NULL,
  `bio` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idusers`),
  UNIQUE INDEX `idusers_UNIQUE` (`idusers` ASC) VISIBLE,
  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE,
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE,
  UNIQUE INDEX `password_hash_UNIQUE` (`password_hash` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `web_project`.`threads`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `web_project`.`threads` (
  `idtopics` INT(11) NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(45) NOT NULL,
  `content` VARCHAR(45) NOT NULL,
  `is_locked` TINYINT(4) NOT NULL DEFAULT 0,
  `created_at` DATE NOT NULL,
  `updated_at` DATE NOT NULL,
  `changes` VARCHAR(45) NOT NULL,
  `users_idusers1` INT(11) NOT NULL,
  `categories_idcategories` INT(11) NOT NULL,
  PRIMARY KEY (`idtopics`, `users_idusers1`, `categories_idcategories`),
  UNIQUE INDEX `idtopics_UNIQUE` (`idtopics` ASC) VISIBLE,
  INDEX `fk_threads_users1_idx` (`users_idusers1` ASC) VISIBLE,
  INDEX `fk_threads_categories1_idx` (`categories_idcategories` ASC) VISIBLE,
  CONSTRAINT `fk_threads_categories1`
    FOREIGN KEY (`categories_idcategories`)
    REFERENCES `web_project`.`categories` (`idcategories`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_threads_users1`
    FOREIGN KEY (`users_idusers1`)
    REFERENCES `web_project`.`users` (`idusers`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `web_project`.`comments`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `web_project`.`comments` (
  `idcomments` INT(11) NOT NULL AUTO_INCREMENT,
  `content` VARCHAR(45) NOT NULL,
  `upvotes` INT(11) NULL DEFAULT 0,
  `downvotes` INT(11) NULL DEFAULT 0,
  `created_at` DATE NOT NULL,
  `updated_at` DATE NOT NULL,
  `threads_idtopics` INT(11) NOT NULL,
  `threads_users_idusers1` INT(11) NOT NULL,
  `users_idusers` INT(11) NOT NULL,
  PRIMARY KEY (`idcomments`, `threads_idtopics`, `threads_users_idusers1`, `users_idusers`),
  UNIQUE INDEX `idcomments_UNIQUE` (`idcomments` ASC) VISIBLE,
  INDEX `fk_comments_threads1_idx` (`threads_idtopics` ASC, `threads_users_idusers1` ASC) VISIBLE,
  INDEX `fk_comments_users1_idx` (`users_idusers` ASC) VISIBLE,
  CONSTRAINT `fk_comments_threads1`
    FOREIGN KEY (`threads_idtopics` , `threads_users_idusers1`)
    REFERENCES `web_project`.`threads` (`idtopics` , `users_idusers1`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_comments_users1`
    FOREIGN KEY (`users_idusers`)
    REFERENCES `web_project`.`users` (`idusers`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `web_project`.`messages`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `web_project`.`messages` (
  `idmessages` INT(11) NOT NULL AUTO_INCREMENT,
  `text` VARCHAR(45) NULL DEFAULT NULL,
  `sent` DATE NOT NULL,
  `edited` DATE NOT NULL,
  `sender_id` INT(11) NOT NULL,
  `receiver_id` INT(11) NOT NULL,
  PRIMARY KEY (`idmessages`, `sender_id`, `receiver_id`),
  UNIQUE INDEX `idmessages_UNIQUE` (`idmessages` ASC) VISIBLE,
  UNIQUE INDEX `sender_id_UNIQUE` (`sender_id` ASC) VISIBLE,
  UNIQUE INDEX `receiver_id_UNIQUE` (`receiver_id` ASC) VISIBLE,
  INDEX `fk_messages_users1_idx` (`sender_id` ASC) VISIBLE,
  INDEX `fk_messages_users2_idx` (`receiver_id` ASC) VISIBLE,
  CONSTRAINT `fk_messages_users1`
    FOREIGN KEY (`sender_id`)
    REFERENCES `web_project`.`users` (`idusers`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_messages_users2`
    FOREIGN KEY (`receiver_id`)
    REFERENCES `web_project`.`users` (`idusers`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
