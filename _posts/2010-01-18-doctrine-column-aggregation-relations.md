---
layout: post
title: 'Doctrine Column Aggregation & Relations'
categories: 
excerpt: >
    Solving a SQL STATE access violation error, when generating doctrine table structures.
tags: 
- Web Development
- PHP
redirect_from: 
  - /post/340691908/doctrine-column-aggregation-relations    
---

Suppose we have this structure:

```yaml
Person:
  columns:
    name: string(63)

Professor:
  inheritance:
    extends: Person
    type: column_aggregation
    keyField: type
    keyValue: professor
  columns:
    faculty_id: integer(10)
  relations:
    Faculty:

Student:
  inheritance:
    extends: Person
    type: column_aggregation
    keyField: type
    keyValue: student
```

When you run the `symfony:build —all` task you get a really annoying error:
```sql
SQLSTATE[42000]: Syntax error or access violation: 1072 Key column ‘faculty_id’ doesn’t exist in table. 

Failing Query: 
“CREATE TABLE person (
    id BIGINT AUTO_INCREMENT, 
    name VARCHAR(63), 
    type VARCHAR(31), 
    INDEX faculty_id_idx (faculty_id), 
    PRIMARY KEY(id)) ENGINE = INNODB”.
```

The problem: the Doctrine CLI task tries to insert multiple CREATE TABLE queries (one for each child + for the parent).

Luckily you can circumvent this behavior by calling (in the setUp method):
```php
$this->setAttribute(Doctrine_Core::ATTR_EXPORT, Doctrine_Core::EXPORT_NONE);
```