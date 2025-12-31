# PROJECT CONTEXT & TECHNOLOGY STACK

**Context:** Build a CMS (Content Management System) inspired by dev.to, viblo, medium,... The goal is to create an environment for developers to write and share knowledge (technical writing), discuss, and store great articles. The system needs to be highly scalable, support fast search.

## 1. Project Overview
- **Name**: DevBlogg
- **Type**: Developer Blogging Platform (CMS).
- **Structure**: Monorepo.

## 2. Tech Stack
- **Backend**: Python + Django + Django REST Framework (DRF).
- **Frontend**: Vue.js + Vite + TailwindCSS.
- **Database**: MySQL.
- **ORM**: Django ORM.
- **Authentication**: JWT + OAuth2 (Google/GitHub) using `django-allauth` + `dj-rest-auth` + `djangorestframework-simplejwt`.
- **Documentation**: Swagger (drf-spectacular).
- **Storage**: Local (Dev) / Cloudinary (Prod).

## 3. Project Structure & Layering
The backend MUST follow these layer dependency rules strictly:

### A. Auth Apps (`devblogg_auth`)
- **Features:** Handle user model (CustomUser), authentication, user-related endpoints (register, login, profile,...).
- 

### B. Core Apps (`devblogg_core`)
- **Features:** Handle main domain, business logic, and routers
- 
---

# CODING CONVENTIONS & BEST PRACTICES

## 1. Backend (Python / Django)

### General
- Use `async/await` for all I/O operations (Database, File, API calls).
- Use `var` when the type is obvious from the right side.
- Follow PascalCase for classes/methods (`GetByIdAsync`) and camelCase for parameters/local variables (`userId`).
- Use Interface Injection via Constructor.

### Controller Guidelines
- Always return `ActionResult<T>`.
- Use `[HttpGet]`, `[HttpPost]`, etc., explicitly.
- Do NOT put business logic in Controllers.
- Always use DTOs for Request bodies and Response types. Never return Domain Entities directly.

### Error Handling
- Use Global Exception Handler Middleware (do not use try-catch in every controller).
- Create custom exceptions in Domain/Application layers (e.g., `NotFoundException`, `ValidationException`).

## 2. Frontend (Vue.js)

### Components
- Use `<script setup>` with Composition API.
- Use TypeScript strictly.
- Component names must be Multi-Word (e.g., `PostCard.vue`, not `Card.vue`).

### API Calls
- Put all API calls in `src/services/xxxService.ts` (e.g., `authService.ts`).
- Do not call `axios` directly inside `.vue` files.
- Use Pinia for state management (Auth, User Profile).

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
# DATABASE SCHEMA (PROPOSED - SIMPLE & EXTENSIBLE)

Goal: keep the schema small (easy to build with EF Core Code First) but flexible enough to grow into a dev.to-like CMS.

## A. Design Principles
- Prefer **GUID PK** (`uniqueidentifier`, `newsequentialid()`) for distributed scalability.
- Use **soft delete** where required (`IsDeleted`, `DeletedAt`, `DeletedById`).
- Add **audit columns** on main tables (`CreatedAt`, `UpdatedAt`).
- Enforce critical business rules with **unique constraints** and **composite PKs** (Likes/Bookmarks/Reports).

## B. Core Enums (stored as `tinyint`)

### `PostStatus`
- `0` Draft
- `1` Pending
- `2` InReview
- `3` Published
- `4` Rejected

### `ModerationAction`
- `0` ClaimPost
- `1` ReleasePost
- `2` ApprovePost
- `3` RejectPost
- `4` BanUser
- `5` UnbanUser

## C. Tables

### 1) `Users`
Holds account + profile basics.

**Columns (suggested)**
- `Id` (PK, `uniqueidentifier`, default `newsequentialid()`)
- `Email` (`nvarchar(256)`, NOT NULL, UNIQUE)
- `UserName` (`nvarchar(50)`, NOT NULL, UNIQUE)
- `DisplayName` (`nvarchar(100)`, NULL)
- `Bio` (`nvarchar(500)`, NOT NULL, default empty string)
- `AvatarUrl` (`nvarchar(1024)`, NULL)
- `PasswordHash` (`nvarchar(512)`, NULL) — nullable to support OAuth-only accounts
- `IsBanned` (`bit`, NOT NULL, default `0`)
- `BannedAt` (`datetime2(3)`, NULL)
- `BannedById` (`uniqueidentifier`, NULL, FK -> `Users.Id`)
- `CreatedAt` (`datetime2(3)`, NOT NULL)
- `UpdatedAt` (`datetime2(3)`, NOT NULL)

