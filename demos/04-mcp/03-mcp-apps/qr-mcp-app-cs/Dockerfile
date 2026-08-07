FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS base
WORKDIR /app
EXPOSE 3002

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

COPY ["qr-mcp-app-cs.csproj", "."]
RUN dotnet restore "qr-mcp-app-cs.csproj"

COPY . .

RUN dotnet build "qr-mcp-app-cs.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "qr-mcp-app-cs.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app

COPY --from=publish /app/publish .

ENV ASPNETCORE_ENVIRONMENT=Production
ENV PORT=3002

ENTRYPOINT ["dotnet", "qr-mcp-app-cs.dll"]