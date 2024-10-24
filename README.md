This code is for data collection for my dissertation. 

Part of my dissertation entails mapping out where different types of traditional media cover within Michigan's Upper Peninsula. Since I am looking at the relationship between media source availability and remoteness, this also incorporaes the USDA-ERS Frontier and Remote Areas Codes.

TV is relatively easy to identify at the ZIP code level, as ZIP codes are organized into DMAs. However, this is a little more complicated for radio. The FCC provides contour data for FM radio coverage through shapefiles. Howevver, the nature of AM radio  often makes it more difficult to consistently assess and plot out contour areas. 

However, <a href = "https://www.v-soft.com/on-line-based-software/zipsignal"> V-Soft </a> provides a nice estimation of AM radio coverage at the ZIP code level based on frequency strength. They also provide this for FM stations as well. 

Data collection intended to accomplish two goals: 1) collect the data and 2) identify any additional radio stations that may cover a ZIP that were not previously identified through the construction of my dataset drawing on primary and secondary sources.

To do this, I first ran a search by ZIP code, to identify all stations that were included in that ZIP. Then I ran a search to identify all ZIP code that a station covered, using its call letters. Each of these queries pulled from a CSV file with this information. 

I automated this search and download process using selenium. Results for each search were individually saved as a .txt file, which I later merged in R with my ZIP code data (`UP_zip_query.csv`) which shows all counties covered by that ZIP and the main municipality of that ZIP. I also used this to alongside the USDA-ERS FAR data and plotted it out using ggplot.
