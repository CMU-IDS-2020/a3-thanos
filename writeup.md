# Explore Worldwide CO2 Emissions

![A screenshot of your application. Could be a GIF.](screenshot.png)

TODO: Short abstract describing the main goals and how you achieved them.
Describe the question that you are enabling a user to answer. The question should be compelling and the solution should be focused on helping users achieve their goals. 
## Project Goals
The goal of our project is to enable the users to explore the worldwide trend of carbon dioxide emissions from 1990 to 2011 and identify sources of CO2 emission and possible factors that may cause some countries to have specific trends. By comparing different countries' total CO2 emissions and emissions per capita, the users are expected to identify the countries that contribute the most to CO2 emissions.
Moreover, by breaking down each country's CO2 emission sources and providing correlations between relevant indicators, the users may discover possible reasons behind certain trends. 


## Design

TODO: **A rationale for your design decisions.** How did you choose your particular visual encodings and interaction techniques? What alternatives did you consider and how did you arrive at your ultimate choices?

Since the first part of our project is to provide a global view of the total CO2 emissions, we chose to use a world map with both color and size encodings and a year slide bar. This could give the users a clear overview of the worldwide CO2 total emissions and emissions per capita overtime. Moreover, by adding bar charts connected to the world map, the users can select multiple countries from the map that they're especially interested and compare their CO2 emissions throughout the two decades.

The second part is to guide the users to explore certain countries' sources of CO2 emissions overtime. Therefore, we designed a scatter plot with color and size encodings to show each country's CO2 emissions overtime. The users can select as many countries as they're interested from the multiple selection bar and the countries would be added to the plot automatically. A bar chart showing the percentage of each CO2 emissions sources is connected to the scatter plot. By enabling interval selection on years on the scatter plot, the users can see the change of each country's CO2 emissions sources overtime. 
## Development

TODO: **An overview of your development process.** Describe how the work was split among the team members. Include a commentary on the development process, including answers to the following questions: Roughly how much time did you spend developing your application (in people-hours)? What aspects took the most time?
