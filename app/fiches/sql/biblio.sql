DROP procedure IF EXISTS `strip_slashes`;

DELIMITER $$

CREATE DEFINER=`root`@`localhost` PROCEDURE `strip_slashes`(usingtable varchar(255), usingfield varchar(255))
BEGIN
  # Supprime les slashs
  DECLARE done INT DEFAULT 0;
  SET @slash1 = '\\"';
  SET @repls1 = '"';
  SET @match1 = '%\\\\\"%';
  SET @slash2 = "\\'";
  SET @repls2 = "'";
  SET @match2 = "%\\\\\'%";
  SET @qry = CONCAT("UPDATE ", usingtable," f SET f.", usingfield,"=REPLACE(f.", usingfield,", ?, ?) WHERE f.", usingfield, " LIKE ?");
  PREPARE stmt FROM @qry;
  myloop: LOOP
    IF done THEN LEAVE myloop;
    END IF;
    EXECUTE stmt USING @slash1, @repls1, @match1;
    IF ROW_COUNT() = 0 THEN SET done = 1;
    END IF;
  END LOOP;
  SET done = 0;
  myloop: LOOP
    IF done THEN LEAVE myloop;
    END IF;
    EXECUTE stmt USING @slash2, @repls2, @match2;
    IF ROW_COUNT() = 0 THEN SET done = 1;
    END IF;
  END LOOP;
  DEALLOCATE PREPARE stmt;
END$$

DELIMITER ;

CALL strip_slashes('fiches_biblio', 'publisher');
CALL strip_slashes('fiches_notebiblio', 'text');
CALL strip_slashes('fiches_notemanuscript', 'text');
CALL strip_slashes('fiches_notetranscription', 'text');
