CREATE TABLE `stations` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`type` TEXT,
	`version` INT,
	`obj` blob,
	`has_monitor` BINARY NOT NULL,
	`monitor_id` double NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `subjects` (
	`id` int NOT NULL AUTO_INCREMENT,
	`alt_id` TEXT,
	`species_id` bigint NOT NULL,
	`gender` TEXT NOT NULL,
	`current_protocol` bigint NOT NULL,
	`current_stepnum` INT NOT NULL,
	`encrypt_data` BINARY NOT NULL,
	`obj` blob,
	PRIMARY KEY (`id`)
);

CREATE TABLE `assignments` (
	`assign_num` int NOT NULL AUTO_INCREMENT,
	`subject_id` INT NOT NULL AUTO_INCREMENT,
	`station_id` INT NOT NULL AUTO_INCREMENT,
	PRIMARY KEY (`assign_num`)
);

CREATE TABLE `sessions` (
	`session_num` int NOT NULL AUTO_INCREMENT,
	`subject_id` int NOT NULL,
	`station_id` int NOT NULL,
	`start_time` DATETIME NOT NULL,
	`start_mode` varchar NOT NULL,
	`stop_time` DATETIME NOT NULL,
	`protocol_id` int NOT NULL,
	`step_num` INT NOT NULL,
	`trial_num_start` bigint NOT NULL,
	`trial_num_end` bigint NOT NULL,
	`status` varchar NOT NULL,
	`local_store_location` varchar NOT NULL,
	PRIMARY KEY (`session_num`)
);

CREATE TABLE `protocols` (
	`id` int NOT NULL AUTO_INCREMENT,
	`protocol_name` TEXT NOT NULL UNIQUE,
	`version` TEXT NOT NULL,
	`num_steps` INT NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `bcore_changes` (
	`id` int NOT NULL AUTO_INCREMENT,
	`subject_id` bigint NOT NULL,
	`change_id` int NOT NULL,
	`time` DATETIME NOT NULL,
	`change_by` TEXT NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `valid_changes` (
	`id` int NOT NULL AUTO_INCREMENT,
	`description` varchar NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `valid_species_strains` (
	`id` bigint NOT NULL AUTO_INCREMENT,
	`species_name` TEXT NOT NULL,
	`strain_name` TEXT NOT NULL,
	`gene_bkgd` TEXT NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `monitors` (
	`id` int NOT NULL AUTO_INCREMENT,
	`monitor_name` TEXT NOT NULL,
	`monitor_make` TEXT NOT NULL,
	`size_x` double NOT NULL,
	`size_y` double NOT NULL,
	`pixel_x` int NOT NULL,
	`pixel_y` int NOT NULL,
	`calibration` blob NOT NULL,
	`calibration_date` DATETIME NOT NULL,
	PRIMARY KEY (`id`)
);

ALTER TABLE `stations` ADD CONSTRAINT `stations_fk0` FOREIGN KEY (`monitor_id`) REFERENCES `monitors`(`id`);

ALTER TABLE `subjects` ADD CONSTRAINT `subjects_fk0` FOREIGN KEY (`species_id`) REFERENCES `valid_species_strains`(`id`);

ALTER TABLE `subjects` ADD CONSTRAINT `subjects_fk1` FOREIGN KEY (`current_protocol`) REFERENCES `protocols`(`id`);

ALTER TABLE `assignments` ADD CONSTRAINT `assignments_fk0` FOREIGN KEY (`subject_id`) REFERENCES `subjects`(`id`);

ALTER TABLE `assignments` ADD CONSTRAINT `assignments_fk1` FOREIGN KEY (`station_id`) REFERENCES `stations`(`id`);

ALTER TABLE `sessions` ADD CONSTRAINT `sessions_fk0` FOREIGN KEY (`subject_id`) REFERENCES `subjects`(`id`);

ALTER TABLE `sessions` ADD CONSTRAINT `sessions_fk1` FOREIGN KEY (`station_id`) REFERENCES `stations`(`id`);

ALTER TABLE `sessions` ADD CONSTRAINT `sessions_fk2` FOREIGN KEY (`protocol_id`) REFERENCES `protocols`(`id`);

ALTER TABLE `bcore_changes` ADD CONSTRAINT `bcore_changes_fk0` FOREIGN KEY (`subject_id`) REFERENCES `subjects`(`id`);

ALTER TABLE `bcore_changes` ADD CONSTRAINT `bcore_changes_fk1` FOREIGN KEY (`change_id`) REFERENCES `valid_changes`(`id`);