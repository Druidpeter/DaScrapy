create database if not exists dascrapy;
use dascrapy;

create table deviants(
    id int auto_increment primary key,
    username varchar(80),
    joined_on date);

create table devCtrlStats(
    id int auto_increment primary key,
    deviant_id int,
    foreign key ctrlDeviants (deviant_id) references deviants(id),
    lastGalleryFetch timestamp default '0000-00-00 00:00:00');

create table urlCtrlStats(
    id int auto_increment primary key,
    url_id int,
    foreign key ctrlUrls (url_id) references urls(id),
    lastCommentFetch timestamp default '0000-00-00 00:00:00');

create unique index username_idx on deviants(username);

create table urls(
    id int auto_increment primary key,
    data varchar(2048),
    urlDate date,
    urlType enum("profile","journal","deviation"),
    global_inc bigint,
    deviant_id int,
    foreign key urlDeviant_idx (deviant_id) references deviants(id));

-- Need to alter table urls to add "last_cmnt_proc" field, which stores
-- the last time the url was visited to check for comments.
-- We check a particular url for comments if the last check was more
-- than 6 months ago.

alter table urls add column last_cmnt_proc
      timestamp default '0000-00-00 00:00:00';

create table util(
       data int,
       tm_stmp timestamp default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP);

create or replace index type_increment_idx on urls(urlType, global_inc);

create table comments(
    id int auto_increment primary key,
    data text,
    url_id int, -- The deviation the comment was made on.
    commentDate date,
    deviant_id int,
    global_inc int,
    href varchar(2048),
    foreign key cmntDeviant_idx (deviant_id) references deviants(id),
    foreign key cmntDeviation_idx (url_id) references urls(id));
    
create fulltext index comment_data_idx on comments(data);

