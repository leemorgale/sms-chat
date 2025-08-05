 


Coding Challenge: Group SMS Chat

This exercise has you create a group chat app over SMS. Back before everyone had multiple app-based messengers on their phone, plain SMS was the only way to have conversations, and managing group chats was a pain: adding a new member or removing an existing one meant starting a whole new thread in your SMS app, and you’d better hope nobody messages the old thread!  

The app GroupMe was an early solution here, bridging the gap between SMS and app-based messengers: you could browse and join chat rooms from an online interface, but messages could be sent and received entirely via text.   You’ll be implementing an MVP of that system: users should be able to sign up, join a room, and then send and receive SMS texts with the rest of the room.


For your solution, the most important things we’ll be evaluating are:
Getting basic functionality up and running quickly
Being able to configure+work with common third-party services (in this case, Twilio)
Making sensible technical design decisions - how data is stored, how code is laid out and how readable and testable it is, etc.

Of secondary importance (you will get some credit for these but they are a lot less important than the things above)
Performance/scalability. As part of your debrief, we’ll definitely talk about what we might want to redo from your MVP code to fully bring it into production, including for scalability concerns, but It’s totally OK if the actual code you turn in is only good for relatively small numbers of users.
Extra Features. The most important thing is to do a good job on the required features listed below, and the time limit is meant to encourage you to focus on them.  If you have extra time, you can feel free to add whatever features you want.
Of no importance at all:
Visual design / UX of the website portion


Required Features

From an API (REST / GraphQL / your choice):

Users can create an account, which includes a phone number and a name.
Users can search for group chats created on the service
Users can create a new group chat, and give it a name
Users can join an existing group
Users can leave a group.

From SMS:
Upon joining a group on the website, users should receive an SMS welcoming them to the chat, and telling them they can reply to send a message
Users should be able to text this number to send a message to the chat
If anyone else in a user's chat room sends a message, they should receive an SMS with that message and the name of the user that sent it.
Users should be able to be part of more than one chat room at a time. (you can set a limit of allowed rooms that you think makes sense, it doesn’t have to be ~infinity, but it should be more than a couple of rooms)

Connecting to Twilio
Instead of actually having to create a twilio account you can rough in what it would look like based on their API documentation. It doesn’t need to actually run but still build as though the service needs to be connected, secured, and use their python sdk
Deliverables and Deploying the site
You can run the site on your local box, no need to deploy it anywhere unless you’d rather do that..


Please do upload your code to either github or gitlab and send me a link when you’re done.  We will also set up a short debrief call where we can talk through your code and/or do a demo.
Feel free to ask questions!
This is a solo project but the role we’re interviewing you for is very collaborative - you are more than welcome to reach out via email if you have any clarifying questions about this prompt or just want to sanity check any part of your solution before implementing it.

Time limit
You can take up to 5 hours. Let me know when you’ve read through this and are starting.  The point of the deadline isn’t to be super strict but we don’t want to take up a ton of your time. The intent of the deadline is instead to be helpful to you -  to remove the pressure to spend a ton of extra time building bonus features, which we know some people would do if we let people take as much time as they wanted, putting candidates that didn’t have that long to spend at a disadvantage.