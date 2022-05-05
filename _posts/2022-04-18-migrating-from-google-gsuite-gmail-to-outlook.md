---
layout: post
title: Migrating from Google Gsuite/Gmail to Outlook.com"
categories: []
tags:
 - Google
 - Gmail
 - Outlook
 - Microsoft
 - Email
 - Custom Domain
---

Since [Gsuite (previously Google Apps) is no longer free](https://support.google.com/a/answer/2855120?product_name=UnuFlow&hl=en&visit_id=637858683232001326-3343759727&rd=1&src=supportwidget0&hl=en), and my personal email (nathan.gs) was hosted there I'm looking for alternatives.

After considering several options:

- paying for [Google Workspace](https://workspace.google.com/)
- paying for [Microsoft 365 Business Basic](https://www.microsoft.com/en-us/microsoft-365/business/microsoft-365-business-basic)
- [CloudFlare Email Routing](https://blog.cloudflare.com/email-routing-open-beta/) + consumer email

I decided to settle on _CloudFlare Email Routing_ + Microsoft's [outlook.com](https://outlook.com), part of my [Microsoft 365 Family](https://www.microsoft.com/en-us/microsoft-365/p/microsoft-365-family/cfq7ttc0k5dm/?activetab=pivot:overviewtab) subscription. This includes 100gb of email storage (currently using ~12gb in Gmail). The goal is to maintain both my custom domain(s) as well as my email archive

### Migration Strategy

My migration strategy contains the following TODO's:

1. [Setup outlook.com](#setup-outlook-com) 
2. [Copy emails from Gmail to outlook.com](#copy-emails-from-gmail-to-outlook-com)
3. [Migrating Contacts & Calendar](#migrating-contacts-calendar)
3. Changing service account senders (printer, nas) to [sendgrid.com](https://sendgrid.com/solutions/email-api/smtp-service/)
4. Setup CloudFlare Email Routing

## Setup outlook.com

Since I was already using my personal email on my custom domain as my Microsoft Live ID I already had access to outlook.com; although by default it had a randomly generated email address, luckily in [Outlook.com you can add aliases](https://support.microsoft.com/en-us/office/add-or-remove-an-email-alias-in-outlook-com-459b1989-356d-40fa-a689-8f285b13f1f2).

## Copy emails from Gmail to outlook.com

After evaluating multiple options: 

- Using Google Takeout to download MBox files and then ingesting them into outlook.com 

    Unfortunately this would involve multiple steps
        
    1. Download from Google Takeout
    2. Convert MBOX to PST, likely using a shady commercial tool
    3. Opening the converted in Outlook Desktop and uploading

    This would be a lengthy process.

- Using a Third Party SaaS sync service

    Unfortunately I could not find any, and some concerns about privacy.
- Syncing between Gmail and Outlook IMAP accounts

I decided on the latter and came across [imapsync](https://imapsync.lamiral.info/), which luckily has a [Nix](https://search.nixos.org/packages?channel=21.11&show=imapsync&from=0&size=50&sort=relevance&type=packages&query=imapsync) package (although outdated). I wanted to use a _cli_ approach over just using a regular mail client, due to the process taking multiple days.

### imapsync

Using [Nixos](https://nixos.org) gaining a temporary shell with everything you need is as simple as:

```bash
nix-shell -p imapsync
```

#### Imapsync and Two Factor Authentication

I'm using 2fa with my accounts, luckily both Gmail and Outlook.com have support for app passwords;

- For [Google Accounts](https://support.google.com/accounts/answer/185833?authuser=1)
- For [Microsoft Accounts](https://support.microsoft.com/en-us/account-billing/using-app-passwords-with-apps-that-don-t-support-two-step-verification-5896ed9b-4263-e681-128a-a6f2979a7944)

I put the passwords in 2 files (which I'll delete when I'm done), in `outlook.pw` and in `gmail.pw`.

On another note, for Outlook, use the @outlook.com email address to authenticate, not the one from your custom domain.

The imapsync, FAQs and following blogs were very useful: 

- [https://imapsync.lamiral.info/FAQ.d/FAQ.Gmail.txt](https://imapsync.lamiral.info/FAQ.d/FAQ.Gmail.txt)
- [https://imapsync.lamiral.info/FAQ.d/FAQ.Office365.txt](https://imapsync.lamiral.info/FAQ.d/FAQ.Office365.txt)
- [https://depts.washington.edu/bitblog/2017/09/archiving-transferring-email-with-imapsync/](https://depts.washington.edu/bitblog/2017/09/archiving-transferring-email-with-imapsync/)

#### Copying emails using `imapsync`

```bash
imapsync \
    --host1 imap.gmail.com \
    --ssl1 \
    --user1 $GMAIL_EMAIL \
    --passfile1 gmail.pw \
    --automap \
    --useheader X-Gmail-Received \
    --useheader Message-Id \
    --exclude \[Gmail\]$ \
    --folderlast [Gmail]/All Mail \
    --user2 OUTLOOK_EMAIL \
    --passfile2 outlook.pw \
    --host2 outlook.office365.com \
    --ssl2
```

Optionally you can add `--subfolder2 gmail` to keep it in a seperate mailbox. 

{% include post_img img="imapsync-in-progress.png" alt="Imapsync in progress" %}

If using a mode modern version of imapsync, you can use `--gmail1`. 

Now wait, the sync will take days (mostly due to the [Gmail limits](https://support.google.com/a/answer/1071518?product_name=UnuFlow&hl=en&visit_id=637858154342472551-3444109678&rd=1&src=supportwidget0&hl=en)). 

## Migrating Contacts & Calendar

