
CREATE database `youku_mobile_user` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
CREATE  TABLE `youku_mobile_user`.`user_home_layout_p1` (
  `ikey` VARCHAR(32) NOT NULL ,
  `value` VARCHAR(50) NULL ,
  PRIMARY KEY (`ikey`) ,
  UNIQUE INDEX `ikey_UNIQUE` (`ikey` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;


CREATE  TABLE `youku_mobile_user`.`user_home_layout_p2` (
  `ikey` VARCHAR(32) NOT NULL ,
  `value` VARCHAR(50) NULL ,
  PRIMARY KEY (`ikey`) ,
  UNIQUE INDEX `ikey_UNIQUE` (`ikey` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

