# granbluev2

A **Granblue Fantasy (GBF) guild-war leaderboard tracker**. During GBF "team raid"
(guild war / 団イベ) events it scrapes ranking data from the game API every 20 minutes,
stores time-series snapshots in Firestore, and serves a read-only dashboard from
Firebase Hosting.

- **Live site:** https://granblue-247222.web.app
- **GCP project:** `granblue-247222` (project number `964139672422`)
- **Region:** `asia-northeast1` (Tokyo) for all compute + Firestore
- **Owner account:** `mail@orbb.li`

## Architecture

```
Cloud Scheduler ──POST .../jobs/cloud-run-crawler:run──▶ Cloud Run JOB ──writes──▶ Firestore
(every 20 min, oauth SA)          (taskCount: 2, parallel)         │                  ▲
                                                                    │            reads │ (public, rules-gated)
                                                                    ▼                  │
                                                              Firebase Hosting ────────┘
                                                              (Vue 2 + AdminLTE3 SPA)
```

The compute is a **Cloud Run _Job_** (batch, runs to completion), **not** a Service.
`gcloud run services list` will therefore show nothing — use `gcloud run jobs list`.

The scheduler doesn't call the app over HTTP; it calls the **Cloud Run Admin API**
`jobs/cloud-run-crawler:run` endpoint with an OAuth token to trigger a job execution.

### Parallel fan-out via task index

The job runs with `taskCount: 2`. Cloud Run injects `CLOUD_RUN_TASK_INDEX` per task,
and `main.py` branches on it so the two crawls run **in parallel** on separate containers:

| `CLOUD_RUN_TASK_INDEX` | Crawl | Source module | Ranks covered |
|---|---|---|---|
| `0` | Personal score borders | `get_personal_border.py` | 2000, then 5000…370000 step 5000 |
| `1` | Crew (guild) rankings | `get_crew.py` | top ~5500 guilds (550 pages) |

## Firestore data model (`(default)` database, Native mode)

| Path | Contents |
|---|---|
| `configs/public_config` | `{ teamraid }` — the active event ID, prefixed onto every game URL |
| `configs/private_config` | `{ cookie, useragent }` — the scraper's game session (secret) |
| `crew/{guildId}` | `{ name, last_updated }` |
| `crew/{guildId}/records/{teamraid}` | `{ records: [ {ranking, point, datetime}, … ] }` (ArrayUnion) |
| `personal_border/{teamraid}` | `{ records: [ {"<rank>": point, …, datetime}, … ] }` (ArrayUnion) |

**Session handling:** `fs_configs.get_configs()` loads the cookie/useragent/teamraid at
startup; `set_cookie()` writes the *refreshed* cookie back in a `finally` block after every
run, keeping the game session alive without baking credentials into the image.

### Security rules (`firebase-firestore_rules`)

Public **read-only**, with one carve-out: everything is world-readable **except**
`private_config` (the cookie), and `crew/**` is fully open. There are **no write rules** —
only the crawler's service account writes, which bypasses rules. Correct posture for a
public leaderboard fed by a trusted backend.

## Layout

```
cloud-run_crawler/       # the scraper (Python), deployed as a Cloud Run Job
  main.py                #   entrypoint; branches on CLOUD_RUN_TASK_INDEX
  fs_configs.py          #   Firestore client + config load / cookie persistence
  gbf_request.py         #   GBF HTTP client (X-VERSION scrape, cookies, retries)
  get_personal_border.py #   task 0 crawl
  get_crew.py            #   task 1 crawl
  requirements.txt
  Procfile
firebase-hosting/        # static dashboard (Vue 2 + AdminLTE3, Firebase SDK 6.3.3)
firebase-firestore_rules # Firestore security rules
firebase.json            # hosting + firestore rules config
.github/workflows/       # CI/CD (see below)
```

## CI/CD (GitHub Actions, Workload Identity Federation — no JSON keys)

Auth uses OIDC (`id-token: write`) against WIF pool
`projects/964139672422/.../providers/github-provider`, impersonating
`github-deployer@granblue-247222.iam.gserviceaccount.com`.

| Workflow | Trigger | Action |
|---|---|---|
| `deploy-job-crawler.yml` | push to `main` touching `cloud-run_crawler/**` | build image → Artifact Registry `my-docker-repo`, deploy Cloud Run Job |
| `deploy-scheduler-crawler.yml` | push touching that file only | create/update the Cloud Scheduler job |
| `firebase-hosting-merge.yml` | push to `main` touching hosting | deploy hosting to `live` channel |
| `firebase-hosting-pull-request.yml` | PR | deploy hosting to a preview channel |

## Service accounts

| SA | Role |
|---|---|
| `github-deployer@` | CI deployer (impersonated via WIF) |
| `crawling-service-account@` | identity the Cloud Run Job runs as (writes Firestore) |
| `cloud-run-invoker@` | identity the Scheduler uses to invoke the job |

## Operations

```bash
gcloud config set project granblue-247222      # ensure you're on mail@orbb.li

# Scheduler (currently PAUSED between events — this is normal)
gcloud scheduler jobs resume  cloud-run-crawler-scheduler-trigger --location=asia-northeast1
gcloud scheduler jobs pause   cloud-run-crawler-scheduler-trigger --location=asia-northeast1

# Manual one-off crawl
gcloud run jobs execute cloud-run-crawler --region=asia-northeast1

# Logs from the last execution
gcloud run jobs executions list --job=cloud-run-crawler --region=asia-northeast1
```

Before an event: set `configs/public_config.teamraid` to the new event ID and refresh
`configs/private_config` (`cookie`, `useragent`) from a logged-in browser session, then
resume the scheduler. After the event: pause it again.

## Known drift / gotchas

- **Scheduler name mismatch:** the live scheduler is `cloud-run-crawler-scheduler-trigger`,
  but `deploy-scheduler-crawler.yml` would create one named `collection-crawler`. The live
  one was created out-of-band; running that workflow would make a *second*, duplicate job.
- **Paused = no data:** if the dashboard looks stale, the scheduler is almost certainly
  paused (expected when no guild war is running).
- **`get_personal_border.py` error handler** calls `json.dump(...)` instead of `json.dumps(...)`;
  on a crawl error it throws a `TypeError` that masks the real error. Left as-is (works in the
  happy path) — fix only if it starts biting.
