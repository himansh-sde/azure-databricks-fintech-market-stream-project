# infra/eventhub.tf

resource "azurerm_eventhub_namespace" "eh_ns" {
  name                = "eh-${var.project_name}-${var.environment}-${random_string.suffix.result}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Standard"
  capacity            = 1 
}

# The topic where trades are published
resource "azurerm_eventhub" "market_trades" {
  name                = "market-trades"
  namespace_name      = azurerm_eventhub_namespace.eh_ns.name
  resource_group_name = azurerm_resource_group.rg.name
  partition_count     = 2
  message_retention   = 1 # Keep messages for 1 day
}

# Dedicated consumer group for Spark
resource "azurerm_eventhub_consumer_group" "spark_vwap_cg" {
  name                = "vwap-spark-cg"
  namespace_name      = azurerm_eventhub_namespace.eh_ns.name
  eventhub_name       = azurerm_eventhub.market_trades.name
  resource_group_name = azurerm_resource_group.rg.name
}

# Access policy so our Python script can push data in Phase 1B
resource "azurerm_eventhub_authorization_rule" "producer_policy" {
  name                = "producer-send-policy"
  namespace_name      = azurerm_eventhub_namespace.eh_ns.name
  eventhub_name       = azurerm_eventhub.market_trades.name
  resource_group_name = azurerm_resource_group.rg.name
  listen              = false
  send                = true
  manage              = false
}
