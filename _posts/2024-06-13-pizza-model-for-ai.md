---
layout: post
title: "The Pizza Model for AI"
categories: 
tags:
 - AI
 - Generative AI
 - LLM
 - Machine Learning
 - Azure
excerpt: >
    <img src="/assets/post/2024/06/13/pizza-model-for-ai/pizza-aas-ai.png" alt="The pizza as a service model for AI" />
    The Pizza Model for AI takes inspiration from the world of cloud computing, where services are often categorized into three main models: IaaS, PaaS and SaaS. 
---

The Pizza Model for AI takes inspiration from the world of cloud computing, where services are often categorized into three main models: Infrastructure as a Service (IaaS), Platform as a Service (PaaS), and Software as a Service (SaaS). Drawing inspiration from these, the Pizza Model for AI emerges as a new paradigm, offering a layered approach to AI services, or what we might call “Models as a Service” (MaaS).

### The Pizza Model for AI

<img src="/assets/post/2024/06/13/pizza-model-for-ai/pizza-aas-ai.png" alt="The pizza as a service model for AI" />

##### Training Infrastructure

The foundation of our pizza is the training infrastructure. This layer comprises the hardware and software that drive AI model training, including GPUs, TPUs, and distributed computing resources.

##### Data Scientist

The next layer is the data scientist. This role involves crafting the recipe for our AI pizza, deciding which ingredients (features) will make the cut, and how to season (tune) the model to perfection.

##### Algorithm

The algorithm forms the sauce of our pizza, spreading across the data to bring out the flavors. It’s the method by which the model learns from data, whether it be supervised, unsupervised, or reinforcement learning.

##### Training Data

No pizza is complete without cheese, and in the AI pizza, that’s the training data. It’s the essential component that melts and binds everything together, providing the model with the information it needs to learn.

##### Model

Finally, the toppings represent the model itself. Each topping (feature) adds a unique taste (prediction capability), and the combination of them defines the overall flavor profile (performance) of the AI model. Depending on the option and recipe taken, the model can be a file (pickle, onnx often in a Docker container) or an API. 

### Machine Learning

In "classical" Machine Learning the Data Scientist is responsible to select the right algorithms, do data prep and cleaning, do feature engineering and model selection. Comparable to a cook creating a pizza from scratch. The Data Scientist has full flexibility in tools, libraries and platforms. To not have to reinvent the pizza-oven the use of [Azure Machine Learning](https://learn.microsoft.com/en-us/azure/machine-learning/), [Azure Databricks](https://learn.microsoft.com/en-us/azure/databricks/machine-learning/) or the Data Science profile in [Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/data-science/data-science-overview). 

A good methodology for this recipe is the [Team Data Science Process](https://learn.microsoft.com/en-us/azure/architecture/data-science-process/overview).

### Custom Azure AI services

An extension of the Azure AI services (see below), in which you can refine the pre-trained models with your own data. Examples are [Azure AI Custom Speech](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/), [Custom Vision](https://learn.microsoft.com/en-us/azure/ai-services/custom-vision-service/), [Custom Translator](https://learn.microsoft.com/en-us/azure/ai-services/translator/custom-translator/overview). The base models have been trained by Microsoft, often with a very large dataset.

### Azure AI services

[Azure AI services](https://learn.microsoft.com/en-us/azure/ai-services/) are powerful AI models, trained on very large datasets. 

### Large Language Models (LLMs)

LLMs, such as the GPT4 models by OpenAI, are extremely large models trained on vast datasets using extensive computing power. They form the basis of Generative AI.

#### Customizing Large Language Models

Large Language Models are typically not fine-tuned with own training data after release, however there are ways to customize them.

<img src="/assets/post/2024/06/13/pizza-model-for-ai/pizza-aas-ai-llm-customization.png" alt="Customizing LLMs" />

##### Prompt Engineering

To customize large language models, one must become a skilled chef in prompt engineering. This involves carefully crafting prompts that guide the model to generate the desired output. It’s like telling the model, “Here’s what I’m looking for; now make it happen.”

##### Retrieval-Augmented Generation (RAG)

Another technique is Retrieval-Augmented Generation (RAG). Think of RAG as the secret spice blend that elevates a dish. It enhances a language model by allowing it to pull in external knowledge during the generation process, leading to more informed and accurate outputs.

### Trustworthiness  

To foster trustworthiness in machine learning and artificial intelligence, it is essential to establish robust feedback loops that not only refine algorithms for fairness, accuracy, and transparency but also adhere to ethical standards and incorporate diverse perspectives to mitigate biases. 

## Conclusion

The Pizza Model for AI serves up a comprehensive framework for understanding and deploying AI services. By considering each layer, from the infrastructure to the model, we can better decide which methodology fits your needs, making sure your next AI project is as delightful and satisfying as your favorite slice of pizza.