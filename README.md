# summit-tracker

GitHub Action that watches https://summit.microsoft.com/en-us/ for MVP Summit registration opening.

**Status: suspended.** 2027 registration opened on 2026-10-29 (issue #1), so the 15-minute schedule is
turned off. The workflow can still be run manually from the Actions tab (`workflow_dispatch`).

## What it looks for

Registration is considered open when any of these appear (all were observed on the live 2026 page):

- the text "Registration coming soon." is gone
- the intro changes from "The next MVP Summit will take place ..." to "This year's event takes place ..."
- a `Register` link/button (here `/en-us/register`), or any element whose text, href or id mentions "register"

A `Sign In` link (`/en-us/auth/sign-in`) also appeared at the same time; it is listed in the issue as a
supporting signal but does not trigger the alert on its own.

## Issues

- **Registration open** (label `registration-open`): created once per calendar year.
- **Page changed** (label `page-changed`): any change to the page's visible text or links, with a diff. The
  new state is committed to `snapshot.txt`, so each issue shows only the latest change.

Enable GitHub notifications for issues to get emailed.

## Resuming next cycle (around September 2027)

1. In `.github/workflows/check-summit.yml`, uncomment the `schedule:` block and remove the SUSPENDED note.
2. Check the page. `snapshot.txt` still holds the 2026 "registration open" state, so if last year's page is
   still up the first run will report "registration open"; close that issue and carry on.
3. GitHub disables scheduled workflows after 60 days without repo activity; page-change commits count as
   activity, but re-enable if it ever stops.
