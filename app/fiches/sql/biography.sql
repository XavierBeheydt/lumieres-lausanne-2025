DROP VIEW IF EXISTS `fiches_placeview`;
CREATE OR REPLACE VIEW `fiches_placeview` AS 
    select `fiches_biography`.`birth_place` AS `place` from `fiches_biography` where (`fiches_biography`.`birth_place` <> _latin1'') 
    union select `fiches_biography`.`death_place` AS `place` from `fiches_biography` where (`fiches_biography`.`death_place` <> _latin1'') 
    union select `fiches_biography`.`origin` AS `place` from `fiches_biography` where (`fiches_biography`.`origin` <> _latin1'') 
    union select `fiches_profession`.`place` AS `place` from `fiches_profession` where (`fiches_profession`.`place` <> _latin1'');


DROP VIEW IF EXISTS `fiches_biblioreferences`;
CREATE OR REPLACE ALGORITHM=UNDEFINED VIEW `fiches_biblioreferences` AS (
    SELECT
        `b`.`id` AS `id`,
        `b`.`title` AS `title`,
        `b`.`litterature_type` AS `litterature_type`,
        `b`.`document_type_id`AS `document_type_id`,
        `b`.`publisher` AS `publisher`,
        `b`.`date` AS `date`,
        `b`.`date_f` AS `date_f`,
        `b`.`pages` AS `pages`,
        group_concat(`p`.`name` order by `c`.`id` ASC separator '|') AS `authors`,
        group_concat(cast(`p`.`id` as char(32) charset utf8) order by `c`.`id` ASC separator ',') AS `authors_id`,
        count(distinct `p`.`name`) AS `nb_authors` 
    FROM (
             `fiches_biblio` `b` 
             LEFT JOIN `fiches_contributiondoc` `c` ON ( (`c`.`document_id` = `b`.`id`) AND (`c`.`contribution_type_id` = 1) )
             LEFT JOIN `fiches_person` `p` ON (`p`.`id` = `c`.`person_id`)
             LEFT JOIN `fiches_biography` `bio` ON (`bio`.`person_id` = `p`.`id`)
         ) 
    GROUP BY `b`.`id`
);


#DROP VIEW IF EXISTS `fiches_manuscriptreferences`;
#CREATE OR REPLACE ALGORITHM=UNDEFINED VIEW `fiches_manuscriptreferences` AS (
#    SELECT
#        `m`.`id` AS `id`,
#        `m`.`id` AS `manuscript_id`,
#        `m`.`title` AS `title`,
#        `m`.`date` AS `date`,
#        group_concat(distinct `p`.`name` order by `c`.`id` ASC separator '|') AS `authors`,
#        group_concat(cast(`p`.`id` as char(32) charset utf8) order by `c`.`id` ASC separator ',') AS `authors_id`,
#        count(distinct `p`.`name`) AS `nb_authors` 
#    FROM (
#             `fiches_manuscript` `m` 
#             LEFT JOIN `fiches_contributionman` `c` ON ( (`c`.`document_id` = `m`.`id`) AND (`c`.`contribution_type_id` = 1) )
#             LEFT JOIN `fiches_person` `p` ON (`p`.`id` = `c`.`person_id`)
#             LEFT JOIN `fiches_biography` `bio` ON (`bio`.`person_id` = `p`.`id`)
#         ) 
#    GROUP BY `m`.`id`
#);
