# Atlas

Atlas is a discord bot to help you manage your discord server. 

Atlas is licensed under the **CC BY-NC-SA** License.

## Licensing
Atlas is licensed under the Attribution-NonCommercial-ShareAlike (CC BY-NC-SA) license. This license allows for the copy, distribution, and creation of adaptations of the material for non-commercial purposes, as long as proper attribution is given to the original creator and any adaptations are licensed under the same terms.

The CC BY-NC-SA license requires the following elements:
* BY: Credit must be given to the original creator
* NC: The material can only be used for non-commercial purposes
* SA: Adaptations must be licensed under the same terms

## Installation
1. Clone the repository
2. Install the required packages using `pip install -r requirements.txt`
3. Modify the values in `.TEMPLATE.env` and rename it to `.env`
4. Run the bot using `python main.py`

Atlas requires all environment variables to be set, and for the Core API to be online.

### Hosting Information
We host Atlas using docker, which is why there is a Github Action to deploy, but support will not be provided for this.

## Contributing
If you would like to contribute to the project, please fork the repository and submit a pull request, detailing the changes you have made.

## Workflows  
### Deployment to a Docker Container  
Automates the process of building and deploying the application to a Docker container.  

### CodeQL Analysis  
Performs security and quality analysis on the codebase to detect vulnerabilities and improve code quality.  

## Modifications  
All workflows can be safely deleted if needed. Removing them will not affect the core functionality of the code itself.  

[![CodeFactor](https://www.codefactor.io/repository/github/markination/atlas/badge)](https://www.codefactor.io/repository/github/markination/atlas)