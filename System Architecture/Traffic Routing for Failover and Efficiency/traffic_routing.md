# Traffic Routing For Resiliency and Efficiency 

This is something I did as part of a larger infrastructure effort I was leading for a collection of ECS services behind an ALB. External Access to the services was regulated and maintained via an External Gateway. 2 of our Services needed to be accessible through the gateway and were exposed as REST API's, All other internal services were not called externally, and just invoked each other. 


Prior to this, all our services were exposed through the Gateway and technically accessible to external services, even though this wasn't needed. Whenever an internal microservice invoked another, it had to jump through gateway, as if it was an external service. This extra hop was a contributing factor to extra latency in our platform. 


As part of the larger infrastructure migration I was leading, we decided to take a common sense approach and allow internal services to go straight through to our CNAME's. We chose this rather than straight to the corresponding ALB to ensure that when we did failover to another region, internal service calls would also fail over. We ended up saving ~30ms response time on average as a result of this. 


Check out the failover section for more info on how that failover records work




![Traffic Routing Diagram](./trd.png)