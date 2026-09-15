Let's create a dedicated troubleshooting runbook for the infrastructure phase.

1. Create the File
Run this in your terminal from the root of your project:

Bash
touch docs/README-Phase1A-Troubleshooting.md
2. The Troubleshooting Runbook
Open docs/README-Phase1A-Troubleshooting.md in your code editor and copy-paste this markdown:

Markdown
# Phase 1A: Terraform Execution & Troubleshooting Log

**Objective:** Document the real-world challenges, environmental bugs, and cloud API deprecations encountered during the deployment of the Azure infrastructure, along with their exact resolutions.

---

## Challenge 1: Command Line Tools Not Found in Git Bash

### The Error
When attempting to authenticate to Azure (`az login`) or initialize Terraform (`terraform init`), the Git Bash terminal returned:
> `bash: az: command not found`
> `bash: terraform: command not found`

### The Cause
The executable files were not in the system's `PATH` variables, or they were installed while the terminal was already open. Git Bash only reads `PATH` variables at launch, meaning it cannot "see" programs installed after it was opened.

### The Resolution
1. **Azure CLI:** Installed via the official Microsoft MSI installer.
2. **Terraform:** Installed natively via the Windows Package Manager:
   ```bash
   winget install Hashicorp.Terraform
Critical Fix: Completely closed the Git Bash window and opened a new instance to force a refresh of the environment variables.

Challenge 2: Terraform Plan Hanging / Stuck
The Error
Running terraform plan caused the terminal to freeze indefinitely without generating the resource plan or throwing a timeout error.

The Cause
This is a known visual rendering bug within Git Bash (MinTTY) on Windows when interacting with Terraform's dynamic progress bars and Azure's interactive API tokens.

The Resolution
Pressed Ctrl + C to force-kill the hung process.

Pressed Enter a few times to clear visual caching glitches.

Verified the Azure authentication token was actively passing by running az account show.

(Fallback option documented): If Git Bash continues to freeze, executing terraform plan in native Windows PowerShell bypasses the MinTTY rendering bug.

Challenge 3: Databricks "Standard" SKU Deprecated
The Error
During terraform apply, the deployment failed mid-way with a 400 Bad Request from the Azure API:

DatabricksStandardSkuNotSupported: The Standard SKU is deprecated. Please use Premium SKU.

The Cause
Microsoft and Databricks recently deprecated the creation of new "Standard" tier workspaces in Azure. The Terraform HCL configuration explicitly requested sku = "standard".

The Resolution & Architectural Concept (Statefulness)
Updated databricks.tf to request the supported tier:

Terraform
resource "azurerm_databricks_workspace" "workspace" {
  # ...
  sku = "premium" 
}
The Power of Terraform State: Re-ran terraform apply. Because Terraform is stateful, it did not duplicate or destroy the Storage Accounts and Event Hubs that had already succeeded. It read the state file (terraform.tfstate), recognized the remaining gap, and flawlessly deployed only the missing Databricks workspace and Access Connector.


***

### 3. Save, Commit, and Extract Secrets!

Let's push this new log to GitHub. Run these commands from the root of your project:

```bash
git add docs/
git commit -m "docs: add phase 1A troubleshooting and execution log"
git push
Now, before we move to Phase 1B (Python), we must extract the connection string for Event Hubs so our Python code knows where to send the data. Run this in your infra folder:

Bash
cd infra
terraform output -raw eventhub_primary_connection_string > ../ingestion/.env.secret
(You won't see any output, but this safely writes your secret directly into a hidden file that Git is instructed to ignore!)