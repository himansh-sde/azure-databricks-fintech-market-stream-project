This is the perfect time to document Phase 1A. By capturing the infrastructure logic, the CLI commands, and the interview talking points now, you are building a study guide for yourself and a professional runbook for your repository.

We will add this to our docs/ folder, just like we did with the Git setup.

1. Create the Documentation File
Make sure you are in the root directory of your project (not the infra folder), then run:

Bash
touch docs/README-Phase1A-Terraform.md
2. The Phase 1A Terraform Runbook
Open docs/README-Phase1A-Terraform.md in your text editor and copy-paste the exact markdown below into it.

Markdown
# Phase 1A: Azure Infrastructure as Code (Terraform)

**Tool Focus:** Terraform (`azurerm`), Azure CLI, Azure Event Hubs, Azure Data Lake Storage (ADLS Gen2), Azure Databricks.
**Objective:** Codify and deploy the physical cloud topology required for high-throughput market data streaming.

---

## 1. The Architectural Topology

This phase provisions the foundational boundaries of our pipeline:

1.  **The Resource Group:** A logical container (`rg-marketstream-dev`) for all project assets.
2.  **The Ingestion Broker:** Azure Event Hubs, acting as our managed Kafka cluster to absorb the market data firehose.
3.  **The Storage Layer:** ADLS Gen2 with Hierarchical Namespace (HNS) enabled. It contains dedicated containers for `bronze` (raw ticks), `silver` (VWAP calculations), and `checkpoints` (Spark state).
4.  **The Compute Plane:** An Azure Databricks workspace equipped with an Access Connector (Managed Identity) for secure, keyless access to the Data Lake.

---

## 2. Infrastructure Setup & Deployment Steps

### Step 1: Install & Authenticate Azure CLI
Before Terraform can communicate with Azure, your local terminal must be authenticated.

1. Install the Azure CLI:
   * **Windows:** Download the [MSI Installer](https://aka.ms/installazurecliwindows)
   * **macOS:** `brew install azure-cli`
2. **Crucial:** If you installed this while your terminal was open, you must restart your terminal so the system recognizes the `az` command.
3. Log into Azure (this opens a browser window):
   ```bash
   az login
Step 2: Write the Terraform Configuration
Navigate to the infra/ directory. Ensure the following files have been created and populated (see repository for exact HCL code):

providers.tf (Azure provider block)

variables.tf (Naming and environment defaults)

main.tf (Resource Group)

storage.tf (ADLS Gen2 and Containers)

eventhub.tf (Namespace, Topic, and Consumer Group)

databricks.tf (Workspace and Access Connector)

outputs.tf (Connection strings and URLs)

Step 3: Deploy the Infrastructure
Run the following commands from within the infra/ directory:

Bash
# 1. Download Azure provider plugins
terraform init

# 2. Preview the resources to be created (Expected: ~9 resources)
terraform plan

# 3. Deploy the resources to Azure (Takes 3-5 minutes)
terraform apply
Step 4: Extract Ingestion Secrets
Once the deployment succeeds, extract the primary connection string for Event Hubs. This will be used in Phase 1B by our Python producer to stream data. We save this to a hidden .env.secret file in the ingestion/ folder (which is protected by our .gitignore).

Bash
terraform output -raw eventhub_primary_connection_string > ../ingestion/.env.secret
3. Interview Preparation: Defending the Architecture
When discussing this portfolio project in a Staff or Senior Data Engineering interview, use these talking points to defend your Terraform design decisions:

Q: Why did you enable Hierarchical Namespace (HNS) on your storage account?

"Standard blob storage is flat. Spark Structured Streaming writes thousands of tiny files to its checkpoint directory to manage state and offsets. Without HNS, directory operations like renaming or listing files cause massive I/O bottlenecks and inflate cloud costs. HNS provides true POSIX-compliant directories, which is critical for Spark and Delta Lake performance."

Q: How does Databricks authenticate to your Data Lake securely?

"I avoid hardcoding Service Principal secrets or storage account keys, as they expire and pose security risks. Instead, I deploy an Azure Databricks Access Connector via Terraform, which creates a System-Assigned Managed Identity in Microsoft Entra ID. I then use Terraform's RBAC (azurerm_role_assignment) to grant that identity 'Storage Blob Data Contributor' access to the Data Lake."

Q: Why did you explicitly define a custom consumer group for Event Hubs?

"If you point a Spark streaming job at the $Default consumer group, and later another team spins up a real-time dashboard pointing to the same hub, the two applications will steal partition offsets from each other, causing silent data loss. I explicitly scope a dedicated consumer group (vwap-spark-cg) to isolate my pipeline's state."


***

### 3. Commit and Push to GitHub

Now that the runbook is saved, let's push this new documentation *and* the Terraform files we wrote earlier up to your GitHub repository. 

Run these commands from the root of your project:

```bash
git add .
git commit -m "feat: add phase 1A terraform code and deployment runbook"
git push