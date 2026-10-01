# summit-tracker

GitHub Action that watches https://summit.microsoft.com/en-us/ every ~15 minutes.

- **Registration open issue** (label `registration-open`, created once): the text
  "Registration coming soon." disappeared, or a link/button/element mentioning "register" appeared.
- **Page changed issue** (label `page-changed`): any change to the page's visible text or links,
  with a diff. The new state is committed to `snapshot.txt`, so each issue shows only the latest change.

Run manually from the Actions tab (`workflow_dispatch`). GitHub disables scheduled workflows after
60 days without repo activity; page-change commits count as activity, but re-enable if it ever stops.
Enable GitHub notifications for issues to get emailed.
