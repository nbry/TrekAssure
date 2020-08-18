# TrekAssure
*"One search for peace of mind for your day of hiking and the journey back home"*

**1.What goal will your website be designed to achieve?**  

Hiking is an incredibly fun activity and is a great way to get some exercise while finding some of the most beautiful places in the world. However some hiking destinations can lead you to the middle of nowhere, and often times hikers will find themeselves in unfamilar places without cell reception. As a hiker, I definitely came across these situations. Before I set out, I seek information only about the trail itself, but I often lack the foresight to think about the journey back home. Occasionally, I'll end up around aimlessly until I can get reception and find my bearings.    

The goal of TrekAssure is to allow a user to search for their trail and get a virtual pack/pamphlet of information. This pamphlet will include various maps and written directions from the trail to back home, and to the nearest hospital(s), pharmacy, grocery store, etc. The pamphlet will be interactive as long as the user has internet conenction. Most importantly, users will be able to press an export button that will allow the user to save the information or email themselves a zipped file containing all relevant information. Once saved, the user can access this information offline.   

**2.What kind of users will visit your site? In other words, what is the demographic of your users?**  

My site can benefit anyone interested in the outdoors and hiking. I'm hoping that TrekAssure can help promote interest in hiking and other outdoor activities. 

**3.What data do you plan on using? You may have not picked your actual API yet,which is fine, just outline what kind of data you would like it to contain.**  

Trail data from [Hiking Project API](https://www.hikingproject.com/data)  
Geocoding, routing, and mapping from [Mapquest API](https://developer.mapquest.com/)  

**4.In brief, outline your approach to creating your project (knowing that you may notknow everything in advance and that these details might change later).** 

**a.What does your database schema look like?**  

TBD

**b.What kinds of issues might you run into with your API?**  

Although it's not the goal of my app, I would like to have a map of the trail on the info pack... but I'm not sure that can be achieved. Current Hiking apps must use coordinates and some clever logic to map out trails. 

**c.Is there any sensitive information you need to secure?**  

User data (username/password)

**d.What functionality will your app include?** 

Ease of use, easy to read, links for directions, pagination for destinations, exportable/emailable zipped files. 

**e.What will the user flow look like?**  

I want it to be as simple as possible. This is designed to be a one or two step process to help hikers be more prepared.   
>1. Search for a trail  
>2. View info  
>3. Press a button to export "info pack"  

**f.What features make your site more than CRUD? Do you have any stretchgoals?**  

My app combines data from two APIs, and I'm hoping it'll allow for some clever formatting for a pamphlet. I want users to be able to keep track of trails they've been to on their profile, so other users can "like" or "favorite" them and create their own custom emergency pamphlets. 
