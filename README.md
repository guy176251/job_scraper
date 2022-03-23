# Job Application Helper

This is my own personal job application helper that I made to aid me in applying and keeping up with a lot of jobs.

Often, I find myself wanting to keep track of all the jobs I've applied for, in addition to tailoring my resume to each job. This results in me having to keep track of various text files and lots of manual clicking and other bothersome things. I figured, why not make an app to help me with this process?

## Pictures

![List view](/docs/images/main-view.png)
![Detail view - top](/docs/images/detail-top.png)
![Detail view - middle](/docs/images/detail-middle.png)
![Detail view - bottom](/docs/images/detail-bottom.png)

## Custom Django Management Commands

### `scrape_jobs`

Scrapes various websites for job links, makes calls to job API to grab job information, stores the info in the database, then applies various information processing to said jobs.

### `process_jobs`

Applies various information processing to said jobs.

### `restore_jobs`

Restores job database from backup, then processes them.
