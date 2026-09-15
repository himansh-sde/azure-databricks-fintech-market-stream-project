# infra/outputs.tf

output "storage_account_name" {
  value = azurerm_storage_account.adls.name
}

output "eventhub_primary_connection_string" {
  value     = azurerm_eventhub_authorization_rule.producer_policy.primary_connection_string
  sensitive = true
}

output "eventhub_name" {
  value = azurerm_eventhub.market_trades.name
}

output "databricks_workspace_url" {
  value = azurerm_databricks_workspace.workspace.workspace_url
}
