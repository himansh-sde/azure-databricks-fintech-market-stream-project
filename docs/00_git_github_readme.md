# Real-Time FinTech Market Data Streaming Pipeline (Phase 1 Setup)

Welcome to the **FinTech Market Data Streaming** project! 

This repository demonstrates an enterprise-grade, real-time data streaming architecture built on Microsoft Azure. Before we can build the cloud infrastructure (Terraform) or the data pipelines (Databricks/PySpark), we must first set up our local development environment.

This `README.md` serves as a comprehensive, step-by-step beginner's guide to setting up Git, connecting to GitHub, and initializing our project codebase. **No steps are skipped.**

---

## 🛠️ Table of Contents
1. [Prerequisites: Installing Git](#step-1-prerequisites-installing-git)
2. [Configuring Git Identity](#step-2-configuring-your-git-identity)
3. [Creating the GitHub Repository](#step-3-creating-the-remote-github-repository)
4. [Setting up the Local Project](#step-4-setting-up-the-local-project-directory)
5. [Linking Local Git to GitHub](#step-5-linking-your-local-folder-to-github)
6. [Securing the Project (.gitignore)](#step-6-securing-the-project-with-gitignore)
7. [Building the Enterprise Folder Structure](#step-7-building-the-enterprise-folder-structure)
8. [Adding the Terraform Foundation](#step-8-adding-the-terraform-foundation)
9. [Committing and Pushing to GitHub](#step-9-committing-and-pushing-code-to-github)

---

## Step 1: Prerequisites (Installing Git)

Git is the engine that tracks changes to your code. If you do not have Git installed on your computer, you must install it first.

### Windows
1. Download the installer from the [Official Git Website](https://git-scm.com/download/win).
2. Run the `.exe` installer. You can click "Next" through all the default options. 
3. This installs **Git Bash**, a terminal program you will use to type all the commands below.

### macOS
Open your terminal application and type:
```bash
git --version
If it is not installed, your Mac will automatically prompt you to install the "Xcode Command Line Tools". Click Install. (Alternatively, you can install it via Homebrew: brew install git).

Linux (Ubuntu/Debian)
Open your terminal and run:

Bash
sudo apt update
sudo apt install git -y
Step 2: Configuring Your Git Identity
Git needs to know who is writing the code so it can attach your name to every update (called a "commit").

Open your terminal (or Git Bash on Windows) and run these two commands. Replace the text inside the quotes with your actual information:

Bash
git config --global user.name "Your First and Last Name"
git config --global user.email "your.email@example.com"
Note: Use the same email address that you plan to use (or currently use) for your GitHub account.

To verify that it worked, type this command:

Bash
git config --global --list
You should see your name and email printed in the output.

Step 3: Creating the Remote GitHub Repository
GitHub is the website where your code will be stored and backed up safely in the cloud.

Go to GitHub.com and create a free account if you don't have one.

Log in and click the "+" icon in the top right corner, then select New repository.

For the Repository name, type: azure-databricks-fintech-market-stream-project

Set it to Public (or Private, up to you).

CRITICAL STEP: Leave the checkboxes for "Add a README file" and "Add .gitignore" UNCHECKED. We want the repository to be completely empty so we can push our local files to it.

Click Create repository.

Leave that webpage open; you will need the URL in a moment.

Step 4: Setting up the Local Project Directory
Now we need to create the actual folder on your computer where your code will live.

Open your terminal / Git Bash and run the following commands one by one:

Bash
# 1. Navigate to your Documents or Desktop folder (wherever you want the project to live)
cd ~/Documents

# 2. Create the new folder with the exact same name as your GitHub repository
mkdir azure-databricks-fintech-market-stream-project

# 3. Move inside the newly created folder
cd azure-databricks-fintech-market-stream-project

# 4. Turn this standard folder into a Git-tracked folder
git init
By running git init, you have created a hidden folder called .git. Your computer is now actively monitoring this folder for code changes.

Step 5: Linking Your Local Folder to GitHub
Right now, your local folder has no idea that your GitHub account exists. We need to link them together.

Run the following commands in your terminal (Make sure to replace <YOUR_GITHUB_USERNAME> with your actual GitHub username):

Bash
# 1. Tell Git that our primary branch will be called 'main'
git branch -M main

# 2. Connect your local folder to the GitHub repository URL (this is called the "origin")
git remote add origin [https://github.com/](https://github.com/)<YOUR_GITHUB_USERNAME>/azure-databricks-fintech-market-stream-project.git
Step 6: Securing the Project with .gitignore
When writing code for the cloud, you will generate secret passwords, connection strings, and backend files. You must never upload these to GitHub. We prevent this by creating a .gitignore file.

Run this command to create the file:

Bash
touch .gitignore
Open the .gitignore file in a text editor (like VS Code, Notepad, or TextEdit) and paste the following text into it exactly as shown:

Plaintext
# ----------------------------------------------------------------------
# SECRETS & ENVIRONMENT VARIABLES (NEVER UPLOAD)
# ----------------------------------------------------------------------
.env
.env.secret

# ----------------------------------------------------------------------
# TERRAFORM STATE (CRITICAL - DO NOT COMMIT)
# ----------------------------------------------------------------------
.terraform/
*.tfstate
*.tfstate.backup
.terraform.lock.hcl
*.tfvars

# ----------------------------------------------------------------------
# PYTHON / DATABRICKS CACHE
# ----------------------------------------------------------------------
__pycache__/
*.pyc
.databricks/
Save and close the file.

Step 7: Building the Enterprise Folder Structure
Professional engineering projects isolate different parts of the pipeline into separate folders. Let's create our project scaffold:

Bash
mkdir infra
mkdir ingestion
mkdir streaming
mkdir tests
mkdir config
(Note: Git tracks files, not empty folders. These folders will remain invisible to Git until we put files inside them).

Step 8: Adding the Terraform Foundation
Let's put some code into our infra/ folder so Git can start tracking it. This code tells Terraform we want to use Microsoft Azure.

Bash
# 1. Move into the infra folder
cd infra

# 2. Create the two starting configuration files
touch providers.tf variables.tf
Open providers.tf in your text editor and paste this code:

Terraform
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.90"
    }
  }
}

provider "azurerm" {
  features {}
}
Open variables.tf in your text editor and paste this code:

Terraform
variable "project_name" {
  type    = string
  default = "marketstream"
}

variable "environment" {
  type    = string
  default = "dev"
}
Save both files.

Step 9: Committing and Pushing Code to GitHub
We have created our files, but they are only saved locally on your computer. We need to package them up (commit) and send them to the cloud (push).

Run these commands in your terminal:

Bash
# 1. Move back to the root directory of your project
cd ..

# 2. Stage all the files (The period '.' means "everything in this folder")
git add .

# 3. Take a snapshot of the code with a descriptive message
git commit -m "feat: initial project setup, gitignore, and terraform foundation"

# 4. Upload (push) the code to GitHub
git push -u origin main
Authentication Note:
The very first time you run git push, a pop-up window or terminal prompt will ask you to log into GitHub. Follow the prompts to authorize your account via your web browser.

🎉 Congratulations!
Go refresh your page on GitHub.com. You should now see your folders, your .gitignore file, and your Terraform code sitting safely in the cloud. You are officially ready to deploy Azure infrastructure!