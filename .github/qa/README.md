# QA cost policy

Heavy browser suites should not run on every pull request commit.

- Live domain smoke: main pushes or manual dispatch.
- Mobile layout QA: main pushes or manual dispatch.
- Lighthouse/accessibility: main pushes or manual dispatch.
- Prelaunch parity: manual dispatch only.
- Content-list audit remains path-filtered because it is cheap and narrowly scoped.

For active visual-design branches, use dedicated checkpoint trigger files so screenshots and browser QA are run intentionally rather than on every CSS/JS change.
