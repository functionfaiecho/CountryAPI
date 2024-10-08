# API for CS 250 - Countries, Links, Descriptions.

## About This Project

Part of enhancement three (Databases), this API was created using FAST API and a database provider of my choosing to provide the user with the a city, country name, description and a link. This is in line with the Java project that is expected of students in CS 250 - Software Development Lifecycle. Interested parties may view the [API Documentation](https://countriesapi.crabcakes.dev/docs). **Due to safety concerns, the .env variables are not provided, and this API may not be accessed locally. It must be accessed through the documentation link.** 

## Table of Contents

1. [**How to use the API**](#how-to-use-the-api)
2. Disclaimer


## How To Use The API

The base URL for all API requests is [https://countriesapi.crabcakes.dev](https://countriesapi.crabcakes.dev). The main endpoints you may interact with are as follows:

- **GET** ```/```
    - Root route.
    - Returns a welcome message.

- **GET** ```/destination/search```
    - Search for destinations using parameters like ```destination```, ```country```or ```description```.
    - For example,
    ```bash
    GET /destinations/search?destination=Auckland
    ```

- **GET** ```/destinations```
    - Get all destinations or filter them by destination name or country.
    - Rate limit @ 20 requests per minute.
    - Query parameters:
        - ```country``` (Filter by country)
        - ```destination```(Filter by destination name).

        **Important**: In the case of destination, it is a city name.

## Disclaimer

Please note that this API was created for educational purposes. Any statements in the descriptions do not constitute the opinion of the developer. In the interest of keeping things uniform, if you would like me to add a destination, please raise a GitHub issue. I will endeavour to address these within 3 hours of their receipt.

🦀