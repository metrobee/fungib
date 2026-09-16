# Coding Guidelines for AI Agents Working on These Projects

This file exists because a security and code-health audit on 2026-09-15/16
found real, live problems across nearly every project in this workspace:
live bank balances and IBANs sitting fully public with zero authentication,
a fieldwork app where the "approved users" gate was enforced client-side
only (meaning any Google account could write/delete shared data), a security
hardening pass that silently broke five active tools because nobody checked
what depended on the paths being tightened, and three separate projects
where the live-deployed checkout and the git-tracked checkout had drifted
apart — meaning a fix made in one place didn't exist anywhere else, and a
stray deploy from the wrong directory could silently undo real fixes.

None of this was exotic. It was avoidable with a few consistent habits.
Follow these rules on every project in this workspace, not just the one
you're currently focused on.

## 1. Security: deny by default, verify with real requests

- **Every new database node, collection, or storage path starts closed**
  (`.read: false, .write: false` or equivalent). Open it only for the
  specific access pattern you actually need, as narrowly as you can.
- **A login screen in the UI is not security.** Firebase Hosting (and any
  static file server) cannot enforce authentication on static files —
  `photos.json`, `observations.json`, exported `.js`/`.json` data dumps,
  etc. are fetchable directly by anyone with the URL regardless of what the
  page's JavaScript does. If data needs to be gated, it must live behind a
  mechanism that actually checks the request (Realtime Database / Firestore
  Security Rules, or a server-side function that verifies an ID token) —
  never behind "the app hides the button until you log in."
- **"Any authenticated user" is usually not the right bar.** If there's an
  approved-users list, an admin-only flag, or a specific owner email, the
  *rule itself* must check that — not just `auth != null`. A rule that
  says "any Google account" is exactly as open as "no auth" to anyone
  willing to create one.
- **Never trust a rules file without checking the live, deployed state.**
  Rules files can drift from what's actually deployed (see #3). After any
  security-relevant change, verify with an actual unauthenticated
  `curl <path>.json` (or equivalent) against the live endpoint — don't just
  read the code and assume it matches production.
- **No credentials, tokens, or API keys with real access belong in
  client-side code or in files served publicly.** Firebase web API keys
  are the one common exception (they're not secret by Firebase's own
  design — the Security Rules are the real gate), but service account
  keys, OAuth client secrets, and admin tokens never belong in anything
  that ships to a browser or a public static file.

## 2. Before tightening security, check what actually depends on it being open

Before you flip an open rule to closed (or restructure access control),
find every real consumer of that path first — grep the whole workspace,
not just the one file you're editing. A hardening pass that doesn't do
this will silently break live features, and unless something surfaces an
error the user actually sees, nobody will notice until much later. If you
can't find why something was open, that's a reason to investigate, not a
reason to assume it's safe to close.

## 3. Deploys: know exactly what you're about to overwrite

- **Before any `deploy` command, confirm you're in the right directory for
  the right project.** Print/check the working directory and the project
  config (`.firebaserc`, or equivalent) and make sure they match your
  intent. Never deploy with an explicit `--project` flag as a way to
  "correct" being in the wrong directory — that's exactly how a different
  app's files end up overwriting a live production site.
- **If more than one local directory could plausibly deploy to the same
  project, that's a live hazard, not a curiosity.** Either delete/archive
  the redundant one, or rename it unambiguously (e.g. `_OLD_DO_NOT_DEPLOY`)
  so nobody `cd`s into it from muscle memory. Don't leave two copies of a
  `firebase.json`/`database.rules.json` pointed at the same project unless
  they are verified byte-identical, and re-verify that after every change.
- **A failed deploy must fail loudly.** Never catch a deploy error and
  just print a warning while letting the script/process exit 0 — that is
  exactly how a broken deploy pipeline goes unnoticed. Propagate the
  failure (non-zero exit, thrown error, whatever the caller will actually
  see).

## 4. Keep the deployed checkout and the git-tracked checkout the same thing

If a project has a "real" git repository and a separate directory that
actually gets deployed (by a cron job, a CLI tool, a LaunchAgent, etc.),
treat that as a problem to fix, not a fact of life. At minimum:
- Any fix made in the deploying checkout gets committed and pushed to the
  real repo in the same session — don't leave it uncommitted "for later."
- The security rules file and the code that runs the deploy should live
  in the same place, or be kept explicitly synced (diffed and copied)
  every time either changes.

## 5. Verify claims, don't assert them

- Don't say something is fixed, exposed, safe, or broken based on reading
  code alone when you can check the live, actual behavior instead — a
  real `curl`, a real test run, a real look at what's deployed. Reading
  code tells you intent; checking the live system tells you truth, and
  they are not always the same file.
- If a repository has an existing test suite, run it before and after
  your change, and read it before assuming you know what "correct" means
  — one of tonight's fixes turned out to already be described, exactly,
  in a test file nobody had wired the actual config up to satisfy.
- When you're not sure whether something is actually a problem, say so
  explicitly rather than guessing confidently in either direction.

## 6. Scope and hygiene

- Fix the bug you're asked to fix. Don't refactor, add abstractions, or
  build speculative flexibility nobody asked for alongside it.
- Don't leave dead code that looks like it's supposed to run (a "live
  listener" block guarded by a check that's always false because the SDK
  was never loaded is worse than no code at all — it looks like a feature
  that exists and doesn't).
- Comments should explain *why*, not *what* — and only when the reasoning
  isn't obvious from the code itself.
- When you fix something, update whatever incident/changelog convention
  the project already uses (check for `INCIDENTS.md`, `PROMISES.md`,
  `AGENTS.md`, `.kiro/steering/`, etc. before assuming there isn't one) —
  and only mark something resolved after you've actually verified it, not
  after you've made a change you believe should have fixed it.

## 7. When in doubt

Ask, rather than guess, when: the fix requires touching production data
irreversibly; you're not sure whether a workflow is still actively relied
on right now; or closing an access gap would break something and you
don't yet know what the intended replacement behavior should be. Getting
the user's five-second confirmation is always cheaper than a silent
regression discovered days later.
