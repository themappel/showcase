# Automated and Flexible Failvoer Configurations for Multi-region deployments 

This was for an Active-Active Application that could handle 100% traffic in either region. It was designed to be resilient in all kinds of situations, such as regional outage in downstream services, unexpected traffic switch in our upstream, or a complete aws regional outage. The setup is very relevant in regards to the AWS us-east-1 outages that have been happening as of late. 



So this diagram is showing one arm of the traffic routing implementation, in practice there is a R53 failover record designated as east, with primary target of us-east-1 and a R53 failover record designated as west, accordingly pointing primarily at us-west-2. 


The failover records a configured with a health check which is very standard (health check status of HEALTHY means record points to primary, UNHEALTHY, switches the record to point to it's secondary target (the other aws region)) the magic is in how that health check is managed. 

The Health check is managed explicitly by a lambda, which is listening to an SNS topic. Messages send to this SNS topic tell the lambda how to switch the health check. The SNS topic is very flexible in that we have a lot of different options in terms of what we can feed into it to trigger a health check switch and hence a failover. 


In this example we have a 5xx cloudwatch metric alarm, presumably hooked up to a critical service, which when triggered will publish to sns -> trigger the lambda -> flip the health check -> switch the failover record. 

The other option the sns topic -> lambda gives us is that we can trigger a quick manual failover without having to go in and muck with the R53 records manually. 


![Failover Diagram](./assets/failover.png)