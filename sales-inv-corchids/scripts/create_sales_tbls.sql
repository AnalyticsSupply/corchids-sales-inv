-- ---
-- Globals
-- ---


DROP TABLE IF EXISTS `plant_reserves`;
DROP TABLE IF EXISTS `date_week`;
DROP TABLE IF EXISTS `plant_supplies`;
DROP TABLE IF EXISTS `plant_summary`;
DROP TABLE IF EXISTS `weeks`;		


-- SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
-- SET FOREIGN_KEY_CHECKS=0;

-- ---
-- Table 'plant_reserves'
-- Table for plant reserves
-- ---
		
CREATE TABLE `plant_reserves` (
  `id` BIGINT NOT NULL,
  `plant` VARCHAR(40) NOT NULL,
  `product` VARCHAR(40) NULL,
  `plant_id` BIGINT NOT NULL,
  `product_id` BIGINT NOT NULL,
  `num_reserved` INTEGER NOT NULL,
  `week_id` BIGINT NOT NULL,
  `customer` VARCHAR(100) NOT NULL,
  `customer_id` BIGINT NOT NULL,
  `sales_rep` VARCHAR(100) NOT NULL,
  `add_date` DATE NOT NULL,
  PRIMARY KEY (`id`)
) COMMENT 'Table for plant reserves';



-- ---
-- Table 'date_week'
-- 
-- ---

CREATE TABLE `date_week` (
  `id` BIGINT NOT NULL,
  `date_entry` DATE NOT NULL,
  `week_id` BIGINT NOT NULL,
  PRIMARY KEY (`id`)
);

-- ---
-- Table 'plant_supplies'
-- 
-- ---

CREATE TABLE `plant_supplies` (
  `id` BIGINT NOT NULL,
  `supplier` VARCHAR(100) NOT NULL,
  `supplier_id` BIGINT NOT NULL,
  `forecast` INTEGER NOT NULL,
  `week_id` BIGINT NOT NULL,
  `add_date` DATE NOT NULL,
  `plant` VARCHAR(40) NOT NULL,
  `plant_id` BIGINT NOT NULL,
  PRIMARY KEY (`id`)
);

-- ---
-- Table 'plant_summary'
-- 
-- ---


CREATE TABLE `plant_summary` (
  `id` BIGINT NOT NULL,
  `plant` VARCHAR(40) NOT NULL,
  `plant_id` BIGINT NOT NULL,
  `week_id` BIGINT NOT NULL,
  `num_reserved` INTEGER NOT NULL,
  `forecast` INTEGER NOT NULL,
  `actual` INTEGER NOT NULL,
  PRIMARY KEY (`id`)
);

-- ---
-- Table 'weeks'
-- Weeks in a year
-- ---

		
CREATE TABLE `weeks` (
  `id` BIGINT NOT NULL,
  `week_number` INTEGER NOT NULL,
  `year` INTEGER NOT NULL,
  `monday_date` DATE NOT NULL,
  PRIMARY KEY (`id`)
) COMMENT 'Weeks in a year';

-- ---
-- Foreign Keys 
-- ---

ALTER TABLE `plant_reserves` ADD FOREIGN KEY (week_id) REFERENCES `weeks` (`id`);
ALTER TABLE `date_week` ADD FOREIGN KEY (week_id) REFERENCES `weeks` (`id`);
ALTER TABLE `plant_supplies` ADD FOREIGN KEY (week_id) REFERENCES `weeks` (`id`);
ALTER TABLE `plant_summary` ADD FOREIGN KEY (week_id) REFERENCES `weeks` (`id`);
