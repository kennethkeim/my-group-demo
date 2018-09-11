import datetime
from app import months
from dbModels import Events, db
from sqlalchemy import or_

def importEventsToYear(year):
    # find all the birthdays and anniversaries
    events = Events.query.filter(or_(Events.type == 'birthday', Events.type == 'anniversary')).all()

    eventsCount = len(events)
    changedEventsCount = 0

    # iterate through each event
    for oldEvent in events:
        month_num = oldEvent.month_num
        day_num = oldEvent.date.day

        # construct the date
        try:
            date = datetime.date(year, month_num, day_num)
        except (ValueError, TypeError):
            return "This date isn't valid."

        # construct the 'readable_date'
        weeks = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        wkday = weeks[date.weekday()]
        month_name = months[month_num]
        readable_date = f"{wkday}, {month_name} {day_num}"

        # set everything to stay same except date and readable_date
        # commit changes
        if db.session.query(db.exists().where(Events.id == oldEvent.id)).scalar(): # this is stock SQLAlchemy
            newEvent = Events.query.get(oldEvent.id)
            newEvent.date = date
            newEvent.readable_date = readable_date
            newEvent.title = newEvent.title
            newEvent.time = newEvent.time
            newEvent.location = newEvent.location
            newEvent.notes = newEvent.notes
            newEvent.type = newEvent.type
            newEvent.month_num = newEvent.month_num
            db.session.commit()
            changedEventsCount += 1


    return f"Found {eventsCount} Events. Changed {changedEventsCount}."
