# PROJECT CONTEXT & TECHNOLOGY STACK

**Context:** Build a CMS (Content Management System) inspired by dev.to, viblo, medium,... The goal is to create an environment for developers to write and share knowledge (technical writing), discuss, and store great articles. The system needs to be highly scalable, support fast search.

## 1. Project Overview
- **Name**: DevBlogg
- **Type**: Developer Blogging Platform (CMS).
- **Structure**: Monorepo.

## 2. Tech Stack
- **Backend**: Python + Django + Django REST Framework (DRF).
- **Frontend**: Next.js + TailwindCSS.
- **Database**: MySQL.
- **ORM**: Django ORM.
- **Authentication**: JWT + OAuth2 (Google/GitHub) 
  - `django-allauth` 
  - `dj-rest-auth` 
  - `djangorestframework-simplejwt`
- **API Docs**: Swagger (drf-spectacular).
- **Storage**: Local (Dev) / Cloudinary (Prod).

## 3. Project Structure
The backend MUST follow these rules strictly:

### A. Auth Apps (`devblogg_auth`)

Responsible for:
  - CustomUser model
  - Authentication / Authorization
  - User registration, login, profile
  - JWT, OAuth2

### B. Core Apps (`devblogg_core`)

Responsible for:
  - Business logic (Posts, Comments, Likes, Bookmarks, Reports)
  - Domain rules
  - Feature APIs

### C. Composition Root (`devblogg_common`)

Responsible for:
  - Reusable utilities, helpers, mixins, base classes
  - Global exception handling
  - Custom permissions, pagination

## 4. Architecture
The backend follows a Service-Oriented Architecture tailored for Django. This ensures adherence to SOLID principles, specifically decoupling business logic from the HTTP layer (Views) and the Database layer (Models).

### A. Services
- **Role:** The "Brain" of the application. Contains all pure business logic.

- **Responsibilities:**
  - Handle complex operations (e.g., ClaimPost, PublishPost, CalculateStats).
  - Orchestrate transactions (Atomic operations involving multiple models).
  - Call external APIs (Email, Cloudinary, AI).
- **Rule:** Services do NOT know about request or response objects. They take clean data (arguments/DTOs) and return results or raise domain exceptions.

- **SOLID Application:** SRP: Each service function does one specific business task.

### B. Serializers
- **Role:** The "Gatekeeper" and "Translator".

- **Responsibilities:**
  - Input Validation: Ensure data sent by users matches the expected format (types, lengths, required fields).
  - Data Transformation: Convert complex querysets/model instances into JSON (Serialization) and JSON into Python objects (Deserialization).
  - Representation: Define what data is exposed to the API clients (hiding sensitive fields like password_hash).
- **Rule:** Do NOT put complex business logic (like sending emails) inside serializers.save(). Keep serializers focused on data structure.

### C. Views
- **Role:** The "Controller" / Interface Layer.

**Responsibilities:**
  - Handle HTTP: Receive requests, parse parameters, and determine the correct response status codes (200, 201, 400, etc.).

  - Permissions & Auth: Check if the user is logged in (IsAuthenticated) or has the right role (IsAdminUser).

  - Orchestration: Call the appropriate Service to execute the logic.

  - Response: Return the result from the Service using the Serializer to format the output.
- **Rule:** Views should be "Thin". If you see more than 10 lines of logic in a View method, move it to a Service.

### D. Models
- **Role:** The "Skeleton". Represents database tables.

- **Responsibilities:**
  - Define database schema (Columns, Types).
  - Define relationships (ForeignKey, ManyToMany).
  - Ensure Data Integrity (Unique constraints, Database-level validation).
  - Fat Model (Limited): Only include logic strictly related to the data instance itself (e.g., full_name property, __str__ method).

- **Rule:** Avoid heavy logic here. Models should focus on data structure, not business processes.

---

# CORE BUSINESS LOGIC & RULES

## 1. IDENTITY & USERS MODULE

### A. Registration Rules
- **Uniqueness**: Email and Username must be unique across the system.
- **Default Role**: New accounts are assigned the `User` role by default.
- **Profile Initialization**: 
  - If `AvatarUrl` is not provided, generate a default avatar based on the User's initials (using UI Dicebear or similar service logic).
  - If `Bio` is not provided, set it to an empty string.

