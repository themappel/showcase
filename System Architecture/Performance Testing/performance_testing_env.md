# Reliable Performance Testing for Distributed Systems


The most major consideration for this performance testing environment was the mocking service. The System being tested had a workflow that was dependent on the data passed back from downstream services while processing the request. Each Downstream service was mocked in it's own ECS cluster, and provided a response designed to illicit the desired flow in the application. Many downstream interactions had to be mocked, but the configuration proved to be re-usable after initial setup. 


All performance environment configurations were set up at the configuration and infrastructure level. This common-sense de-coupling of performance environment configurations and application code give us a few key benefits: 

- Easily provision performance environment with no custom set-up
- Test the application exactly as how it will be deployed
- Easily maintain configurations
- Scale the performance environment up and down easily 




![Traffic Routing Diagram](./assets/perftestenv.png)