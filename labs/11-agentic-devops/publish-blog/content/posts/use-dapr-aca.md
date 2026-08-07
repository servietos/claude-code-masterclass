+++
date = '2023-02-05T13:22:53+02:00'
title = 'Use Dapr with Azure Container Apps'
tags = ['Cloud Native', 'Azure', 'Dapr']
+++

In this post, I will show you how to use Dapr with Azure Container Apps (ACA) and demonstrate how easy it is to use Dapr for Lift and Shift scenarios. The complete code and details can be found in my [az-204 GitHub repository](https://github.com/alexander-kastil/az-204/tree/main/demos/05-containers/demo-08).

Dapr is a portable, event-driven runtime that makes it easy for developers to build resilient, microservices-based applications. It provides a set of building blocks for common application patterns, such as service invocation, state management, and pub/sub messaging. Dapr can be used with any programming language and framework, and it can run on any cloud or on-premises environment.

Azure Container Apps (ACA) natively supports [Dapr](https://docs.dapr.io/concepts/overview/), a distributed application runtime that simplifies building resilient microservices. By enabling Dapr in your container app, you gain access to a set of managed APIs and building blocks—such as service invocation, state management, pub/sub, bindings, actors, and secrets—through a Dapr sidecar that runs alongside your app. This sidecar can be invoked via HTTP or gRPC, and Dapr components can be shared across multiple container apps using scopes.

![dapr-architecture](/images/posts/aca-dapr/dapr-architecture.png)

## Step-by-Step Guide: Using Dapr with Azure Container Apps

This post walks you through a practical scenario of integrating Dapr with Azure Container Apps (ACA) for a simple .NET 9 Web API. Here’s a more detailed breakdown of the steps:

1. **Project Overview & Prerequisites**

   - The sample project is a .NET 9 Web API that uses Dapr for state management. It leverages the Dapr.Client and Dapr.AspNetCore NuGet packages.
   - Ensure you have the Azure CLI, Docker, and the .NET SDK installed. You’ll also need an Azure subscription and permissions to create resources.

2. **Understanding Dapr in ACA**

   - ACA provides native support for Dapr, enabling you to add distributed system capabilities (like state management, pub/sub, and service invocation) to your microservices with minimal code changes.
   - Dapr runs as a sidecar alongside your app, exposing HTTP/gRPC endpoints for building block APIs. Components can be shared across apps using scopes.

3. **Configuring State Store (Redis Example)**
   - The blog demonstrates configuring a Redis state store for local development. The provided YAML defines a Dapr component for Redis, which Dapr uses to persist state.
   - You can run Redis locally using Docker for quick setup and testing.

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: food-state
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
```

In order to use Redis locally, you need to install it. You can do this using Docker:

```bash
docker run -d --name redis/redis-stack -p 6379:6379 redis
```

4. **Registering and Using DaprClient**
   - The DaprClient is registered in `Program.cs` and injected into the controller. The state store name is managed via configuration, making it easy to switch between local and cloud state stores.

```csharp
builder.Services.AddDaprClient();
```

- The controller uses `GetStateAsync` and `SaveStateAsync` to retrieve and update the counter value, demonstrating Dapr’s state management API in action.

```c#
[Route("[controller]")]
[ApiController]
public class CountController : ControllerBase
{
    string storeName = "";
    const string key = "counter";

    private readonly DaprClient client;

    public CountController(DaprClient daprClient, IConfiguration cfg)
    {
        client = daprClient;
        storeName = cfg.GetValue<string>("DAPR_STATE_STORE");
    }

    [HttpGet("get")]
    public async Task<int> Get()
    {
        var counter = await client.GetStateAsync<int>(storeName, key);
        await client.SaveStateAsync(storeName, key, counter + 1);
        return counter;
    }
}
```

5. **Switching to Azure State Store**
   - For cloud deployment, the state store is switched to Azure Blob Storage by providing a new Dapr component YAML. This demonstrates how Dapr abstracts the underlying state provider, making it easy to change backends without code changes.

```yaml
componentType: state.azure.blobstorage
version: v1
metadata:
  - name: accountName
    value: "foodstoragedev"
  - name: accountKey
    value: "<ACCOUNT_KEY>"
  - name: containerName
    value: "food-state"
```

In the Container App Environment, we will create a new component using the Azure CLI. The component name is `food-state` and the type is `state.azure.blobstorage`.

```bash
az containerapp env dapr-component set -n $acaenv -g $grp \
    --dapr-component-name $statestore \
    --yaml statestore-blob.yaml
```

6. **Deploying to Azure Container Apps**
   - The post details how to deploy the app to ACA using the Azure CLI. It covers setting up the environment, configuring the Dapr component, and deploying the container with Dapr enabled.
   - The deployment uses .NET 8+ conventions (port 8080) and demonstrates how to pass container registry credentials securely.

```bash
pwd=$(az acr credential show -n $acr -g $grp --query passwords[0].value -o tsv)
loginSrv=$(az acr list -g $grp --query "[?name=='$acr'].loginServer" -o tsv)

...

az containerapp create -n $app -g $grp \
    --image $img \
    --environment $acaenv \
    --target-port 8080 --ingress external \
    --min-replicas 1 --max-replicas 1 \
    --enable-dapr \
    --dapr-app-port 8080 \
    --dapr-app-id $app \
    --registry-server $loginSrv \
    --registry-username $acr \
    --registry-password $pwd
```

7. **Verifying and Monitoring**

   - After deployment, you can verify state persistence in your Azure Storage account or other configured state store.
   - Logs can be viewed in the Azure Portal or queried using the Azure CLI and Log Analytics, helping you monitor and troubleshoot your Dapr-enabled app.

8. **Cleanup**
   - To avoid unnecessary costs, remember to delete your resource group when finished.

By following these steps, you can quickly enable Dapr’s powerful distributed application features in your Azure Container Apps, with minimal changes to your application code and maximum flexibility for future enhancements.
