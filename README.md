# scraping-ZoomURL-from-Outlook-by-Django

    This is a web application that extracts and lists Zoom invitation emails in Outlook within a set period of time. 
Users can delete or add event names, meeting schedules, and comments to each email invitation. The updated mails are displayed by schedule and can be clicked to join the meeting. The email list can also be sorted by filling out letters in top-right search form.
![Index Screen](images_for_README/index.png)

This is the screen for determining the collection period. Users can start scraping by clicking the green button.
The top 'Try with Sample Data Set' is a data set for quickly experience the app. By clicking it, a pre-prepared data set will be entered into the database.
![Scrape Screen](images_for_README/scrape.png)

This is the screen for checking and updating the details of mails which users chose in Index Page. Users can add an event name, a meeting schedule and comments and update it.
![Update Screen](images_for_README/update.png)


# How to develop this app

    This application is developed by django framework using 1 app (named scraping_tool, reffered to another repository) and basic skills. So, if you are a beginner in django, this app may help you understand the overview of django.

# Skills we use

- scraping (https://pypi.org/project/pywin32/)
    We use pywin32, a Python extension for Microsoft Windows, which provides access to much of the Win32 API, the ability to create and use COM objects, and the Pythonwin environment.
    
- ajax
    We use it to delete HTML elements by clicking an icon without screen transition.
    
- django-bootstrap-datepicker-plus (https://pypi.org/project/django-bootstrap-datepicker-plus/)
    This is a very comvinient widget which has Date-Picker, Time-Picker, DateTime-Picker, Month-Picker and Year-Picker, and we can easily select options by date-range-pickers.

- django-widget-tweaks (https://pypi.org/project/django-widget-tweaks/)
    This enables us to add parameters in css-like way, such as class, id, name, etc.