**Indexes**
- UNIQUE: (`Email`)
- UNIQUE: (`UserName`)

### 2) `Roles` + `UserRoles`
Keep roles extensible (User/Moderator/Admin now, expandable later).

**`Roles`**
- `Id` (PK, `int identity`)
- `Name` (`nvarchar(32)`, NOT NULL, UNIQUE) — seed: `User`, `Moderator`, `Admin`

**`UserRoles`**
- `UserId` (FK -> `Users.Id`)
- `RoleId` (FK -> `Roles.Id`)
- PK: (`UserId`, `RoleId`)

### 3) `UserAuthProviders`
Supports OAuth2 (Google/GitHub) and silent sign-up.

**Columns**
- `Id` (PK, `uniqueidentifier`, default `newsequentialid()`)
- `UserId` (`uniqueidentifier`, NOT NULL, FK -> `Users.Id`)
- `Provider` (`nvarchar(20)`, NOT NULL) — e.g. `Google`, `GitHub`
- `ProviderUserId` (`nvarchar(128)`, NOT NULL)
- `ProviderEmail` (`nvarchar(256)`, NULL)
- `CreatedAt` (`datetime2(3)`, NOT NULL)

**Constraints / Indexes**
- UNIQUE: (`Provider`, `ProviderUserId`)
- Index: (`UserId`)

### 4) `Posts`
Implements post lifecycle, soft delete, and moderation claim fields.

**Columns**
- `Id` (PK, `uniqueidentifier`, default `newsequentialid()`)
- `AuthorId` (`uniqueidentifier`, NOT NULL, FK -> `Users.Id`)
- `Title` (`nvarchar(200)`, NOT NULL)
- `Slug` (`nvarchar(220)`, NOT NULL, UNIQUE)
- `Summary` (`nvarchar(500)`, NULL)
- `Content` (`nvarchar(max)`, NOT NULL)
- `Status` (`tinyint`, NOT NULL) — see `PostStatus`
- `IsDeleted` (`bit`, NOT NULL, default `0`)
- `DeletedAt` (`datetime2(3)`, NULL)
- `DeletedById` (`uniqueidentifier`, NULL, FK -> `Users.Id`)
- `PublishedAt` (`datetime2(3)`, NULL)
- `AssignedModeratorId` (`uniqueidentifier`, NULL, FK -> `Users.Id`)
- `ClaimedAt` (`datetime2(3)`, NULL)
- `CreatedAt` (`datetime2(3)`, NOT NULL)
- `UpdatedAt` (`datetime2(3)`, NOT NULL)

**Constraints / Indexes**
- UNIQUE: (`Slug`) — supports slug collision handling
- Index: (`AuthorId`, `CreatedAt`)
- Index: (`Status`, `ClaimedAt`) — moderation queue
- Filtered index (recommended): (`Status`, `ClaimedAt`) WHERE `Status` = `2` (InReview)

### 5) `Comments`
Supports nested comments and soft delete behavior.

**Columns**
- `Id` (PK, `uniqueidentifier`, default `newsequentialid()`)
- `PostId` (`uniqueidentifier`, NOT NULL, FK -> `Posts.Id`)
- `AuthorId` (`uniqueidentifier`, NOT NULL, FK -> `Users.Id`)
- `ParentCommentId` (`uniqueidentifier`, NULL, FK -> `Comments.Id`)
- `Content` (`nvarchar(max)`, NOT NULL)
- `IsDeleted` (`bit`, NOT NULL, default `0`)
- `DeletedAt` (`datetime2(3)`, NULL)
- `DeletedById` (`uniqueidentifier`, NULL, FK -> `Users.Id`)
- `CreatedAt` (`datetime2(3)`, NOT NULL)
- `UpdatedAt` (`datetime2(3)`, NOT NULL)

