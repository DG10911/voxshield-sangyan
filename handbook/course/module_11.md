# MODULE 11 — Scaling, Security and Compliance

A clever demo and a real bank system are two very different animals.

A demo has to impress a few people in a room. A bank system has to survive millions of real calls, stay safe from attackers, and satisfy the law.

This module is about growing up. How VoxShield goes from handling ten calls to handling millions. How we protect the system itself, honestly stating what is built and what is not. And how the whole design fits India's data protection law.

LEARN:
- Why a "stateless" design lets you scale just by adding more servers
- What is real security in VoxShield today, and what is still on the backlog
- How the design lines up with India's DPDP Act 2023

## Chapter 11.1 — From 10 Calls to 10 Million

Let us start with a simple picture.

Right now, VoxShield runs on one small server. It costs about **$25 a month**. It handles a demo, a pilot, a handful of calls at a time. That is perfect for proving the idea works.

But a large Indian bank might take **millions** of calls in a single day. One small server cannot do that. So how do you grow from ten to ten million without rewriting everything?

The answer is a design choice made early: VoxShield is **stateless**.

> In simple words: "stateless" means each call is judged completely on its own. The server does not need to remember the last call to handle the next one.

Think of a busy sweet shop. Imagine every customer walks in, is served, and leaves — and the shopkeeper needs no memory of the previous customer to serve the next. If the queue gets long, you do not need a smarter shopkeeper. You just open more counters.

VoxShield is exactly like that. Each audio clip comes in, gets a score, and the answer goes back. Nothing about that one call depends on another. So to handle more calls, you do not rebuild the machine. You simply **run more copies of it** behind a **load balancer** — a traffic policeman that spreads incoming calls evenly across all the copies.

Here is what growing looks like, in three honest tiers.

| Scale | What you run | What it needs |
| 1 to 100 calls (pilot, today) | One small server (one $25 VPS) | A single CPU box. This is what is live right now. |
| 10,000 concurrent calls | Many copies (pods) on Kubernetes, GPU batching, a queue | An orchestrator to manage the copies, GPUs to run many clips at once, a queue to absorb spikes |
| 1,000,000 concurrent calls | Multi-region autoscale with disaster recovery | Clusters in several regions, automatic scaling up and down, a backup region if one fails |

Notice how the growth is mostly about **adding more of the same thing**. That is the gift of a stateless design. Twice the traffic, twice the servers. National scale, several regional clusters.

### The honest note on speed

Here is a point we are careful never to oversell.

Adding GPUs does **not** make VoxShield more accurate. The accuracy is identical on a plain CPU. A GPU buys you one thing only: **speed at scale**.

Today, on the live CPU server, a detection takes about **2 seconds** (measured 1.7 to 2.1 seconds). That is already well within a comfortable limit for a phone call. A GPU could push that under a second and, more importantly, let one machine judge many clips at the same time (this is **GPU batching**).

> In simple words: a GPU does not make VoxShield smarter, only faster when there are huge crowds of calls. The quality of the answer is the same on a cheap CPU.

So we scale for throughput, not for cleverness. The clever part — the detection — is already done, and it runs fine on modest hardware.

### The one thing that must change to scale

There is one honest piece of engineering left before true scale.

Today, VoxShield keeps its memory **in-process**. The audit log, the enrolled voiceprints, the action records — they all live inside the running program. That is fine for one server. But if you run twenty copies, each has its own separate memory, and a restart wipes it.

So the one real task to scale is to **externalise the state**. The audit trail and the enrolment store must move out of the program's memory and into a shared **database** that every copy can read and write.

That is not a redesign. The detection engine stays exactly as it is. We simply give all the copies one shared notebook to write in. Once that is done, the stateless design scales cleanly, from one $25 box to a national deployment.

## Chapter 11.2 — Securing the System Itself

Detecting fakes is one job. Protecting the detector is another.

A bank does not just ask "is your AI accurate?" It also asks "is your system itself safe, and will you be straight with me about it?" We take that seriously. So here we split the truth into two clear lists — what is real today, and what is honestly still on the backlog.

We do this because engineering honesty is the whole point of VoxShield. We name the gaps. We do not hide them behind marketing.

### What is real today

These are built and running right now.

