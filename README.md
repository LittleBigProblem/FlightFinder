# FlightFinder
A user based Australian flight finder application because the big company ones all kinda suck

# Setup Instructions
## Amadeus
This project uses Amadeus for the flight API data. To begin;
### Step 1
Access the bellow link to find the instructin for creating an Amadeus account and getting your API key and secret\
[Amdeus Developer Console](https://developers.amadeus.com/self-service/apis-docs/guides/developer-guides/quick-start/#step-2-get-your-api-key)
### Step 2
Once you have the API key and Secret, go to the folder you have the FlightSearcher files inside, and create a .env file
### Step 3
Inside of the .env file, add the following data
```
API_KEY=your_api_key
API_SECRET=your_api_secret
```
and replace your_api_key with your API KEY and your_api_secret with your Secret from the Amadeus Developer website
