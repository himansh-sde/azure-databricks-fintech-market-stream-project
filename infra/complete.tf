terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85.0"
    }
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.35.0"
    }
  }
}

# 1. AZURE PROVIDER (With Auto-Purge for Key Vault)
provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true # Eliminates the need for 'az keyvault purge'
      recover_soft_deleted_key_vaults = false
    }
  }
}

data "azurerm_client_config" "current" {}

# 2. BASE INFRASTRUCTURE
resource "azurerm_resource_group" "rg" {
  name     = "rg-marketstream-prod"
  location = "East US"
}

# 3. EVENT HUBS & SAS POLICIES
resource "azurerm_eventhub_namespace" "ehns" {
  name                = "ehns-marketstream-${random_integer.suffix.result}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Standard"
  capacity            = 1
}

resource "azurerm_eventhub" "eh" {
  name                = "market-trades"
  namespace_name      = azurerm_eventhub_namespace.ehns.name
  resource_group_name = azurerm_resource_group.rg.name
  partition_count     = 2
  message_retention   = 1
}

# Automating the separated network policies we did manually
resource "azurerm_eventhub_authorization_rule" "listen_policy" {
  name                = "consumer-listen-policy"
  namespace_name      = azurerm_eventhub_namespace.ehns.name
  eventhub_name       = azurerm_eventhub.eh.name
  resource_group_name = azurerm_resource_group.rg.name
  listen              = true
  send                = false
  manage              = false
}

resource "azurerm_eventhub_authorization_rule" "send_policy" {
  name                = "producer-send-policy"
  namespace_name      = azurerm_eventhub_namespace.ehns.name
  eventhub_name       = azurerm_eventhub.eh.name
  resource_group_name = azurerm_resource_group.rg.name
  listen              = false
  send                = true
  manage              = false
}

# 4. STORAGE & DATABRICKS MANAGED IDENTITY
resource "azurerm_databricks_access_connector" "dbac" {
  name                = "dbac-marketstream"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_storage_account" "sa" {
  name                     = "stmarketstream${random_integer.suffix.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true # ADLS Gen2
}

# Automating the "Storage Blob Data Contributor" IAM Role
resource "azurerm_role_assignment" "adls_contributor" {
  scope                = azurerm_storage_account.sa.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_databricks_access_connector.dbac.identity[0].principal_id
}

# 5. KEY VAULT & SECURITY (RBAC)
resource "azurerm_key_vault" "kv" {
  name                      = "kv-market-${random_integer.suffix.result}"
  location                  = azurerm_resource_group.rg.location
  resource_group_name       = azurerm_resource_group.rg.name
  tenant_id                 = data.azurerm_client_config.current.tenant_id
  sku_name                  = "standard"
  enable_rbac_authorization = true # Force RBAC instead of legacy Access Policies
}

# Give yourself Admin rights to create the secrets via Terraform
resource "azurerm_role_assignment" "kv_admin_self" {
  scope                = azurerm_key_vault.kv.id
  role_definition_name = "Key Vault Administrator"
  principal_id         = data.azurerm_client_config.current.object_id
}

# 6. AUTOMATED SECRET INJECTION
# Inject Event Hub Connection String
resource "azurerm_key_vault_secret" "eh_conn" {
  name         = "eh-conn-string"
  value        = azurerm_eventhub_authorization_rule.listen_policy.primary_connection_string
  key_vault_id = azurerm_key_vault.kv.id
  depends_on   = [azurerm_role_assignment.kv_admin_self]
}

# Inject Storage Account Key
resource "azurerm_key_vault_secret" "storage_key" {
  name         = "storage-acct-key"
  value        = azurerm_storage_account.sa.primary_access_key
  key_vault_id = azurerm_key_vault.kv.id
  depends_on   = [azurerm_role_assignment.kv_admin_self]
}

# 7. DATABRICKS WORKSPACE
resource "azurerm_databricks_workspace" "dbw" {
  name                = "dbw-marketstream"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "premium"
}

# Utility for unique naming
resource "random_integer" "suffix" {
  min = 1000
  max = 9999
}

# Outputs for you to easily grab the producer connection string
output "databricks_url" {
  value = azurerm_databricks_workspace.dbw.workspace_url
}
output "producer_connection_string" {
  value     = azurerm_eventhub_authorization_rule.send_policy.primary_connection_string
  sensitive = true
}
