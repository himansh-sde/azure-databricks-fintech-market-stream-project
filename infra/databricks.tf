# infra/databricks.tf

resource "azurerm_databricks_workspace" "workspace" {
  name                = "dbw-${var.project_name}-${var.environment}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "premium"
}

# Creates a Managed Identity for Databricks to access ADLS securely
resource "azurerm_databricks_access_connector" "unity_connector" {
  name                = "db-access-connector-${var.project_name}-${var.environment}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  identity {
    type = "SystemAssigned"
  }
}

# Assign the identity read/write access to the storage account
resource "azurerm_role_assignment" "databricks_storage_access" {
  scope                = azurerm_storage_account.adls.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_databricks_access_connector.unity_connector.identity[0].principal_id
}
