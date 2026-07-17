---
layout: post
title: "The Five Elements of an AI OS"
categories: 
tags:
 - AI
 - Generative AI
 - Agentic AI
 - AI OS
 - Knowledge & Data
excerpt: |
  We called it an operating system, and then mostly used the word as branding. But the metaphor holds up better than it has any right to. An AI OS has a kernel, memory, a scheduler running programs, and device drivers—we just call them governance, context, process & workflows, and integrations.

  Then there's the fifth element, the one the metaphor strains to hold: the humans. Take any one away and the other four stop being useful.
---

We called it an operating system, and then mostly used the word as branding. Every vendor with a chat box and a webhook is shipping an "AI OS" this year.

I should declare my interest early: I'm CEO of [Scrydon](https://scrydon.com/), and an AI OS is what we build. So read this as a practitioner's argument rather than a neutral survey. The frame below is the one I'd defend against my own competitors—and the one I'd want used against us.

But the metaphor holds up better than it has any right to. Sit with it for a while and the mapping gets uncomfortably precise. An [AI OS](https://scrydon.com/platform/ai-os/) has a kernel, memory, a scheduler running programs, and device drivers. We just call them **governance**, **context**, **process & workflows**, and **integrations**.

And then there's a fifth element that has no clean analogue at all, because it isn't part of the machine: the **humans**, and whether they're still in control. That one is last on purpose, and it's the only one that can't be bought.

Five elements. Like a real OS, take any one away and the other four stop being useful.

Let me walk through them in the order they actually matter—which is not the order the marketing slides use.

## Why an Operating System at All?

Before the elements, the premise. Scrydon's argument in [*Who Needs an AI OS?*](https://scrydon.com/insights/2026/07/09/who-needs-an-aios/) is a scale argument, and it's worth restating because it's the whole foundation:

> Scale to 1,000 people across departments and geographies, however, and informal approaches break down.

Five people don't need an operating system. They need a shared drive and a group chat. Five agents don't either—you can wire them together with a Python script and read the logs yourself.

A thousand of either, and something has to schedule, route, and govern the work. That something is either an operating system you chose deliberately, or an operating system that emerged accidentally out of Slack messages, spreadsheets, and tribal knowledge. Every large organisation already runs an AI OS. Most of them just never designed it.

The same thing happened with computers. Early machines ran one program at a time, loaded by hand, and the operator *was* the operating system. That worked until it didn't. Nobody decided operating systems should exist; they became unavoidable the moment you had more work than one person could hand-schedule.

We're at that moment with agents.

Though it's worth being precise about *whose* operating system we mean, because the word is doing two jobs. Agno ships an agent framework and a runtime it calls AgentOS—fast, bring-your-own-cloud, private by default, genuinely good. The name is exact in a way that's easy to skim past: it's an OS for *agents*. You bring the process, the context and the governance; it makes what you built run well, and it makes it run well for a software team.

That's not the thing I'm describing. An OS for agents schedules agents. An OS for an organisation schedules the *business*—and the business was there first, mostly doesn't consist of agents, and isn't going to be rewritten to suit them.

## 1. Governance: the Kernel

Start here, because everything else runs on top of it.

In a real OS, the kernel isn't the interesting part—it's the part that decides what's *allowed*. Ring 0 versus ring 3. System calls. Memory protection. The kernel's entire job is to be the thing that userland programs cannot talk their way around. A process doesn't ask nicely for another process's memory; the request is structurally impossible.

That's what governance is in an AI OS, and it's why it can't be a layer you add later. Scrydon frames it as policy-based guardrails, federated identity, zero-trust infrastructure, and complete audit trails—running inside your perimeter, from [air-gapped](https://scrydon.com/platform/sovereign-infra/air-gapped/) to [EU cloud](https://scrydon.com/platform/sovereign-infra/cloud/).

The thing worth noticing: an agent asking permission is not governance. An agent asking permission is a prompt, and prompts are negotiable. Real governance is the agent *being unable* to reach the system it doesn't have an identity for. The difference between "the agent was told not to" and "the agent could not" is the difference between a policy document and a kernel.

I wrote before about [why enterprise IT flinches at fully autonomous agents](/2026/02/22/openclaw-vs-enterprise-workflow-engines/). This is the flinch, precisely located. It's not fear of AI. It's the reasonable objection that a system with no privilege boundary is a system where every actor is root.

Nobody would ship that operating system. We keep shipping that agent platform.

The serious end of the market has worked this out. Deliverance sells itself as the agentic operating system for the enterprise and leads with the control plane—runtime governance, stopping an agent mid-execution, policy enforcement, human gates, air-gapped through to sovereign cloud and deliberately outside CLOUD Act reach. Agree with the details or don't; the *ordering* is right. Putting the kernel first isn't a marketing choice, it's a bet that governance is the one element you cannot retrofit. It's the same bet I'd make, and the fact that a competitor makes it too is better evidence than my saying so alone.

## 2. Context: Memory

Here's where the metaphor earns its keep.

An operating system's most underrated job is memory management. Not storage—*memory*. The difference is that storage is where things sit, and memory is what a running process can actually see right now. The OS decides which pages are resident, maps them into the process's address space, and hands over precisely the working set for the task at hand.

An AI OS does the same for meaning. Scrydon defines it as the runtime that brings *the right context to the right agent at the right time*, assembled from two sources: the [ontology](https://scrydon.com/platform/cognitive-enterprise/)—the semantic model of your business—and live operational data.

Ontology is the address space. Live data is what's resident.

And this reframes the failure mode everyone knows by feel. Teams keep hitting what Scrydon calls the **context wall**: the agent works beautifully in the demo and falls over in production, because production is where the process actually needs to know that this customer is under a payment plan, that this SKU is discontinued in Belgium but not in France, that this approval already went through last Tuesday.

That's not a model problem. You cannot fix it with a better model any more than you can fix a segfault with a faster CPU. It's a memory management problem. The agent was handed the wrong working set.

Which is also the honest answer to "why can't we just use ChatGPT for this?" Personal AI is a process with no persistent address space. Brilliant, and amnesiac by design—every session starts with an empty heap. It has no shared memory of your business, and it never will, because it was never architected to.

The compounding claim in the Scrydon piece follows directly from this: every execution writes back into the ontology, so the next run starts better informed. Personal AI conversations evaporate. Organisational AI accretes. Same reason a database gets faster with a warm cache and a chat window never does.

None of which is my idea, and I'd rather credit it than pretend. Palantir has been building this element since before the rest of us had the vocabulary for it—the Ontology, wrapped in Foundry and AIP, treats the semantic model of the business as the primary asset rather than a modelling exercise you do before the real work. They were right early. If you want evidence that this frame isn't something I reverse-engineered from my own product, the most successful company in the category built an empire on element two.

What's more instructive is where platforms *look* like they have this element and don't. A library of prebuilt agents is the usual tell—Deliverance ships north of a hundred agents and a hundred and fifty skills, which is a serious library and a real asset. But a library is drivers and userland. It's capability, ready to run. It is not a semantic model of *your* business, and no quantity of the former adds up to the latter. An AML agent knows anti-money-laundering. It does not know that this counterparty was cleared under an exception your compliance committee granted in March, and there's no ontology for it to ask. So it runs the process it was built for instead of the process you actually have—and hits the context wall from the inside, where it's hardest to catch, because nothing errors. It quietly answers a slightly different question than the one you needed answered.

Agentforce comes at the same element from the opposite direction, and their move is the sharpest in the market: make the agent native to the platform where the data already lives and it needs no connector to know the account. That's genuine context, structurally rather than by integration, and it's why it demos so well.

It's also the ceiling. Your process doesn't live in your CRM. It starts there, touches the ERP, passes through the thing in the basement from 2009, and ends where a person signs. An ontology that stops at the platform boundary is a working set that stops at the platform boundary—and the steps that fall outside it are precisely the ones that were hard.

## 3. Process & Workflows: the Scheduler and the Programs

These are usually sold as two things. They're one thing seen from two altitudes, and pulling them apart is how you end up with a beautiful process map that nothing executes, or a pile of flows that no one can explain the purpose of.

The scheduler's job in an OS is unglamorous and total: take work, decide who runs it, decide when, handle the fact that some of it blocks on I/O and some of it needs to preempt everything else. No scheduler, no multitasking—you're back to one program at a time, loaded by hand. And what it schedules are *programs*: the actual userland things that do the job.

An AI OS schedules business processes. It takes a process, decomposes it into steps, and for each step answers the only question that matters: *who or what should execute this?* Sometimes the answer is an agent. Often it's an existing system that has done the job correctly for fifteen years. Sometimes it's a rule engine, because a threshold check doesn't need a frontier model and never did. And sometimes it's a person—which is where this gets interesting, and where I'll pick it up again at the end.

The workflow is what that decomposition *becomes* when it runs. An LLM classifying an inbound document, a rule checking a limit, a system of record getting updated, an exception routing to someone who can own it. This is the [flow-based argument](/2026/01/31/the-future-of-agentic-ai-is-flow-based/) I've made before, and the OS frame sharpens why it works.

Individual LLM calls are non-deterministic. Individual system calls fail too. An OS doesn't achieve reliability by making every operation deterministic—it achieves reliability by making the *composition* predictable, observable, and recoverable when a piece misbehaves. Same with workflows. You don't need the LLM to be deterministic. You need to know what it was asked, what it saw, what it decided, what it invoked, and what happens when it's wrong. **Determinism in the graph; reasoning at the nodes.**

I'd like to claim that formulation, but the market arrived at it independently, which is worth more than my agreeing with myself. Agentforce's Agent Script does exactly this—required business logic runs in sequence, LLM reasoning handles the nuance. Different company, opposite end of the market, same conclusion. When teams with nothing in common converge on a pattern, it's usually because the pattern is load-bearing rather than fashionable.

Which is why process-first beats model-first. Start from the model and you get a system looking for work to do. Start from the process and you get work that finds the right executor. Those produce very different architectures, and only one of them survives contact with an actual enterprise.

The next move here is the interesting one, and coding agents already showed us the shape: autonomous reasoning *generates* the artifact, deterministic execution *runs* it. Describe intent in natural language, get a flow, review it, deploy it. Autonomy in authorship, determinism in production. Not a compromise between the two paradigms—the layering that lets you have both.

## 4. Integrations: Drivers

Nobody loves drivers. Drivers are where operating systems go to accumulate scar tissue. They're also the entire reason an OS is useful, because without them the kernel is an elegant abstraction that can't talk to a printer.

Every OS that won, won on drivers. Not on kernel design—there were better kernels. On the boring, unglamorous fact that when you plugged something in, it worked.

The AI OS driver model runs on three tiers, and it's worth being precise about them:

**[MCP](https://modelcontextprotocol.io/)** is how an agent reaches a tool. Call it the device driver interface—the standard shape that lets a capability be plugged in without the agent knowing anything about what's on the other side.

**A2A** is how agents reach each other. This is inter-process communication, and it's newer and messier than anyone admits, in exactly the way IPC was messy before anyone agreed on pipes and sockets.

**Legacy integration** is the tier nobody puts on the slide and everybody spends their quarter on. The mainframe. The SOAP endpoint. The ERP with the integration surface of a brick. This is where AI OS projects actually succeed or die, and the reason is structural: your processes already run through these systems. An AI OS that can't reach them isn't orchestrating your business. It's orchestrating a demo.

The tell for a serious platform isn't how many MCP servers it lists. It's whether it has an answer for the thing running in the basement since 2009.

## 5. Humans: in Control

Here's where the metaphor runs out, and I think that's the most useful thing about it.

Four elements map cleanly onto an operating system because they're all *machine*. The fifth doesn't map at all, because an operating system has no element called "the user." The user isn't in the architecture diagram. The user is who the diagram is *for*. Every OS ever built takes it as axiomatic and unstated: the machine serves someone, and that someone is not a component.

An AI OS can't leave it unstated, because in an AI OS people show up in two completely different roles, and conflating them is how organisations lose control without noticing.

**Humans as executors.** Back to the scheduler: sometimes the right performer for a step is a person. In an AI OS, humans are schedulable resources—not exceptions, not fallbacks, not the sad path when the AI fails. A first-class executor type the scheduler routes to *on purpose*, because the decision is consequential, or contested, or because someone needs to put their name on it. The lawyer signing the document isn't a limitation of the automation. The lawyer *is a step*, with an SLA and an audit trail like every other step.

**Humans as owners.** This is the role with no analogue, and the one that matters. The scheduler never schedules the owner. Somebody decides what the system is *for*, what it's allowed to become, and when it stops—and that authority can't be a step in a flow, because a step in a flow is something the system already controls.

An OS gets this for free through sheer physics. However elegant the scheduler, a person can hit Ctrl-C. Pull the power. Decide the machine is doing the wrong thing entirely and turn it off, and no amount of process priority argues back. The interrupt always wins, because the interrupt comes from outside.

An AI OS has to *engineer* what an OS gets from physics. Every element above is really a mechanism for keeping that outside-ness real:

- **Governance** is what makes "no" structural instead of negotiable.
- **Context** is what makes oversight *possible*—you cannot supervise a decision whose inputs you can't see. An unauditable system isn't under human control no matter who nominally owns it.
- **Process & workflows** are what make the system legible enough to interrupt. You can't hit Ctrl-C on a thing you can't see running. When a CFO asks "what will this do?"—you show them the flow.
- **Integrations** are what bound its reach.

Which is the actual argument of this whole post. "Human in the loop" gets said constantly and usually means an approval button bolted onto the end of something already decided. That's not control. That's a person rubber-stamping at the speed the machine sets, which is worse than no oversight, because it produces the paperwork of accountability without the substance.

Real control is architectural. It's the difference between a system that asks permission and a system that *cannot proceed*—and you only get the second one if the other four elements were built to deliver it.

This isn't about limiting AI capability. It's the same thing I keep coming back to: the deployments that reach production are the ones where lawyers still sign, analysts still approve, and edge cases still find a person. Not because the AI is weak. Because that's what it means for the thing to be *yours*.

### Whose machine is it, though?

One more owner question, and it isn't about agents at all. Ownership isn't only whether you can hit Ctrl-C today—it's whether you could leave. Which makes *sovereign* two questions wearing one label: **where does it run, and can you walk away?**

The first has been answered about as hard as it can be: Palantir will run behind your air gap and prove it in a SCIF. The second mostly doesn't get raised. The Ontology is theirs—format, runtime, semantics, all the way down—so your semantic model, the compounding asset in this whole stack, only means anything inside their system. The asset and the lock-in are the same object, growing at the same rate. And it arrives with an army of forward deployed engineers, which is most of why Palantir works and also the point: the air gap stops packets, not people. The vendor is in the room learning your exceptions and your workarounds, and those people have a manager and a roadmap somewhere else. Nothing sinister is implied; it doesn't need to be. That's an org chart, not espionage—and an org chart is a channel whether anyone intends it as one. The deepest lock-in was never the format. It's that the *understanding* of why your ontology is shaped that way walks in every morning, and on the last day of the engagement walks out.

Point it at me, then. Scrydon isn't open source—if "closed" means you can't read my source, I'm in the same room and shouldn't throw anything. What I'd defend is the distance to the exit: our data sits in Apache Iceberg, not our format but *the* format, readable by engines we don't control. And we cannot see what you do—no telemetry, no dashboard in our office, no mechanism by which I'd know what a customer's agents did last Tuesday. We gave up the SaaS feedback loop on purpose, because "we won't look" is a policy, and policies get revised, companies get acquired, jurisdictions compel. "We cannot look" is a kernel.

Which is this post's test, pointed at the vendor instead of the agent. Told no, or unable. Ask every platform you're evaluating—ask me—what you keep on the way out, and what we can see while we're in. An operating system you cannot leave is one where you aren't, finally, the owner. You're just the person who bought the hardware.

## The Elements Only Work Together

Here's the part that took me longest to see. These five aren't a feature list. They're a dependency graph, and it's brutally unforgiving:

- **Governance without context** is compliance theatre with nothing to govern.
- **Context without governance** is your entire business ontology, one prompt injection away from an exfiltration incident.
- **Process without integrations** is a beautiful map of work you cannot actually perform.
- **Integrations without process** is n8n with better branding—capability with no idea what it's for.
- **All four without humans in control** is the one that should worry you. Everything works. Nothing is anyone's. It's an organisation that has automated its processes and quietly outsourced its judgement, and it will run beautifully right up until the day it's confidently, auditably, at scale, wrong.

You can buy all five separately. Most organisations are, right now, and they're discovering the same thing everyone discovers: five components from five vendors is not an operating system. It's five components. The integration burden of making them into a system is the actual work, and it never appears on any of the five invoices.

An operating system isn't a collection of parts. It's the part that makes the parts cohere.

## So Who Needs One?

The honest answer is: fewer organisations than the market currently believes, and every single one of them already knows who they are.

If your processes fit in one team's head, you don't need this. Use personal AI, use n8n, ship something today, and be genuinely happy. That's not a consolation prize—most work is that work, and an operating system would be pure overhead.

You need an AI OS when your processes span teams, systems, and decision points. When you've hit the context wall and noticed that more model isn't the answer. When "it usually works" is not a sentence you're allowed to say to a regulator. When the data cannot leave the perimeter, and that's a legal fact rather than a preference. When you want the tenth process to be cheaper than the first, because the first nine taught the ontology something.

That last one is the real dividing line, and it's what [Scrydon is building](https://scrydon.com/platform/ai-os/): AI that compounds instead of AI that resets. Everything else on the list is a threshold you cross once. Compounding is the thing that keeps paying.

Because that's what operating systems were always for. Not to do the work—the programs do the work. The OS exists so the thousandth program doesn't have to rediscover the disk, and so the person who owns the machine still owns it at program one thousand and one.

*The right context, to the right agent, at the right time.* It sounds like a tagline. Read it as a specification and the fifth element is already hiding in it—because the honest version of that sentence has always been the right context, to the right agent, **system, or person**, at the right time.

The person was in the spec the whole time. Build the OS that keeps them there.