- **SHA-256 audio audit hash.** Every clip we analyse is fingerprinted with a SHA-256 hash. This gives a tamper-evident record that a specific audio was examined, without storing the audio itself.
- **On-premise and air-gap-capable.** VoxShield can run entirely inside the bank's own walls. The Docker image bakes the models in at build time, so no model is downloaded at runtime. It does not phone home. A bank's audio never has to leave the bank.
- **Never auto-blocks a customer.** This is a safety feature, not just a courtesy. A HIGH-concern result routes to a **human step-up** check. The machine never rejects a real person on its own.
- **Caddy HTTPS.** The live deployment sits behind Caddy, which provides encrypted HTTPS so traffic in transit is protected.
- **TURN relay for calls.** For the live two-phone call feature, a TURN relay (coturn) carries the WebRTC connection so calls connect reliably even across tricky networks.

> In simple words: today, your audio stays on your premises, every check is fingerprinted, the link is encrypted, and no real customer is ever auto-rejected by a machine.

### Roadmap and hardening backlog

Now the honest part. The following are **not built yet**. They are named, planned, and on the backlog — not shipped. We would rather tell you plainly than let you assume.

- **API-key authentication.** Right now the endpoints are open. Proper API keys and token-based auth are on the backlog, not in production.
- **Rate-limiting.** There is no throttle yet to stop one caller flooding the service. It needs adding.
- **RBAC (Role-Based Access Control).** Different staff should see different things — an analyst, a manager, an auditor. This role system is not built yet.
- **A persistent encrypted database.** As Chapter 11.1 explained, state is in-memory today. A real, persisted database is required for scale and for durable audit.
- **AES-256 at rest.** Once there is a database, the data stored in it should be encrypted at rest with AES-256. This is "ready" in design only, not implemented.
- **SOC2 and ISO 27001.** These are formal security certifications banks value. They are targets we intend to pursue, not badges we hold today.

> In simple words: authentication, rate-limits, roles, a real database, encryption at rest, and formal certificates are all planned and named — but honestly, none of them are built yet.

We list these not to look unfinished, but because a bank will ask, and we would rather be the vendor who answered truthfully. A system at **TRL-5** — a validated working prototype — is exactly where these hardening items belong on the roadmap. Overclaiming them would be the real red flag.

## Chapter 11.3 — Compliance and the DPDP Act 2023

India now has its own data protection law: the **Digital Personal Data Protection Act, 2023**, usually shortened to the **DPDP Act**. Any system that processes personal data of Indians must respect it. And a person's voice is deeply personal data.

The good news is that VoxShield's design was already pulling in the right direction. Let us walk through how, in plain terms.

### Data minimisation

The law says: do not collect or keep more personal data than you truly need.

VoxShield is naturally frugal here. A piece of audio comes in. It is turned into **one score** and a set of reasons. Then the audio itself is **discarded**. Only a **hash** — a short fingerprint that cannot be turned back into the voice — is kept for the audit trail.

> In simple words: we do not hoard people's voices. The audio becomes a number, then it is thrown away. All we keep is a fingerprint that proves a check happened.

That is data minimisation working by design, not bolted on afterwards.

### Purpose limitation

The law says: use the data only for the specific purpose you collected it for.

VoxShield has one narrow purpose — decide whether a voice is likely genuine or cloned, to protect a customer from fraud. The audio is not repurposed for advertising, profiling, or anything else. It comes in for fraud checking, it serves that one purpose, and it is gone.

### No solely-automated decision

This is one of the most important protections in the law, and one of VoxShield's core principles. A person should not have a serious decision made about them by a machine alone.

VoxShield **never auto-blocks**. A HIGH-concern verdict does not reject the customer. It raises a flag for a **human** to step in and decide. The machine advises. A person decides.

> In simple words: the computer never has the final word over a customer. It always hands a hard case to a human being.

This single design rule keeps VoxShield on the right side of the "no solely-automated decision" requirement.

### Transparency through reason codes

The law leans towards explainability — people should be able to understand a decision that affects them.

VoxShield does not output a bare "fake" or "genuine". It gives **reason codes** — the specific signals that drove the score, drawn from the SHAP explanation of the detectors. A human reviewer can see *why* a call looked suspicious. That makes the decision explainable to staff, to auditors, and if needed, to the customer.

### Data localisation through on-premise

The law is protective about where Indian data lives and travels.

Because VoxShield can run **fully on-premise** inside the bank's own infrastructure, the audio never has to leave the country or even the building. The bank keeps physical control of its data. This directly supports the localisation instinct of the DPDP Act.

Put these together — minimise, limit the purpose, keep a human in charge, explain the reasons, keep the data local — and you get a system whose design aligns with the DPDP Act by intention, not by accident. The hardening items from Chapter 11.2 (a real encrypted database, access control) are the pieces that will complete the compliance picture, and we have named them honestly rather than claimed them early.