**Indexes**
- Index: (`PostId`, `CreatedAt`)
- Index: (`ParentCommentId`)

### 6) `PostLikes`
One Like per User per Post (toggle by delete/insert).

**Columns**
- `PostId` (`uniqueidentifier`, FK -> `Posts.Id`)
- `UserId` (`uniqueidentifier`, FK -> `Users.Id`)
- `CreatedAt` (`datetime2(3)`, NOT NULL)

**Constraints / Indexes**
- PK (composite): (`PostId`, `UserId`)
- Index: (`UserId`, `CreatedAt`)

### 7) `PostBookmarks`
One Bookmark per User per Post (toggle by delete/insert).

**Columns**
- `PostId` (`uniqueidentifier`, FK -> `Posts.Id`)
- `UserId` (`uniqueidentifier`, FK -> `Users.Id`)
- `CreatedAt` (`datetime2(3)`, NOT NULL)

**Constraints / Indexes**
- PK (composite): (`PostId`, `UserId`)
- Index: (`UserId`, `CreatedAt`)

### 8) `PostReports`
Unique reports per user (threshold > 5 unique reports).

**Columns**
- `PostId` (`uniqueidentifier`, FK -> `Posts.Id`)
- `UserId` (`uniqueidentifier`, FK -> `Users.Id`)
- `Reason` (`nvarchar(500)`, NULL)
- `CreatedAt` (`datetime2(3)`, NOT NULL)

**Constraints / Indexes**
- PK (composite): (`PostId`, `UserId`) — ensures “unique reports”
- Index: (`PostId`, `CreatedAt`) — fast counting for threshold checks

### 9) `ModerationLogs`
Mandatory audit trail for moderation actions (approve/reject/ban/claim).

**Columns**
- `Id` (PK, `bigint identity`)
- `Action` (`tinyint`, NOT NULL) — see `ModerationAction`
- `ActorUserId` (`uniqueidentifier`, NOT NULL, FK -> `Users.Id`) — who performed the action
- `PostId` (`uniqueidentifier`, NULL, FK -> `Posts.Id`) — for post-related actions
- `TargetUserId` (`uniqueidentifier`, NULL, FK -> `Users.Id`) — for user-related actions (ban/unban)
- `Reason` (`nvarchar(1000)`, NULL)
- `MetadataJson` (`nvarchar(max)`, NULL) — optional JSON for future data without schema churn
- `CreatedAt` (`datetime2(3)`, NOT NULL)

**Indexes**
- Index: (`PostId`, `CreatedAt`)
- Index: (`TargetUserId`, `CreatedAt`)
- Index: (`ActorUserId`, `CreatedAt`)

## D. Relationship Summary
- `Users (1) -> (N) Posts` via `Posts.AuthorId`
- `Posts (1) -> (N) Comments` via `Comments.PostId`
- `Comments (1) -> (N) Comments` via `Comments.ParentCommentId`
- `Users (N) <-> (N) Roles` via `UserRoles`
- `Users (1) -> (N) UserAuthProviders`
- `Users (N) <-> (N) Posts` via `PostLikes`, `PostBookmarks`, `PostReports`
- `ModerationLogs` references `Users` (actor/target) and optionally `Posts`

## E. Notes Mapping to Business Rules
- **Email/Username unique**: enforced by unique constraints on `Users`.
- **Soft delete posts**: `Posts.IsDeleted` (never physically delete rows).
- **InReview claiming**: `Posts.Status = InReview` with `AssignedModeratorId` + `ClaimedAt` set atomically by the application.
- **Stale review > 30 minutes**: handled in application (or background job) using `ClaimedAt`.
- **Report threshold > 5**: count rows in `PostReports` per `PostId` (unique per user enforced by composite PK).
- **Moderation transparency**: all actions must write to `ModerationLogs`.

## F. Optional (Add Later, Not Required Now)
- `Tags`, `PostTags` (many-to-many)
- `PostAssets` (for images/files stored locally/Cloudinary)
- Full-Text Index on `Posts(Title, Content)` for fast search at scale