### B. Authentication Rules
- **Access Control**: 
  - *Guests* (Unauthenticated) can only: View Published Posts, View Comments, Search.
  - *Authenticated Users* can: Write Posts, Comment, Like, Bookmark, Report.
- **OAuth Handling**: 
  - If a user logs in via Google/GitHub and the email does not exist, the system performs **Auto-Registration** (Silent Sign-up).


## 2. CONTENT MODULE (POSTS)

### A. Post Lifecycle (State Machine)
A Post must have one of the following statuses (`PostStatus` enum):
1. **Draft**: Private. Visible only to the Author. content is saved but not submitted.
2. **Pending**: Submitted for review. Waiting for Moderator action.
3. **InReview**: Currently being reviewed by an assigned Moderator. Visible in the shared moderation queue but marked as claimed by a reviewer.
4. **Published**: Visible to everyone.
5. **Rejected**: Violated community guidelines. Visible only to Author and Moderators.

### B. Creation & Publishing Workflow
1. **Slug Generation**: 
   - Rule: Slug is generated from Title (lower-case, remove accents, replace spaces with hyphens).
   - Collision Handling: If `slug` exists, append a random string (e.g., `hoc-lap-trinh-csharp-a1b2`).
2. **Moderator Review**:
   - Upon submission from `Draft` to `Pending`, the moderator will review the post manually.
   - If the post triggers the community standards (spam, inappropriate content, advertising content, ...), moderators can `Reject` it with a reason.
   - If approved, the post status changes to `Published`.
### C. Editing Rules
- **Ownership**: Only the `Author` can edit their posts.
- **Re-evaluation**: 
  - If a **Published** post is edited, it remains **Published** (unless the edit triggers a banned keyword filter - optional).
  - If a **Rejected** post is edited, it transitions back to **Pending** for re-review.

### D. Deletion Rules
- **Soft Delete**: Posts are never physically deleted from the database. Set `IsDeleted = true`.
- **Authority**: Users can delete their own posts. Moderators can delete any post.


## 3. INTERACTION MODULE

### A. Likes & Bookmarks
- **One-Time Action**: A user can only Like a post once. Toggling (Clicking again) removes the Like.
- **Self-Interaction**: Users CAN like their own posts (to boost initial visibility).

### B. Comments
- **Hierarchy**: Support nested comments (Reply to reply).
- **Modification**: 
  - Users can delete their own comments.
  - If a parent comment is deleted, child comments (replies) are visually hidden or marked as "Parent deleted" but remain in DB.


## 4. MODERATION MODULE (ROLES & RESPONSIBILITIES)

### A. User Reporting Logic
- Any Authenticated User can `Report` a post.
- **Threshold Rule**: If a Post receives > 5 unique Reports, it is temporarily moved to **Pending** status automatically until a Moderator reviews it again.

### B. Moderator Workflow
- **The Queue**: Moderators see a dashboard of posts with status `Pending` or flagged via Reports.
- **Decision Actions**:
  - **Approve**: Sets status to `Published`.
  - **Reject**: Sets status to `Rejected` AND requires a `Reason` (text). The system sends a notification to the Author.

### C. Administrator Authority
- **User Management**: Admin can `Ban` a user.
- **Banned Effect**: A Banned User:
  - Cannot login.
  - Their existing posts remain visible (unless individually deleted).

## 5. AUTHORITY & BYPASS RULES

### A. Auto-Publish Privilege
- **Rule**: Posts created by users with `Role = Moderator` or `Role = Admin` will bypass the Moderator Queue.
- **Initial Status**: Their posts are set to `Published` immediately upon clicking "Publish".

### B. Self-Moderation Restrictions
- **Rule**: A Moderator cannot "Approve" their own reported posts. 
- **Scenario**: If a Moderator's post receives > 5 reports and moves to `Pending`, another Moderator or an Admin must be the one to review and re-approve it.

### C. Transparency
- **Rule**: Every moderation action (Approve/Reject/Ban) must be logged in a `ModerationLogs` table, including who performed the action on whose post.

## 6. MODERATION QUEUE LOGIC

### A. Shared Queue System
- **Visibility**: All Moderators and Admins see the same list of `Pending` posts.

