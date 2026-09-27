#!/bin/bash

az postgres flexible-server microsoft-entra-admin list \
  --resource-group <resource-group> \
  --server-name <server-name>

OBJECT_ID=$(az ad signed-in-user show --query id -o tsv)

az postgres flexible-server update \
  --subscription <subscription-id> \
  --resource-group <resource-group> \
  --name <server-name> \
  --microsoft-entra-auth Enabled

az postgres flexible-server microsoft-entra-admin create \
  --resource-group <resource-group> \
  --server-name <server-name> \
  --display-name "admin@domain.com" \
  --object-id $OBJECT_ID \
  --type User

az postgres flexible-server microsoft-entra-admin delete \
  --resource-group <resource-group> \
  --server-name <server-name> \
  --object-id <object-id>

az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv

export PGPASSWORD=$(az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv)
psql "host=<server>.postgres.database.azure.com user=<user>@domain.com dbname=<database> sslmode=require"

az cloud show --query endpoints.ossrdbmsResourceId

az ad user show --id user@domain.com --query id -o tsv

az ad group show --group "Group Name" --query id -o tsv

az identity show --name <identity-name> --resource-group <rg> --query principalId -o tsv

az ad sp show --id <app-id> --query id -o tsv

az postgres flexible-server parameter set \
  --resource-group <resource-group> \
  --server-name <server-name> \
  --source user-override \
  --name pgaadauth.enable_group_sync \
  --value ON

az postgres flexible-server parameter set \
  --resource-group <resource-group> \
  --server-name <server-name> \
  --source user-override \
  --name pgaadauth.enable_group_sync \
  --value OFF

az postgres flexible-server parameter show \
  --resource-group <resource-group> \
  --server-name <server-name> \
  --name pgaadauth.enable_group_sync

# !!!IMPORTANT: Must enable Entra auth before attempting to create an admin

az postgres flexible-server update \
  --resource-group <resource-group> \
  --name <server-name> \
  --microsoft-entra-auth Enabled \
  --password-auth Disabled

az postgres flexible-server update \
  --resource-group <resource-group> \
  --name <server-name> \
  --microsoft-entra-auth Enabled \
  --password-auth Enabled

az postgres flexible-server update \
  --resource-group <resource-group> \
  --name <server-name> \
  --microsoft-entra-auth Disabled \
  --password-auth Enabled
