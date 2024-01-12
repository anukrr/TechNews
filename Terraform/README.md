Terraform:\
This Folder includes necessary files to recreate AWS architecture + configurations made using terraform. \
main.tf: This script replicates AWS architecture using terraform.04c381bd \
Use: \
    1. Add Environment variables to a terraform.tfvariables file
    2. To initialise terraform: \
    ```terraform init```
    3. To compare your configuration to your resource's state, review changes before you apply them, or to refresh your workspace's state:\
    ```terraform plan``````
    4. To build terraform build.

note: Possibly some resources might not build as ECRs constructed in terraform will not have images pushed to them.
