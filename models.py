#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from spyne import ComplexModel
from spyne import Date, DateTime, Int, String


class UserModel(ComplexModel):
    user_id       = Int
    username      = String
    nickname      = String
    password      = String
    first_name    = String
    last_name     = String
    email_address = String
    phone_number  = String
    session_id    = String
    expire_time   = DateTime


class JournalModel(ComplexModel):
    journal_id = Int
    name       = String
    language   = String
    history    = String
    host       = String
    publisher  = String
    used_name  = String
    frequency  = String
    issn       = String
    cn         = String
    pdc        = String


class SubscriptionModel(ComplexModel):
    subscription_id = Int
    journal_id      = Int
    year            = Int


class StorageModel(ComplexModel):
    storage_id = Int
    journal_id = Int
    year       = Int
    volume     = Int
    issue      = Int


class ArticleModel(ComplexModel):
    article_id  = Int
    storage_id  = Int
    page_number = Int
    title       = String
    author      = String
    content     = String
    keyword1    = String
    keyword2    = String
    keyword3    = String
    keyword4    = String
    keyword5    = String


class BorrowingModel(ComplexModel):
    borrowing_id = Int
    user_id      = Int
    storage_id   = Int
    borrow_date  = Date
    agreed_date  = Date
    return_date  = Date
