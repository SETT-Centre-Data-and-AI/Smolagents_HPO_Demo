# HPO Smolagents

By Matt Stammers

25/11/2025 - Presented at HDUG, London

## What is this?

![Smolagent_Logo](https://github.com/SETT-Centre-Data-and-AI/Smolagents_HPO_Demo/blob/main/img/HPO_smolagent.png)

## Explainer

These agents are pure demo-agents to illustrate how an agent can solve a very simple HPO mapping problem using clinical psuedo-data. 

I have picked out a handful of the experiments to illustrate different agent behaviours for this repo. I ran over 25 different experiments on 10 different LLMs to come up with these demo scripts.

They demonstrate an MVP version of how the problem can be solved and were given in demonstration at HDUG 2025 - London @ St Mary's House, Euston as part of the data for R&D program.

Quality Ranking:
- The deepseek-14b agent is a very early experiment and tends to work but it doesn't do much. It was the third experiment I ran.
- The gpt-oss20b agent is a middle-stage smolagent experiment which works some of the time but illustrates nicely how unreliable these agents can be in terms of performance.
- The qwenv3-8b agent is the best performing and generally succeeds to a moderate degree within 4-10 steps. However, it sometimes goes down rabbit holes.

All of them are slow are none are intended for any type of production purpose but they can be run on fairly basic HPC hardware from a single script.

## Quickstart

1. git clone this repo to a location of your choice which is GPU-enabled
2. Go to: https://hpo.jax.org/data/ontology and download hp.json (then rename to hpo to avoid confusion and drop into /src)
3. Install UV and Python if not already available
4. call:

```sh
uv sync
python src/{agent_name}
```

and the agent should run. If you run into problems please raise an issue as this has only been tested in linux environments.

## Warnings & Legal Disclaimers

This is NOT a medical device and it is not a clinical tool - it is a basic Smolagents based demo of how one of the tools we are building works. It is NOT intended for any production purpose whatsoever and is meant for illustration purposes only.

Performance WILL vary and the majority of runs with the first two agents (deepseek and gpt-oss will fail). Only the qwen_v3 based agent performs the majority of the time but even this can fail, go down rabbit holes and behave strangely. 

These are not designed as any kind of production experiment but they do allow anyone to test out the theory. They are easy to break and will not work in all environments.

UHSFT and Matt Stammers give no guarantees and take no legal responsibility for any use of this code which is provided for free under an MIT licence purely to demonstrate the principles of the how the HPO agent works and to allow others to build upon the experiment in their own way at their own risk because this project is an NHS funded project for the benefit of the wider public and the NHS.

Funder: Data for R&D Driver Program, NHS England.

Finally, I know that the bugs the agent finds in the first attempts could be easily solved with prompts. However, I left them in because they increase the failure rate which is what I wanted to simulate. If you make it too easy for the agent then you cannot test failures which was the point of this demo.
