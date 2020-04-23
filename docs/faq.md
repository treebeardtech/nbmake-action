# FAQ

## Why use continuous integration for my notebooks?

**Reproducibility**:

- So you never have to say 'works on my machine' again
- Catch breaking changes across your project
- Get rapid feedback as your project progresses

**Automation**:

- Get notifications via messages and develop asynchronously
- Peace of mind with automated testing
- Cloud containers test your project environment

**Collaboration**:

- Share the output of your work with others
- Consume pipeline outputs in other services
- Work on multiple parts of a pipeline with confidence

## How much does Treebeard cost?

Treebeard is free to use for open source projects (up to 24h build time per month) and most of our code is open source (we're working on opening up the rest). View the code at [https://github.com/treebeardtech/treebeard](https://github.com/treebeardtech/treebeard)

For closed-source private projects wanting to use our hosted service, see options [here](https://treebeard.io/pricing/) and please [get in touch](mailto:laurence@treebeard.io).

## What does Treebeard do with my data?

The Treebeard library relies on our backend services for executing your project, serving your outputs, and integrating with your Github and Slack accounts if requested. All data is encrypted, secured using Google Cloud Platform, and handled in accordance with our [privacy policy](https://treebeard.io/privacy/). Email [laurence](mailto:laurence@treebeard.io) with any questions.

## How does Treebeard work with private Github repos?

Projects triggered from a Github repository have the same private/public status as the repository.  
Projects initially triggered from the Treebeard CLI are public by default.  
But, if the project has been initialised from Github the public/private status will remain the same as the Github project.

## What are Treebeard's machine specs?

Our build machines provide 8 CPUs, 7.2 GB memory, 90GB SSD with the current goal of working with almost all tasks you would be able to achieve on your laptop.

If more capacity is needed, please [get in touch](mailto:laurence@treebeard.io).
