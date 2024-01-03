# Task Management API Project

## Overview
Create an API for a task management system that allows users to manage their tasks. The API should support creating, updating, deleting, and retrieving tasks.

## Features

1. **Task CRUD Operations:**
   - Create a new task with details such as title, description, due date, priority, etc.
   - Retrieve a list of tasks.
   - Retrieve details of a specific task by ID.
   - Update task details.
   - Delete a task.

2. **Task Categories:**
   - Allow tasks to be categorized into different categories (e.g., Personal, Work, Shopping).
   - Retrieve tasks based on categories.

3. **User Authentication:**
   - Implement user authentication to secure the API.
   - Users should be able to register, log in, and log out.

4. **Task Status:**
   - Track the status of tasks (e.g., To-Do, In Progress, Completed).
   - Update the status of a task.

5. **Due Date Reminders:**
   - Allow users to set due dates for tasks.
   - Implement a feature to send reminders to users for approaching or overdue tasks.

6. **Collaboration:**
   - Allow users to share tasks with other users.
   - Collaborators should be able to view and update shared tasks.

7. **Statistics and Insights:**
   - Provide statistics on completed tasks, overdue tasks, etc.
   - Generate insights on task completion trends over time.

8. **Search and Filters:**
   - Implement search functionality to find tasks by title or description.
   - Allow users to filter tasks based on different criteria (e.g., priority, due date).

9. **API Documentation:**
   - Create clear and comprehensive API documentation using tools like Swagger or OpenAPI.

10. **Rate Limiting and Security:**
    - Implement rate limiting to prevent abuse.
    - Ensure the API is secure, using HTTPS and handling authentication securely.

## Tech Stack
- **Backend Framework:** Flask (Python) or Express (Node.js)
- **Database:** MongoDB or PostgreSQL
- **Authentication:** JWT (JSON Web Tokens)
- **Documentation:** Swagger or OpenAPI

## Potential Extensions
- Mobile app or web front-end that consumes this API.
- Integration with third-party services such as email for task reminders.
- Export/Import tasks in standard formats like JSON or CSV.

This project provides a good balance of CRUD operations, user authentication, and additional features to enhance the overall user experience. It can be extended based on your interests and the complexity you want to add to the project.


## Next

- Adding employees to a taskgroup should only be allowed to authorized 
task managers or admin.
- limit the pool of employees the task manager can chose from by the category
of the task.
- make related category field a many to many relationship so a position
can have multi disciplinary qualifications.
- Add functionality of task group sought after positions field
- IMPORTANT: check why fields are displayed for unatuhenticated users in task
view get method.

- write ttests for taskgroup
make sure to test for both scenarios , authenticated owner and non
authenticated owner etc.