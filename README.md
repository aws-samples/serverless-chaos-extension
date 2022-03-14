# lambda-chaos-extension

Using `lambda-chaos-extension` to inject chaos to Lambda functions without any modification to function code.

This demo inject two chaos actions: 

1. Add 5 minutes delay to 10% of function invokes, causing the function to timeout.
2. Replace function response for 50% of invokes. 

## Deploy the sample application

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build --use-container
sam deploy --guided
```

## Chaos Tests

Browse the API Gateway URL or curl it from command line for couple of times. 

- The normal results are status 200, {"message": "hello world"}. 
- 50% of the responses are status 500, {"message": "hello, Chaos!!!"}
- 10% of the responses are status 502, {"message": "Internal server error"}. 





