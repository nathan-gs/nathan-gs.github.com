---
layout: post
title: "Autogen: multi-agent large language models (LLM-MA) to solve complex tasks"
categories: 
tags:
 - AI
 - Generative AI
 - Azure
---

Large language models (LLMs) excel in natural language understanding and generation, but they also present challenges in solving more complex tasks. Multi-agent systems offer significant advantages over single-agent Large Language Models (LLMs) when it comes to addressing complex problems. __[AutoGen](https://github.com/microsoft/autogen/)__, a framework framework for orchestrating, automating, and optimizing LLM workflows allows developers to create customizable agents that collaborate to solve tasks. AutoGen agents are customizable, conversable, and seamlessly allow human participation. They can operate in various modes that employ combinations of LLMs, human inputs, and tools.

Some interesting papers and articles on the topic

- [Large Language Model based Multi-Agents: A Survey of Progress and Challenges](https://arxiv.org/html/2402.01680v2) from Jan 2024
- [Navigating Complexity: Orchestrated Problem Solving with Multi-Agent LLMs](https://arxiv.org/html/2402.16713v1) from Feb 2024
- [Today’s AI models are impressive. Teams of them will be formidable (The Economist)](https://www.economist.com/science-and-technology/2024/05/13/todays-ai-models-are-impressive-teams-of-them-will-be-formidable) from May 2024
- [The Promise of Multi-Agent AI (Forbes)](https://www.forbes.com/sites/joannechen/2024/05/24/the-promise-of-multi-agent-ai) from May 2024

### What are Agents

In artificial intelligence, an agent is a computer program or system designed to perceive its environment, make decisions, and take actions to achieve specific goals or sets of goals. A multi-agent system involves multiple autonomous agents that interact with each other to achieve a common goal. By collaborating, they enhance overall system performance and achieve better outcomes than individual drones acting independently. The new wave of Generative AI revived and adapted this concepts to _Large Language Model Multi-Agent Systems_ (__LLM-MA__). 

#### Specialization and Collaboration

- Multi-agent systems involve multiple agents, each with distinct capabilities. These agents collaborate, leveraging their unique expertise and perspectives to tackle complex tasks effectively.
- Unlike a single LLM-powered agent, which might struggle to coordinate and strategize in complex environments, multi-agent systems enable efficient interactions among diverse agents.

#### Decomposition and Nuanced Solutions

- A novel approach involves an orchestrating LLM that decomposes complex problems into manageable sub-problems.
- Instead of expecting the LLM to solve the entire problem at once, it asks follow-up questions to gain a deeper understanding of user requirements.
- Specialized LLM agents or non-LLM functions then work in parallel to solve sub-problems, with the orchestrating LLM compiling comprehensive answers.
- This decomposition approach empowers LLMs to provide nuanced solutions, breaking down complex problems into manageable parts.

## Understanding Agents in AutoGen

In the context of AutoGen, agents are specialized entities equipped with large language models. Each agent has a unique role and is designed to perform specific tasks. An agent has a specific System Prompt which defines the behavior and role. By employing multiple agents, AutoGen can approach a problem from various angles, ensuring a more comprehensive and effective solution. 

<img src="/assets/post/2024/06/23/autogen-multi-agent-llms-to-solve-complex-tasks/autogen_agentchat.png" alt="AutoGen: Agentchat" />
_AutoGen agentchat from [microsoft/autogen](https://github.com/microsoft/autogen) on Github._

### Types of Agents

Some examples of agents in AutoGen are:

- __AssistantAgent__: An agent that acts as an AI assistant, using LLMs by default but not requiring human input or code execution. It can write code, suggest corrections, or perform other actions based on the received messages3.
- __UserProxyAgent__: An agent that acts as a proxy for humans, soliciting human input as the agent's reply at each interaction turn by default and also having the capability to execute code and call functions or tools. It can also generate replies using an LLM when code execution is not performed.
- __GroupChatManager__: An agent that coordinates between multiple agents

## Capabilities of AutoGen

<img src="/assets/post/2024/06/23/autogen-multi-agent-llms-to-solve-complex-tasks/autogen_studio.png" alt="AutoGen Studio" />

AutoGen is not just limited to generating text; it can interact with the environment in various ways, making it a versatile tool for numerous applications.

### Feedback loops

AutoGen allows __Human Feedback Loops__ to improve agent performance, like we are used to in interactive chatgpt-like applications. Another important feedback mechanism is __Agent-to-Agent Feedback__, imagine two AutoGen agents collaborating on a creative writing task. Agent A generates an initial story fragment, and Agent B responds with a continuation. They iterate, providing feedback and refining the narrative until they create a cohesive story. Finally, __Code Execution Feedback loops__ can help Autogen write executable code, by running the generated sample and processing the output (including looking at return codes and error messages).

By combining these three approaches, AutoGen achieves adaptability, continuous improvement, and versatility. 

### Use Cases

- __Code Generation__: execution, and debugging: AutoGen can help developers write, run, and fix code using LLMs, tools, and human feedback. For example, an AssistantAgent can generate code snippets, suggest corrections, or execute code based on the user's requests. A UserProxyAgent can solicit human input, run code, or call functions or tools. AutoGen can also support automated code generation and question answering with retrieval augmented agents. 
- __Code Conversion__: AutoGen can automatically convert one programming language to an another. For example convert COBOL to Java, one _Agent_ can generate code snippets, while another _Agent_ suggest corrections, or executes the code based. This can be mixed with direct human interaction.
- __Schema Matching for APIs__: using multiple Agents to convert the schema of one API to the schema of another API, and then use an LLM to generate a mapping between them. For example, if one API returns a field called “firstName” &  “lastName” and another API returns a field called “fullName”.
- __Writing ETL__: by a combination of agents automatically write extract, transform, load (ETL) pipelines. 
- __Better Writing__: AutoGen can also be used to write blog posts, like the one you're reading now. Different agents can contribute to various sections, ensuring that the content is well-researched, coherent, and engaging.
- __Gaming__: Autogen [can play chess](https://github.com/microsoft/autogen/blob/main/notebook/agentchat_nested_chats_chess.ipynb) and other games.
- __Social Simuation__: Autogen is an excellent basis for _multi-agent debates_.
- __Planning Trips and Travel__: Incorporating specific agents tasked with local knowledge and language help, to come-up with a better travel plan.

## Getting started

Getting started with Large Language Model Multi-Agent (LLM-MA) systems is easy with Autogen. Easiest is to use a subscription to [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service), although you can [bring your own model](https://microsoft.github.io/autogen/docs/topics/non-openai-models/about-using-nonopenai-models). I got excellent results with [GPT-4o](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#gpt-4o-and-gpt-4-turbo). 

#### Exploring notebooks

AutoGen provides a collection of notebooks that demonstrate various features and use cases. These notebooks cover topics like function calling, mitigating prompt hacking, group chat orchestration, code generation, debugging, and more. 

- [Notebooks in the Autogen documentation](https://microsoft.github.io/autogen/docs/notebooks/)
- [Notebooks in microsoft/autogen](https://github.com/microsoft/autogen/tree/main/notebook)

#### Using Autogen Studio

AutoGen Studio is an interactive interface powered by AutoGen, it allows you to rapidly prototype multi-agent solutions for your tasks.

- [Getting started](https://microsoft.github.io/autogen/docs/autogen-studio/getting-started/)
- [Introducing AutoGen Studio](https://microsoft.github.io/autogen/blog/2023/12/01/AutoGenStudio/)
- [Introducing AutoGen Studio: A low-code interface for building multi-agent workflows](https://www.microsoft.com/en-us/research/blog/introducing-autogen-studio-a-low-code-interface-for-building-multi-agent-workflows/)

To get this working on [NixOS](/tags/nixos), take a look at my config: [nathan-gs/nix-conf](https://github.com/nathan-gs/nix-conf/blob/main/services/autogenstudio.nix).

## Responsible AI and AutoGen

Definitely review the [Autogen Transparency FAQ](https://github.com/microsoft/autogen/blob/main/TRANSPARENCY_FAQS.md) on limitations. 

## Conclusion

AutoGen represents a significant advancement in the field of AI, leveraging the power of multi-agent systems to solve complex tasks. By employing multiple agents with different prompts and temperatures, AutoGen can provide diverse perspectives, specialized expertise, and increased reliability. Its capabilities extend beyond simple text generation, making it a valuable tool for developers, businesses, and content creators alike.

Whether it's generating and debugging code, converting programming languages, matching API schemas, writing ETL pipelines, playing chess, or crafting blog posts, AutoGen's multi-agent approach ensures that complex tasks are handled efficiently and effectively. 