- **Claiming / InReview**: When a moderator starts reviewing a `Pending` post, the system should atomically mark the post as `InReview` and set an `AssignedModeratorId` and `ClaimedAt` so other moderators see it as claimed.

### B. MODERATION WITH IN-REVIEW STATUS

- **Status Transition**: 
  - `Pending` -> `InReview` (When a moderator starts reading).
  - `InReview` -> `Published/Rejected` (Final decision).
  - `InReview` -> `Pending` (If moderator cancels or session expires).
- **Ownership**: Only the moderator who set the post to `InReview` can `Approve/Reject` it.
- **Stale Review Handling**: If a post stays in `InReview` for more than 30 minutes without action, it becomes available for other moderators to "Claim" again.

---

# API ENDPOINT
## 1. Authentication Module

| Method | Endpoint                     | Description                          |
|--------|------------------------------|--------------------------------------|
| POST   | /api/auth/register/          | Register a new user                  |
| POST   | /api/auth/login/             | User login (returns JWT token)       |
| POST   | /api/auth/token/refresh/     | Get a new Access Token when expired  |
| POST   | /api/auth/logout/            | Logout (Blacklist token)             |
| GET    | /api/auth/user/              | Get current User info (me)           |
| PATCH  | /api/auth/user/              | Update Profile (Bio, Avatar, DisplayName) |
| POST   | /api/auth/google/            | Google OAuth2 Login (Frontend sends code/token) |
| POST   | /api/auth/github/            | GitHub OAuth2 Login                  |

## 2. Content Module: Posts

| Method | Endpoint                     | Description                          | 
|--------|------------------------------|--------------------------------------|
| GET    | /api/posts/                  | Feed homepage. Filter by status=PUBLISHED. |
| GET    | /api/posts/{slug}/           | View post details. |
| POST   | /api/posts/                  | Create a new post. Default status is DRAFT. Input: Title, Content, Tags, Summary. |
| PATCH  | /api/posts/{id}/             | Edit a post. Only the author can edit it. If the post is Published -> keep it Published. If Rejected -> move back to Pending. |
| DELETE | /api/posts/{id}/             | Delete a post (Soft Delete). set is_deleted=True. |
| POST   | /api/posts/{id}/publish/     | Submit for review. Change status from DRAFT -> PENDING. (If user is Mod/Admin -> PUBLISHED always). |
| GET    | /api/posts/me/drafts/        | View drafts. Get list of DRAFT posts of the current user. |

## 3. Interaction Module

| Method | Endpoint                     | Description                          |
|--------|------------------------------|--------------------------------------|
| POST	 | /api/posts/{id}/like/	      | Toggle Like. If already like -> unlike (delete record), else create like record. |
| POST	 | /api/posts/{id}/bookmark/  	| Toggle Bookmark. Save post to bookmark list. |
| GET	   | /api/bookmarks/	            | Get user bookmark list. |
| POST	 | /api/posts/{id}/comments/  	| Write a comment on a post. |
| POST	 | /api/comments/{id}/reply/	  | Reply to a comment. Input: content, parent_id. |
| DELETE | /api/comments/{id}/	        | Delete a comment. Only the author can delete it. Soft delete. |
| POST	 | /api/posts/{id}/report/	    | Report a post. Input: reason. Logic: If > 5 unique reports -> Auto move to PENDING. |

## 4. Moderation Module

| Method | Endpoint                     | Description                          |
|--------|------------------------------|--------------------------------------|
| GET	   | /api/moderation/queue/	      | Get queue list of posts with status=PENDING or status=IN_REVIEW (of the current moderator). Sorted by time.
| POST	 | /api/moderation/posts/{id}/claim/ | Claim a post for review. Change status from PENDING -> IN_REVIEW. Set AssignedModeratorId and ClaimedAt. |
| POST	 | /api/moderation/posts/{id}/approve/ | Approve a post. Change status from IN_REVIEW -> PUBLISHED. Only the assigned moderator can approve. |
| POST	 | /api/moderation/posts/{id}/reject/  | Reject a post. Change status from IN_REVIEW -> REJECTED. Input: reason. Only the assigned moderator can reject. |
| POST	 | /api/moderation/users/{id}/ban/     | Ban a user. Admin only. Banned users cannot login. |