create database if not exists dascrapy;
use dascrapy;

create table deviants(
    id int auto_increment primary key,
    username varchar(80),
    joined_on date);

create unique index username_idx on deviants(username);

create table urls(
    id int auto_increment primary key,
    data varchar(2048),
    urlDate date,
    urlType enum("profile","journal","deviation"),
    global_inc bigint,
    deviant_id int,
    foreign key urlDeviant_idx (deviant_id) references deviants(id));

create or replace index type_increment_idx on urls(urlType, global_inc);

create table comments_deviations(
    id int auto_increment primary key,
    data text,
    url_id int,
    foreign key urlDeviation_idx (url_id) references urls(id));
    
create fulltext index comment_data_idx on comments_deviations(data);
