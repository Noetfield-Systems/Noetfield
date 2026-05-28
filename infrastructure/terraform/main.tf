terraform {
  required_version = ">= 1.7.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Production infrastructure should be added as small, reviewed modules.
# The preferred strategic cloud is Azure because Noetfield's wedge product is
# Microsoft Copilot Governance and enterprise identity starts with Entra ID.
