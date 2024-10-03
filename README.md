# FlightSearch

**FlightSearch** is an automated tool designed to find the cheapest flight tickets available and share them with a broad audience on social media. By leveraging multiple APIs, it identifies and promotes flights with exceptionally low prices, helping users take advantage of hidden airline deals.

## Features

- **Advanced Search Algorithm**: Utilizes the [Travelpayouts Aviasales API](https://support.travelpayouts.com/hc/en-us/articles/203956163-Aviasales-Data-API) to fetch special flight offers and find abnormally low-priced tickets.
- **Twitter Integration**: Automatically posts deals on Twitter using the [Twitter API](https://developer.x.com/en/docs/x-api), complete with an affiliate link, relevant hashtags, and a stock photo for maximum reach.
- **Automated Workflow**: Includes downloading a relevant image from [Unsplash](https://unsplash.com/developers) to match the destination, ensuring visually appealing posts.

## Objective

The main goal of **FlightSearch** is to help users discover the best flight deals, many of which are under-promoted or difficult to find. Airlines frequently offer sales that go unnoticed by the general public, and this tool aims to bridge that gap by highlighting these offers through social media.

## Workflow

1. **Retrieve Data**: Fetch flight deal data from the Travelpayouts API.
2. **Filter Results**: Apply an algorithm to identify the best and lowest-priced tickets.
3. **Generate Affiliate Links**: Create a unique affiliate link to earn commissions on bookings.
4. **Download Stock Photo**: Automatically download a relevant stock photo from Unsplash that corresponds to the destination.
5. **Post on Twitter**: Share the deal on Twitter, complete with hashtags, affiliate link, and stock image to maximize engagement.

## Set-up Instructions

To set up and run **FlightSearch**, you’ll need API access for the following services:

1. **Twitter API**: [Sign up here](https://developer.x.com/en/docs/x-api) to obtain API credentials.
2. **Travelpayouts/Aviasales API**: [Get your API key here](https://support.travelpayouts.com/hc/en-us/articles/203956163-Aviasales-Data-API).
3. **Unsplash API**: [Sign up here](https://unsplash.com/developers) for access to high-quality stock images.

Ensure all API credentials are set up and configured correctly within the tool before running.